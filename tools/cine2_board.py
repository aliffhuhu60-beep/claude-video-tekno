"""Storyboard v3: video asal dikekalkan + intro/outro gaya hijau (tiada nama lain)."""
import sys, os, io, subprocess, base64, html
sys.path.insert(0, os.path.dirname(__file__))
import cine2 as C
from PIL import Image
SRC = "/home/user/raw2/video_asal.mp4"
def orig(t):
    seek = ["-sseof", "-0.25"] if t > 1795.0 else ["-ss", f"{t:.3f}"]
    p = subprocess.run(["ffmpeg", "-v", "error", *seek, "-i", SRC, "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
    return Image.open(io.BytesIO(p.stdout)).convert("RGBA")
def frame(t):
    base = orig(t - C.S) if C.S <= t < C.E else Image.new("RGBA", (1920, 1080), (0, 0, 0, 255))
    g = C.graphic(t)
    if g is not None: base.alpha_composite(g)
    return base.convert("RGB")
def mm(t): return f"{int(t // 60):02d}:{t % 60:06.3f}"
ROWS = [
 ("INTRO", 0.3, "Pudar dari hitam ke latar hijau dengan partikel emas; jalur emas tumbuh, teks muncul satu demi satu."),
 ("INTRO", 2.4, "Kad intro lengkap: IPG Kampus Tun Hussein Onn · EDUP3133 · SIMULASI PENGAJARAN MIKRO (MICRO TEACHING) · Bahasa Melayu Tahun 5 · SP 5.3.3 · Disediakan oleh MOHAMAD ALIFF BIN AHMAD SHAHABUDDIN · Opsyen Bahasa Melayu."),
 ("INTRO → ASAL", 3.6, "Video asal bermula dari saat pertama pada 00:02.600. Latar hijau dissolve menjadi lut sinar supaya kad masih boleh dibaca."),
 ("INTRO → ASAL", 7.7, "Kad pudar keluar sepenuhnya menjelang 00:08.2 (transisi lembut)."),
 ("ASAL", 9.0, "Video asal dimainkan seperti asal — tanpa grafik, tanpa potongan. Hanya sari kata baharu yang telah dibetulkan (bawah-tengah)."),
 ("ASAL", 600.0, "Contoh pertengahan video asal."),
 ("ASAL → OUTRO", C.E - 9.5, "10 s akhir: latar hijau lut sinar masuk perlahan; SETINGGI-TINGGI PENGHARGAAN kepada PUAN JULINA BINTI TARIKAT."),
 ("ASAL → OUTRO", C.E - 3.0, "TERIMA KASIH atas sokongan, kerjasama dan semangat — KELUARGA BMONETHO."),
 ("OUTRO", C.E + 0.4, "Video asal tamat 29:57.800 → latar hijau penuh: DISEDIAKAN OLEH MOHAMAD ALIFF BIN AHMAD SHAHABUDDIN · SIMULASI PENGAJARAN MIKRO (MICRO TEACHING)."),
 ("OUTRO", 1799.7, "Pudar ke hitam sepenuhnya tepat pada 30:00.000."),
]
cards = []
for sec, t, txt in ROWS:
    b = io.BytesIO(); frame(t).resize((640, 360), Image.LANCZOS).save(b, "JPEG", quality=80)
    cards.append((sec, t, txt, base64.b64encode(b.getvalue()).decode()))
css = open(os.path.join(os.path.dirname(__file__), "board.css")).read() + """
table{border-collapse:collapse;width:100%;margin:8px 0;background:var(--card)}td,th{border:1px solid var(--line);padding:6px 10px;text-align:left;font-size:14px}
.row{display:grid;grid-template-columns:340px 1fr;gap:14px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px;margin:10px 0}
.row img{width:100%;border-radius:8px}@media (max-width:640px){.row{grid-template-columns:1fr}}
.tag{display:inline-block;font-size:12px;border-radius:6px;padding:1px 8px;background:#D4AF3733;margin-right:6px}"""
h = [f"<!doctype html><html lang=ms><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Storyboard v3</title><style>{css}</style></head><body>",
     "<header><div class=w><h1>Storyboard v3 — <span>Video Asal + Intro & Outro</span></h1><p>Simulasi Pengajaran Mikro · jumlah tepat 30:00.000 · tiada nama lain selain guru & pensyarah</p></div></header><main>",
     "<div class=box><b>Laporan durasi (dirancang)</b><table><tr><th>Bahagian</th><th>Masa dalam video akhir</th><th>Durasi</th></tr>"
     "<tr><td>Intro (kad hijau penuh)</td><td>00:00.000 – 00:02.600</td><td>2.600 s (78 bingkai)</td></tr>"
     "<tr><td>Video asal — penuh, tidak dipotong</td><td>00:02.600 – 29:57.800</td><td>1795.200 s (53 856 bingkai @30 fps; fail asal 1795.208 s)</td></tr>"
     "<tr><td>Outro (kad hijau penuh)</td><td>29:57.800 – 30:00.000</td><td>2.200 s (66 bingkai)</td></tr>"
     "<tr><td><b>Jumlah</b></td><td></td><td><b>1800.000 s = 30:00 (54 000 bingkai)</b></td></tr></table>"
     "<p class=meta>Tindihan lut sinar yang dibenarkan: kad intro pada 00:02.6–00:08.2, kad penghargaan pada 29:47.2–29:57.8. Sari kata baharu (gaya arahan asal) dipaparkan sepanjang video asal. Bingkai dalam storyboard ini menggunakan video sekarang — sari kata CapCut lama yang kelihatan akan tiada dalam versi akhir (video tanpa sari kata).</p></div>"]
for sec, t, txt, b in cards:
    h.append(f"<div class=row><img src='data:image/jpeg;base64,{b}' alt=''><div><span class=tag>{html.escape(sec)}</span><b>{mm(t)}</b><p>{html.escape(txt)}</p></div></div>")
h.append("</main></body></html>")
open(sys.argv[1], "w").write("\n".join(h)); print("ok")
