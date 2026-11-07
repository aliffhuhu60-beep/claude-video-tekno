"""Hasilkan klip INTRO dan OUTRO (penghargaan) — grafik + muzik asli, tanpa rakaman PdP.

Guna:  python3 tools/intro_outro.py OUT_DIR
Keluaran: intro_v1.mp4, outro_v1.mp4  (1920x1080, 30 fps, H.264, AAC 48 kHz stereo)
"""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
import gfx
from gfx import W, H, FOREST, GOLD, SOFT, WHITE, SEMI, BOLD, XB, DSEMI

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
FPS = 30
SR = 48000

# ---------------------------------------------------------------- maklumat (daripada RPH)
NAMA = "MOHAMAD ALIFF BIN AHMAD SHAHABUDDIN"
OPSYEN = "Opsyen Bahasa Melayu"
INSTITUSI = "Institut Pendidikan Guru Kampus Tun Hussein Onn"
KURSUS = "EDUP3133 · Teknologi untuk Pengajaran dan Pembelajaran"
PENSYARAH = "PUAN JULINA BINTI TARIKAT"
KELUARGA = "KELUARGA BMONETHO"


# ---------------------------------------------------------------- latar
def make_bg():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((x - W * 0.35) / W) ** 2 + ((y - H * 0.45) / H) ** 2)
    k = np.clip(1.0 - d * 0.9, 0.55, 1.0)[..., None]
    base = np.array([16, 72, 54], np.float32) * k + np.array([6, 30, 22], np.float32) * (1 - k)
    return base


BG = make_bg()
rng = np.random.default_rng(7)
PARTS = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(1.5, 4.0), rng.uniform(4, 14), rng.uniform(0.15, 0.45))
         for _ in range(46)]


def background(t):
    im = Image.fromarray(BG.astype(np.uint8)).convert("RGBA")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for (px, py, r, sp, a) in PARTS:  # zarah emas terapung perlahan
        yy = (py - sp * t) % H
        xx = px + 10 * math.sin(t * 0.4 + px)
        d.ellipse((xx - r, yy - r, xx + r, yy + r), fill=GOLD + (int(255 * a),))
    lay = lay.filter(ImageFilter.GaussianBlur(1.2))
    # garis emas nipis menyapu perlahan di bawah
    d2 = ImageDraw.Draw(lay)
    gx = (t * 120) % (W + 600) - 300
    d2.rectangle((gx, H - 120, gx + 300, H - 118), fill=GOLD + (90,))
    return Image.alpha_composite(im, lay)


# ---------------------------------------------------------------- blok teks
def block(lines, align="left", width=None):
    """lines: [(teks, fon, warna, jarak_bawah)] -> RGBA rapat."""
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    ws = [tmp.textlength(s, font=f) for s, f, c, g in lines]
    bw = int(width or max(ws)) + 8
    bh = int(sum(f.size * 1.25 + g for s, f, c, g in lines)) + 8
    im = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y = 0
    for (s, f, c, g), w in zip(lines, ws):
        x = 0 if align == "left" else (bw - w) / 2
        d.text((x, y), s, font=f, fill=c)
        y += f.size * 1.25 + g
    return im


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return 1 - (1 - u) ** 3


class El:
    def __init__(self, img, x, y, t_in, t_out, dx=-60, dy=0, fin=0.6, fout=0.7):
        self.img, self.x, self.y, self.t_in, self.t_out = img, x, y, t_in, t_out
        self.dx, self.dy, self.fin, self.fout = dx, dy, fin, fout

    def draw(self, canvas, t):
        if t < self.t_in or t > self.t_out:
            return
        a_in = ease((t - self.t_in) / self.fin)
        a_out = 1 - ease((t - (self.t_out - self.fout)) / self.fout) if t > self.t_out - self.fout else 1
        a = a_in * a_out
        if a <= 0:
            return
        ox = self.dx * (1 - a_in)
        oy = self.dy * (1 - a_in)
        im = self.img
        if a < 1:
            im = im.copy()
            im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
        canvas.alpha_composite(im, (int(self.x + ox), int(self.y + oy)))


class Bar(El):
    """Jalur emas menegak yang 'tumbuh'."""
    def __init__(self, x, y, h, t_in, t_out):
        super().__init__(None, x, y, t_in, t_out)
        self.h = h

    def draw(self, canvas, t):
        if t < self.t_in or t > self.t_out:
            return
        g = ease((t - self.t_in) / 0.8)
        fo = 1 - ease((t - (self.t_out - 0.7)) / 0.7) if t > self.t_out - 0.7 else 1
        d = ImageDraw.Draw(canvas)
        d.rectangle((self.x, self.y, self.x + 8, self.y + self.h * g), fill=GOLD + (int(255 * fo),))


def render(elements, dur, path_noext, fade_black_end=0.0, fade_in=0.5):
    n = int(round(dur * FPS))
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", path_noext + ".wav", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-ac", "2",
           "-movflags", "+faststart", "-shortest", path_noext + ".mp4"]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        t = i / FPS
        c = background(t)
        for e in elements:
            e.draw(c, t)
        rgb = c.convert("RGB")
        k = 1.0
        if t < fade_in:
            k = t / fade_in
        if fade_black_end and t > dur - fade_black_end:
            k = max(0.0, (dur - t) / fade_black_end)
        if k < 1:
            rgb = Image.eval(rgb, lambda v: int(v * k))
        p.stdin.write(rgb.tobytes())
    p.stdin.close()
    p.wait()


# ---------------------------------------------------------------- muzik asli (disintesis)
def note(f):
    return 440.0 * 2 ** ((f - 69) / 12)


