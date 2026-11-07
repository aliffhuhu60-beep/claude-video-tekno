"""Render video akhir daripada timeline.json + overlays.json + subs.ass.

Langkah: clips -> fasa (concat) -> grafik (mov alfa) -> audio (numpy) -> pas akhir (xfade + grafik + sari kata)
Guna: python3 render.py [clips|overlays|audio|final|all] VERSION
"""
import json, os, sys, subprocess, math, wave
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import gfx

W = "/home/user/work/"
RAW = "/home/user/raw/"
OUT = "/home/user/claude-video-tekno/output/"
FPS = 30
SR = 48000
SRC = {"A": RAW + "pdp.mp4", "S": RAW + "sokongan.mp4", "G": RAW + "gameplay.mp4"}
TL = json.load(open(W + "timeline.json")); SH = TL["shots"]
OV = json.load(open(W + "overlays.json"))
CL = W + "clips/"; os.makedirs(CL, exist_ok=True)
OVD = W + "ovl/"; os.makedirs(OVD, exist_ok=True)
VER = sys.argv[2] if len(sys.argv) > 2 else "v1"

def F(t):
    return int(round(t * FPS))

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-3000:]); raise SystemExit(1)
    return r

# ------------------------------------------------------------------ 1. klip
GRADE = "eq=contrast=1.05:saturation=1.05,colorbalance=rm=0.02:bm=-0.02:rs=0.015:bs=-0.015,vignette=angle=0.32"
def clip(i, x):
    path = f"{CL}{i:03d}.mp4"
    n = F(x["out_end"]) - F(x["out_start"])
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return path
    vf = []
    if x["src"] == "G":
        vf += ["crop=1440:810:0:0", "scale=1920:1080:flags=lanczos", "fps=30"]
    else:
        if x["crop"]:
            a, b, w, h = x["crop"]
            vf += [f"crop={w}:{h}:{a}:{b}"]
            vf += ["scale=1920:1080:flags=lanczos"]
            if 1280 / w > 1.3:
                vf += ["unsharp=5:5:0.45:5:5:0.0"]
        else:
            vf += ["scale=1920:1080:flags=lanczos"]
        vf += [GRADE, "fps=30"]
    vf += ["setsar=1", "format=yuv420p"]
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{x['tin']:.3f}", "-i", SRC[x["src"]], "-an", "-vf", ",".join(vf),
         "-frames:v", str(n), "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-g", "30", "-r", "30",
         "-video_track_timescale", "15360", path])
    # pastikan bilangan bingkai tepat (pad bingkai terakhir jika sumber pendek)
    got = int(run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries",
                   "stream=nb_read_packets", "-of", "csv=p=0", path]).stdout.strip())
    if got < n:
        tmp = path + ".pad.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vf", f"tpad=stop_mode=clone:stop={n - got}",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-g", "30", "-video_track_timescale", "15360", tmp])
        os.replace(tmp, path)
    return path

def do_clips():
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(3) as ex:
        list(ex.map(lambda a: clip(*a), enumerate(SH)))
    # fasa
    phases = []
    for i, x in enumerate(SH):
        if not phases or phases[-1][0] != x["phase"]:
            phases.append([x["phase"], []])
        phases[-1][1].append(f"{CL}{i:03d}.mp4")
    for k, (ph, files) in enumerate(phases):
        lst = f"{W}phase_{k}.txt"
        open(lst, "w").write("".join(f"file '{f}'\n" for f in files))
        run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", f"{W}phase_{k}.mp4"])
    print("klip & fasa siap", len(phases))

# ------------------------------------------------------------------ 2. grafik beranimasi
from render_plan import build, _tup  # noqa

def ease(u):
    u = min(max(u, 0.0), 1.0); return 1 - (1 - u) ** 3

