"""Bingkai pratonton keluaran (rakaman + grafik + sari kata) pada masa t, dan storyboard v2 HTML.

Guna: python3 preview_frames.py check   -> lembaran semakan grafik
      python3 preview_frames.py board   -> storyboard_v2.html
"""
import json, os, sys, io, subprocess, base64, html, re
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import gfx
from render_plan import build  # noqa  (memuatkan pelan semasa)

W = "/home/user/work/"
RAW = "/home/user/raw/"
TL = json.load(open(W + "timeline.json")); SH = TL["shots"]
OV = json.load(open(W + "overlays.json"))
SRC = {"A": RAW + "pdp.mp4", "S": RAW + "sokongan.mp4", "G": RAW + "gameplay.mp4"}

def grab(src, t):
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", SRC[src], "-frames:v", "1", "-f", "image2pipe",
                        "-vcodec", "png", "-"], capture_output=True, check=True)
    return Image.open(io.BytesIO(p.stdout)).convert("RGB")

def shot_at(t):
    for x in SH:
        if x["out_start"] <= t < x["out_end"]:
            return x

def base_frame(t):
    x = shot_at(t)
    st = x["tin"] + (t - x["out_start"])
    im = grab(x["src"], st)
    if x["src"] == "G":
        im = im.crop((0, 0, 1440, 810))
    elif x["crop"]:
        a, b, w, h = x["crop"]; im = im.crop((a, b, a + w, b + h))
    return im.resize((1920, 1080), Image.LANCZOS).convert("RGBA"), x

def subs_at(t):
    for line in open(W + "subs.ass"):
        if line.startswith("Dialogue"):
            f = line.split(",", 9)
            a, b = [sum(float(p) * m for p, m in zip(v.split(":"), (3600, 60, 1))) for v in f[1:3]]
            if a <= t < b:
                return f[9].strip()

def sub_img(txt):
    lines = []
    for ln in txt.split("\\N"):
        parts, col, bold = [], gfx.WHITE, False
        for tok in re.split(r"(\{[^}]*\})", ln):
            if tok.startswith("{"):
                if "37AFD4" in tok: col, bold = gfx.GOLD, True
                elif "62B06E" in tok: col, bold = gfx.SOFT, True
                else: col, bold = gfx.WHITE, False
            elif tok:
                parts.append((tok, col, bold))
        lines.append(parts)
    return gfx.subtitle(lines)

def frame(t):
    im, x = base_frame(t)
    for o in OV:
        if o["t0"] <= t < o["t0"] + o["dur"]:
            blk = build(o["kind"], o["spec"])
            im.alpha_composite(blk, (o["x"], o["y"]))
    s = subs_at(t)
    if s:
        im.alpha_composite(sub_img(s))
    return im.convert("RGB"), x

def mmss(t):
    return f"{int(t // 60):02d}:{t % 60:04.1f}"

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "check":
        ims = []
        for o in OV:
            fr, _ = frame(o["t0"] + min(o["dur"] - 1, 3.0))
            ims.append(fr.resize((640, 360)))
        g = Image.new("RGB", (640 * 4, 360 * ((len(ims) + 3) // 4)))
        for i, m in enumerate(ims):
            g.paste(m, ((i % 4) * 640, (i // 4) * 360))
        g.save(W + "check_overlays.jpg", quality=82)
    else:
        rows = []
        for i, x in enumerate(SH):
            t = x["out_start"] + min(2.0, x["dur"] / 2)
            fr, _ = frame(t)
            b = io.BytesIO(); fr.resize((384, 216), Image.LANCZOS).save(b, "JPEG", quality=72)
            rows.append((i, x, base64.b64encode(b.getvalue()).decode()))
        css = open(os.path.join(os.path.dirname(__file__), "board.css")).read()
        h = [f"<!doctype html><html lang=ms><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
             f"<title>Storyboard v2</title><style>{css}</style></head><body><header><div class=w><h1>Storyboard v2 — <span>30:00</span></h1>"
             f"<p>Simulasi Pengajaran Mikro · Mohamad Aliff bin Ahmad Shahabuddin · {len(SH)} shot + intro 8 s + outro 40 s</p></div></header><main>"]
        h.append(open(os.path.join(os.path.dirname(__file__), "board_notes.html")).read())
        cur = None
        h.append("<h2>INTRO 00:00–00:08</h2><p class=meta>Grafik tajuk + nama (tanpa klip PdP).</p>")
        lab = {"A": "Kamera utama", "S": "Video sokongan", "G": "Gameplay"}
        kd = {"guru": "Guru (MCU/MS)", "guru-wide": "Guru (sederhana luas)", "wide": "Wide kelas", "reaksi": "Reaksi murid (selari)",
              "broll": "B-roll gameplay", "montaj": "Montaj aktiviti"}
        for i, x, b in rows:
            if x["phase"] != cur:
                cur = x["phase"]; h.append(f"<h2>{html.escape(cur)}</h2><div class=grid>")
            au = "Suara guru" if x["audio"] == "A" else "Muzik · suara disenyap"
            h.append(f"<figure><img src='data:image/jpeg;base64,{b}' alt=''><figcaption><b>{mmss(x['out_start'])}</b> +{x['dur']:.1f}s · "
                     f"{kd[x['kind']]}<br><span>{lab[x['src']]} {mmss(x['tin'])} · {au}</span></figcaption></figure>")
            nxt = SH[i + 1]["phase"] if i + 1 < len(SH) else None
            if nxt != cur:
                h.append("</div>")
        h.append("<h2>OUTRO 29:20–30:00</h2><p class=meta>Penghargaan: Puan Julina binti Tarikat → Keluarga BMONETHO → nama guru → fade hitam.</p>")
        h.append("</main></body></html>")
        open(sys.argv[2], "w").write("\n".join(h))