def music(dur, path, seed=1):
    t = np.arange(int(dur * SR)) / SR
    out = np.zeros((len(t), 2))
    chords = [[48, 55, 60, 64, 71], [45, 52, 57, 60, 67], [41, 48, 57, 60, 64], [43, 50, 55, 59, 62]]
    seg = 4.0
    rs = np.random.default_rng(seed)
    for ci in range(int(math.ceil(dur / seg))):
        ch = chords[ci % 4]
        s0 = ci * seg
        idx = (t >= s0) & (t < s0 + seg + 1.5)
        tt = t[idx] - s0
        env = np.minimum(tt / 1.2, 1) * np.exp(-np.maximum(tt - seg, 0) * 2.5)
        for j, m in enumerate(ch):
            f = note(m)
            sig = (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * 2 * f * tt + 0.3)) * env * 0.05
            pan = 0.35 + 0.3 * (j / 4)
            out[idx, 0] += sig * (1 - pan)
            out[idx, 1] += sig * pan
        # arpeggio loceng lembut
        for k in range(8):
            ts = s0 + k * 0.5
            m = ch[(k * 2 + ci) % 5] + 12
            bi = (t >= ts) & (t < ts + 1.6)
            tb = t[bi] - ts
            b = np.sin(2 * np.pi * note(m) * tb) * np.exp(-tb * 3.2) * 0.035 * (0.6 + 0.4 * rs.random())
            out[bi, 0] += b * (0.3 + 0.4 * (k % 2))
            out[bi, 1] += b * (0.7 - 0.4 * (k % 2))
    # bass lembut
    for ci in range(int(math.ceil(dur / seg))):
        m = chords[ci % 4][0] - 12
        idx = (t >= ci * seg) & (t < ci * seg + seg)
        tt = t[idx] - ci * seg
        out[idx] += (np.sin(2 * np.pi * note(m) * tt) * np.minimum(tt / 0.3, 1) * np.exp(-tt * 0.4) * 0.07)[:, None]
    fi, fo = min(1.0, dur / 4), min(2.5, dur / 3)
    g = np.minimum(t / fi, 1) * np.minimum((dur - t) / fo, 1)
    out *= np.clip(g, 0, 1)[:, None]
    raw = path + "_raw.wav"
    import wave
    with wave.open(raw, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
    # kenyaringan sasaran -14 LUFS, true peak <= -1 dBTP
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.5:LRA=7", "-ar", str(SR),
                    path + ".wav"], check=True)
    os.remove(raw)


# ---------------------------------------------------------------- INTRO (8 s)
def intro():
    dur = 8.0
    x = 210
    els = [
        Bar(160, 300, 470, 0.2, dur),
        El(block([(INSTITUSI.upper(), BOLD(26), SOFT, 4), (KURSUS, SEMI(26), (200, 225, 210), 0)]), x, 300, 0.3, dur),
        El(block([("SIMULASI PENGAJARAN MIKRO", XB(88), WHITE, 0)]), x, 410, 0.8, dur),
        El(block([("(MICRO TEACHING)", DSEMI(44), GOLD, 0)]), x, 525, 1.2, dur),
        El(block([("Bahasa Melayu Tahun 5 · SP 5.3.3 Ayat Aktif dan Ayat Pasif", SEMI(30), (220, 232, 225), 0)]),
           x, 600, 1.6, dur),
        El(block([("DISEDIAKAN OLEH", BOLD(22), GOLD, 6), (NAMA, XB(46), WHITE, 6), (OPSYEN, SEMI(28), SOFT, 0)]),
           x, 680, 2.4, dur),
    ]
    p = os.path.join(OUT, "intro_v1")
    music(dur, p, seed=3)
    render(els, dur, p, fade_black_end=0.0, fade_in=0.4)


# ---------------------------------------------------------------- OUTRO (40 s)
def outro():
    dur = 40.0
    cx = lambda im: (W - im.width) // 2

    def centred(lines, t0, t1, y=None):
        im = block(lines, align="center")
        return El(im, cx(im), (H - im.height) // 2 if y is None else y, t0, t1, dx=0, dy=40, fin=0.8, fout=0.8)

    els = [
        centred([("SETINGGI-TINGGI PENGHARGAAN", BOLD(30), GOLD, 26),
                 ("kepada pensyarah yang dihormati", SEMI(30), (210, 228, 218), 22),
                 (PENSYARAH, XB(70), WHITE, 18),
                 ("Pensyarah " + KURSUS, SEMI(28), SOFT, 6),
                 (INSTITUSI, SEMI(28), SOFT, 0)], 0.5, 12.5),
        centred([("TERIMA KASIH", BOLD(30), GOLD, 26),
                 ("atas sokongan, kerjasama dan semangat", SEMI(30), (210, 228, 218), 22),
                 (KELUARGA, XB(84), WHITE, 0)], 13.0, 24.5),
        centred([("DISEDIAKAN OLEH", BOLD(30), GOLD, 26),
                 (NAMA, XB(62), WHITE, 18),
                 (OPSYEN, SEMI(30), SOFT, 6),
                 (INSTITUSI, SEMI(28), (210, 228, 218), 0)], 25.0, 34.5),
        centred([("SIMULASI PENGAJARAN MIKRO", XB(56), WHITE, 10),
                 ("(MICRO TEACHING)", DSEMI(36), GOLD, 0)], 35.0, 40.0),
    ]
    p = os.path.join(OUT, "outro_v1")
    music(dur, p, seed=11)
    render(els, dur, p, fade_black_end=2.5, fade_in=0.8)


if __name__ == "__main__":
    which = sys.argv[2:] or ["intro", "outro"]
    if "intro" in which:
        intro()
    if "outro" in which:
        outro()