def do_overlays():
    for j, o in enumerate(OV):
        path = f"{OVD}{j:02d}.mov"
        n = F(o["dur"])
        spec = o["spec"]
        full = build(o["kind"], spec)
        slide = 120 if o["kind"] == "popup" else 36
        cw, ch = full.size[0] + slide, full.size[1]
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{cw}x{ch}",
                              "-r", "30", "-i", "-", "-c:v", "qtrle", "-pix_fmt", "argb", path], stdin=subprocess.PIPE)
        cache = {}
        for f in range(n):
            t = f / FPS
            kind = o["kind"]
            key = None
            if kind == "steps":
                nsteps = len(spec) - 1
                nv = min(nsteps, 1 + int(t / 1.5))
                key = ("s", nv)
                blk = cache.get(key) or build(kind, spec, full=False, n=nv)
            elif kind == "key":
                nv = min(len(spec[1]), 1 + int(t / 1.5)); key = ("k", nv)
                blk = cache.get(key) or build(kind, spec, full=False, n=nv)
            elif kind == "ayat":
                sa = spec.get("second_at")
                nv = len(spec["items"]) if (sa is None or t >= sa) else 1; key = ("a", nv)
                blk = cache.get(key) or build(kind, spec, full=False, n=nv)
            elif kind == "popup":
                sh = (t - 0.6) / 0.8
                if 0 < sh < 1:
                    blk = build(kind, spec, shine=sh)
                else:
                    key = ("p",); blk = cache.get(key) or build(kind, spec)
            else:
                key = ("f",); blk = cache.get(key) or full
            if key is not None:
                cache[key] = blk
            fin = 0.6 if kind == "popup" else 0.45
            a_in = ease(t / fin)
            a_out = 1 - ease((t - (o["dur"] - 0.7)) / 0.7) if t > o["dur"] - 0.7 else 1.0
            a = a_in * a_out
            canvas = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
            off = int(slide * (1 - a_in))
            b = blk
            if a < 1:
                b = blk.copy(); b.putalpha(blk.getchannel("A").point(lambda v, a=a: int(v * a)))
            canvas.alpha_composite(b, (slide - off, 0))
            p.stdin.write(canvas.tobytes())
        p.stdin.close(); p.wait()
        o["file"], o["cx"] = path, o["x"] - slide
    json.dump(OV, open(W + "overlays_r.json", "w"), indent=1)
    print("grafik siap", len(OV))

# ------------------------------------------------------------------ 3. audio
def read_wav(p):
    w = wave.open(p); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return a.reshape(-1, w.getnchannels())

def write_wav(p, a):
    with wave.open(p, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())

def do_audio():
    from intro_outro import music
    voice = W + "pdp_voice.wav"
    if not os.path.exists(voice):
        run(["ffmpeg", "-v", "error", "-y", "-i", SRC["A"], "-vn", "-ac", "2", "-ar", str(SR), "-af",
             "highpass=f=100,afftdn=nf=-28:tn=1,equalizer=f=3000:t=q:w=1.2:g=4.5,"
             "acompressor=threshold=-22dB:ratio=3:attack=8:release=180:makeup=3,alimiter=limit=0.95", voice])
    V = read_wav(voice)
    total = TL["total"]
    out = np.zeros((int(round(total * SR)) + SR, 2), np.float32)
    def place(sig, t0, fin=0.012, fout=0.012):
        s0 = int(round(t0 * SR)); sig = sig.copy(); n = len(sig)
        a, b = int(fin * SR), int(fout * SR)
        if a: sig[:a] *= np.linspace(0, 1, a)[:, None]
        if b: sig[-b:] *= np.linspace(1, 0, b)[:, None]
        out[s0:s0 + n] += sig[:len(out) - s0]
    # suara guru: gabung shot berturut-turut dengan julat pdp bersambung
    runs = []
    for x in SH:
        if x["audio"] != "A": continue
        p0, p1 = x["pdp"]
        if runs and abs(runs[-1]["p1"] - p0) < 0.02 and abs(runs[-1]["o1"] - x["out_start"]) < 0.02:
            runs[-1]["p1"] = p1; runs[-1]["o1"] = x["out_end"]
        else:
            runs.append(dict(p0=p0, p1=p1, o0=x["out_start"], o1=x["out_end"], xf=x.get("xfade_in", False)))
    for r in runs:
        seg = V[int(r["p0"] * SR):int(r["p0"] * SR) + int(round((r["o1"] - r["o0"]) * SR))]
        place(seg, r["o0"], 0.3 if r["xf"] else 0.04, 0.3)
    # muzik montaj
    mr = []
    for x in SH:
        if x["audio"] != "M": continue
        if mr and abs(mr[-1][1] - x["out_start"]) < 0.02:
            mr[-1][1] = x["out_end"]
        else:
            mr.append([x["out_start"], x["out_end"]])
    for k, (a, b) in enumerate(mr):
        p = W + f"mus_{k}"
        music(b - a + 0.6, p, seed=20 + k)
        m = read_wav(p + ".wav") * 10 ** (-7 / 20)
        place(m[:int((b - a) * SR)], a, 0.6, 0.8)
    # sfx halus
    subs = []
    for line in open(W + "subs.ass"):
        if line.startswith("Dialogue"):
            f = line.split(",", 9)
            subs.append([sum(float(p) * m for p, m in zip(v.split(":"), (3600, 60, 1))) for v in f[1:3]])
    def quiet(t):
        return not any(a - 0.4 < t < b + 0.4 for a, b in subs)
    rs = np.random.default_rng(3)
    def whoosh(d=0.55):
        n = int(d * SR); t = np.arange(n) / SR
        nz = rs.standard_normal(n)
        sig = np.zeros(n); y = 0
        for i in range(n):   # penapis lulus-rendah berubah (sapuan)
            al = 0.02 + 0.25 * (i / n) ** 1.5
            y += al * (nz[i] - y); sig[i] = y
        env = np.sin(np.pi * t / d) ** 2
        s = sig * env; s /= np.abs(s).max() + 1e-9
        return np.stack([s * 0.10, s * 0.10], 1).astype(np.float32)
    def chime():
        n = int(1.2 * SR); t = np.arange(n) / SR
        s = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * 4) * g for f, g in ((1318.5, 0.6), (1975.5, 0.3), (2637, 0.15)))
        s /= np.abs(s).max()
        return np.stack([s * 0.08, s * 0.08], 1).astype(np.float32)
    for o in OV:
        if o["kind"] == "phase" and quiet(o["t0"]):
            place(whoosh(), max(0, o["t0"] - 0.2), 0, 0)
        if o["kind"] == "popup" and quiet(o["t0"] + 0.4):
            place(chime(), o["t0"] + 0.3, 0, 0)
    # intro / outro
    for f, t0 in (("intro_v1.mp4", 0.0), ("outro_v1.mp4", TL["body_end"])):
        tmp = W + f + ".wav"
        run(["ffmpeg", "-v", "error", "-y", "-i", OUT + f, "-vn", "-ac", "2", "-ar", str(SR), tmp])
        place(read_wav(tmp), t0, 0.01, 0.05)
    out = out[:int(round(total * SR))]
    write_wav(W + "mix_raw.wav", out)
    # loudnorm 2 laluan: -14 LUFS, TP -1
    r = run(["ffmpeg", "-hide_banner", "-i", W + "mix_raw.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
             "-f", "null", "-"])
    js = r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1]
    m = json.loads(js)
    af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    run(["ffmpeg", "-v", "error", "-y", "-i", W + "mix_raw.wav", "-af", af + ",alimiter=limit=0.89:level=false",
         "-ar", str(SR), W + "mix.wav"])
    print("audio siap")

