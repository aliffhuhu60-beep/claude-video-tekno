"""Jana storyboard HTML (dengan bingkai sebenar + mockup grafik) daripada shotlist.py.

Guna:  python3 tools/storyboard.py RAW_DIR OUT_DIR
"""
import os, sys, subprocess, html, base64, io
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import gfx
from shotlist import SHOTS

RAW, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
SRC = {"A": os.path.join(RAW, "pdp.mp4"), "G": os.path.join(RAW, "gameplay.mp4")}

NAME = "[NAMA PENUH GURU]"
ROLE = "[JAWATAN]"


def grab(src, t):
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", SRC[src], "-frames:v", "1",
                        "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, check=True)
    return Image.open(io.BytesIO(p.stdout)).convert("RGB")


def framed(s, t):
    im = grab(s["src"], t)
    if s["src"] == "G":
        im = im.crop((0, 0, 1440, 810))
    elif s["frame"][0] == "crop":
        _, cx, cy, z = s["frame"]
        w, h = 1280 / z, 720 / z
        x0 = min(max(cx - w / 2, 0), 1280 - w)
        y0 = min(max(cy - h / 2, 0), 720 - h)
        im = im.crop((int(x0), int(y0), int(x0 + w), int(y0 + h)))
    return im.resize((1920, 1080), Image.LANCZOS)


def mmss(x):
    return f"{int(x // 60):02d}:{x % 60:04.1f}"


def overlay(base, g, phase):
    out = base.convert("RGBA")
    for part in g.split("||"):
        kind, _, rest = part.partition(":")
        f = rest.split("|")
        if kind == "PHASE":
            out = Image.alpha_composite(out, gfx.phase_card(f[0], f[1]))
        elif kind == "STEPS":
            out = Image.alpha_composite(out, gfx.steps_panel(f[0], f[1:]))
        elif kind == "POPUP":
            out = Image.alpha_composite(out, gfx.teacher_popup(NAME, ROLE, "Minit 01:16 · Fasa: SET INDUKSI", 0.5))
        elif kind in ("AYAT", "AYATTL"):
            def parts(s):
                return [(w + " ", "v" if (w.startswith(("men", "mem", "meng", "di")) and len(w) > 5 and w not in ("dikehendaki",)) else "n",
                         gfx.GOLD if w.startswith("me") else (gfx.SOFT if w.startswith("di") else gfx.WHITE)) for w in s.split()]
            items = [("AYAT AKTIF", gfx.GOLD, parts(f[0]))]
            if len(f) > 1:
                items.append(("AYAT PASIF", gfx.SOFT, parts(f[1])))
            pos = (60, 60) if kind == "AYATTL" or phase == "SET INDUKSI" else (1060, 90)
            out = Image.alpha_composite(out, gfx.sentence_panel(items, pos=pos, width=800))
    return out.convert("RGB")


rows, t = [], 0.0
for s in SHOTS:
    dur = s.get("dur") or (s["tout"] - s["tin"])
    start = t
    t += dur
    if s["src"] == "X":
        if s["gfx"] == "TITLE":
            im = gfx.title_card(["BAHASA MELAYU · TAHUN 5", "Tema: Teknologi dan Inovasi"],
                                ["SIMULASI PENGAJARAN", "MIKRO"], "(MICRO TEACHING)",
                                ["Tajuk: Ekspedisi Ayat — Ayat Aktif dan Ayat Pasif · SP [X.X.X]", NAME + " · " + ROLE]).convert("RGB")
        else:
            bg = grab("A", 2700)
            im = gfx.credits_card(bg, [("SETINGGI-TINGGI PENGHARGAAN", ["[NAMA PENSYARAH (jawatan)]"]),
                                       ("TERIMA KASIH", ["[NAMA KELUARGA / KUMPULAN]"]),
                                       ("GURU", [NAME, ROLE]),
                                       ("", ["[SLOGAN]"])]).convert("RGB")
    else:
        im = framed(s, s["tin"] + min(3.0, dur / 2))
        if s.get("gfx"):
            im = overlay(im, s["gfx"], s["phase"])
        if s["audio"] == "guru" and s["src"] == "A":
            im = Image.alpha_composite(im.convert("RGBA"), gfx.subtitle(
                [[("(contoh kedudukan sari kata)", gfx.WHITE, False)]])).convert("RGB")
    th = im.resize((480, 270), Image.LANCZOS)
    buf = io.BytesIO(); th.save(buf, "JPEG", quality=78)
    th.save(os.path.join(OUT, f"shot_{s['id']}.jpg"), quality=80)
    rows.append((s, start, dur, base64.b64encode(buf.getvalue()).decode()))