# ------------------------------------------------------------------ 4. pas akhir
def do_final():
    ovr = json.load(open(W + "overlays_r.json"))
    nph = len([f for f in os.listdir(W) if f.startswith("phase_") and f.endswith(".mp4")])
    # offset xfade (dalam masa badan)
    starts = []
    for x in SH:
        if x.get("xfade_in"):
            starts.append((F(x["out_start"]) - F(TL["intro"])) / FPS)
    inputs = ["-i", OUT + "intro_v1.mp4"]
    for k in range(nph):
        inputs += ["-i", f"{W}phase_{k}.mp4"]
    inputs += ["-i", OUT + "outro_v1.mp4"]
    for o in ovr:
        inputs += ["-i", o["file"]]
    fc = []
    prev = "1:v"
    for k in range(1, nph):
        fc.append(f"[{prev}][{k + 1}:v]xfade=transition=fade:duration={0.3}:offset={starts[k - 1]:.4f}[x{k}]")
        prev = f"x{k}"
    fc.append(f"[0:v]fps=30,format=yuv420p,setsar=1[i0]")
    fc.append(f"[{nph + 1}:v]fps=30,format=yuv420p,setsar=1[o0]")
    fc.append(f"[i0][{prev}][o0]concat=n=3:v=1:a=0[base]")
    cur = "base"
    base_idx = nph + 2
    for j, o in enumerate(ovr):
        t0 = o["t0"]
        fc.append(f"[{base_idx + j}:v]setpts=PTS-STARTPTS+{t0:.3f}/TB[ov{j}]")
        fc.append(f"[{cur}][ov{j}]overlay=x={o['cx']}:y={o['y']}:eof_action=pass:enable='between(t,{t0:.3f},{t0 + o['dur']:.3f})'[c{j}]")
        cur = f"c{j}"
    fc.append(f"[{cur}]subtitles={W}subs.ass:fontsdir=/usr/share/fonts/opentype/inter,format=yuv420p[v]")
    final = f"{OUT}SIMULASI_PENGAJARAN_MIKRO_{VER}.mp4"
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-i", W + "mix.wav", "-filter_complex", ";".join(fc),
         "-map", "[v]", "-map", f"{base_idx + len(ovr)}:a", "-t", f"{TL['total']:.3f}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-maxrate", "7.5M", "-bufsize", "15M",
         "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", "30", "-g", "60",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", final])
    prev720 = f"{OUT}SIMULASI_PENGAJARAN_MIKRO_{VER}_preview720p.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", final, "-vf", "scale=1280:720:flags=lanczos", "-c:v", "libx264",
         "-preset", "fast", "-crf", "24", "-maxrate", "3M", "-bufsize", "6M", "-c:a", "aac", "-b:a", "128k",
         "-movflags", "+faststart", prev720])
    print("siap", final)

if __name__ == "__main__":
    step = sys.argv[1]
    if step in ("clips", "all"): do_clips()
    if step in ("overlays", "all"): do_overlays()
    if step in ("audio", "all"): do_audio()
    if step in ("final", "all"): do_final()