total = t
# ---------------------------------------------------------------- ringkasan masa
by_phase, guru_t, murid_t = {}, 0.0, 0.0
for s, st, d, _ in rows:
    by_phase[s["phase"]] = by_phase.get(s["phase"], 0) + d

css = """
:root{--f:#0B3B2C;--g:#D4AF37;--s:#6EB062;--bg:#f6f7f5;--tx:#1b2420;--mut:#5b6b63;--line:#dfe4e0;--card:#fff}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#0f1714;--tx:#e8efe9;--mut:#9fb0a7;--line:#24332c;--card:#15211c}}
:root[data-theme=dark]{--bg:#0f1714;--tx:#e8efe9;--mut:#9fb0a7;--line:#24332c;--card:#15211c}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--tx);font:15px/1.5 Inter,system-ui,sans-serif}
header{background:var(--f);color:#fff;padding:28px 16px}header .w{max-width:1100px;margin:auto}
h1{margin:0 0 4px;font-size:26px}h1 span{color:var(--g)}header p{margin:0;color:#cfe3d6}
main{max-width:1100px;margin:auto;padding:16px}
.sum{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 20px}.pill{background:var(--card);border:1px solid var(--line);border-radius:999px;padding:6px 12px}
.pill b{color:var(--s)}
h2{font-size:18px;margin:28px 0 8px;padding-left:10px;border-left:5px solid var(--g)}
.row{display:grid;grid-template-columns:300px 1fr;gap:14px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px;margin:10px 0}
.row img{width:100%;border-radius:8px;display:block}
.meta{font-size:13px;color:var(--mut)}.meta b{color:var(--tx)}
.tag{display:inline-block;font-size:12px;border-radius:6px;padding:1px 7px;margin-right:4px;background:var(--line)}
.tag.m{background:#6EB06233}.tag.g{background:#D4AF3733}
.note{font-size:13px;margin-top:4px;color:var(--mut)}
.box{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin:12px 0}
.box li{margin:4px 0}
@media (max-width:640px){.row{grid-template-columns:1fr}}
"""
h = [f"<!doctype html><html lang=ms><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Storyboard Pengajaran Mikro</title><style>{css}</style></head><body>"]
h.append(f"<header><div class=w><h1>Storyboard v1 — <span>Simulasi Pengajaran Mikro</span></h1>"
         f"<p>Bahasa Melayu Tahun 5 · Ekspedisi Ayat (Ayat Aktif &amp; Ayat Pasif) · Draf untuk kelulusan sebelum suntingan akhir</p></div></header><main>")
h.append("<div class=sum>" + f"<span class=pill>Tempoh draf <b>{mmss(total)}</b> (sasaran 15:00)</span>" +
         "".join(f"<span class=pill>{html.escape(k)} <b>{mmss(v)}</b></span>" for k, v in by_phase.items()) +
         f"<span class=pill>Shot <b>{len(rows)}</b></span></div>")
h.append(open(os.path.join(os.path.dirname(__file__), "storyboard_notes.html")).read())
cur = None
for s, st, d, b64 in rows:
    if s["phase"] != cur:
        cur = s["phase"]; h.append(f"<h2>{html.escape(cur)}</h2>")
    src = {"A": "Kamera utama", "G": "Gameplay tablet", "X": "Grafik"}[s["src"]]
    rng = f" · sumber {mmss(s['tin'])}–{mmss(s['tout'])}" if s["src"] != "X" else ""
    fr = ""
    if s.get("frame"):
        fr = "Wide (penuh)" if s["frame"][0] == "wide" else f"Potong zum {s['frame'][3]}×"
    au = {"guru": "<span class='tag g'>Suara guru</span>", "muzik": "<span class='tag m'>Muzik latar · suara disenyap</span>"}[s["audio"]]
    gf = ""
    if s.get("gfx"):
        gf = "<div class=note>Grafik: " + html.escape(s["gfx"].replace("||", " + ").replace("|", " / ")) + "</div>"
    nt = f"<div class=note>{html.escape(s['note'])}</div>" if s.get("note") else ""
    h.append(f"<div class=row><img alt='Shot {s['id']}' src='data:image/jpeg;base64,{b64}'><div>"
             f"<div class=meta><b>#{s['id']}</b> · video akhir <b>{mmss(st)}</b> (+{d:.1f} s) · {src}{rng} {('· ' + fr) if fr else ''}</div>"
             f"<div><b>{html.escape(s['shot'])}</b></div><div style='margin-top:4px'>{au}</div>{gf}{nt}</div></div>")
h.append("</main></body></html>")
open(os.path.join(OUT, "storyboard_v1.html"), "w").write("\n".join(h))
print("total", mmss(total), {k: mmss(v) for k, v in by_phase.items()})
