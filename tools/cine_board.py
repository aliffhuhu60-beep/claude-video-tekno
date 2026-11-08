"""Storyboard bergambar untuk versi 'video asal dikekalkan' + intro/outro sinematik."""
import sys, os, io, subprocess, base64, html
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import cine as C
SRC = "/home/user/raw2/video_asal.mp4"

def orig(t):
    seek = ["-sseof", "-0.25"] if t > C.ORIG_DUR - 0.3 else ["-ss", f"{t:.3f}"]
    p = subprocess.run(["ffmpeg", "-v", "error", *seek, "-i", SRC, "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, check=True)
    return Image.open(io.BytesIO(p.stdout)).convert("RGBA")

def frame(t):
    if t < C.S:
        return C.intro_frame(t)
    if t < C.INTRO_END:
        a = C.smooth((t - C.S) / (C.INTRO_END - C.S))
        im = Image.blend(C.intro_frame(t), orig(t - C.S), a)
    elif t < C.E:
        im = orig(t - C.S)
    else:
        return C.outro_frame(t, orig(C.ORIG_DUR - 0.04))
    for l, (x, y) in C.overlays_at(t):
        im.alpha_composite(l, (x, y))
    return im

def mm(t):
    return f"{int(t // 60):02d}:{t % 60:06.3f}"

ROWS = [
 ("INTRO", 0.25, "Pudar dari hitam: latar gelap elegan, cahaya bergerak perlahan, partikel emas, ikon garis pendidikan (buku, papan putih, topi graduasi), zum sinematik perlahan."),
 ("INTRO", 0.85, "Tajuk SIMULASI PENGAJARAN MIKRO didedahkan huruf demi huruf (jarak huruf mengecil + kabur gerakan berkurang)."),
 ("INTRO", 1.75, "Sapuan cahaya pada tajuk, garisan emas tumbuh, subtajuk 'Pengalaman Pengajaran, Pembelajaran dan Amalan Pedagogi' naik perlahan."),
 ("INTRO → ASAL", 3.0, "Smooth dissolve 0.8 s ke video asal (video asal bermula dari saat pertama pada 00:02.600)."),
 ("ASAL + tindihan", 5.0, "Jalur atas: penerangan simulasi pengajaran mikro; kata kunci ditebalkan emas satu demi satu. Lower third 1/3: nama pertama (letter reveal + garisan cahaya)."),
 ("ASAL + tindihan", 8.6, "Lower third 2/3. Cip kata kunci kinetik: KEMAHIRAN PEDAGOGI · STRATEGI PENGAJARAN · PENGURUSAN PEMBELAJARAN · PENGALAMAN PENGAJARAN."),
 ("ASAL + tindihan", 12.2, "Lower third 3/3. Grafik diletakkan di atas dinding / belakang badan — tidak menutup muka guru dan tidak bertembung dengan sari kata CapCut asal."),
 ("ASAL (bersih)", 16.5, "Tindihan pudar keluar sepenuhnya pada 00:16.0. Dari sini video asal dimainkan tanpa sebarang grafik, teks, transisi atau perubahan warna/audio."),
 ("ASAL (bersih)", 900.0, "Contoh pertengahan: kandungan asal 100% (termasuk sari kata CapCut anda sendiri)."),
 ("ASAL + tindihan", C.E - 8.5, "10 s akhir video asal: kad hitam-emas kiri-atas 'PENSYARAH PEMBIMBING · PUAN JULINA BINTI TARIKAT' (jarak huruf beranimasi, sapuan cahaya)."),
 ("ASAL + tindihan", C.E - 2.5, "'KELUARGA BMONETHO' — tipografi eksklusif, glow sinematik, garisan cahaya bergerak, zum-keluar halus."),
 ("ASAL → OUTRO", C.E + 0.25, "Video asal tamat pada 29:57.808 (bingkai terakhirnya dikekalkan) → dissolve ke latar hitam-emas."),
 ("OUTRO", C.E + 1.2, "TERIMA KASIH — pendedahan perlahan + sapuan cahaya."),
 ("OUTRO", 1799.85, "Pudar sehingga hitam sepenuhnya pada 30:00.000."),
]
out = sys.argv[1]
cards = []
for sec, t, txt in ROWS:
    im = frame(t).convert("RGB")
    b = io.BytesIO(); im.resize((640, 360), Image.LANCZOS).save(b, "JPEG", quality=80)
    cards.append((sec, t, txt, base64.b64encode(b.getvalue()).decode()))
css = open(os.path.join(os.path.dirname(__file__), "board.css")).read() + """
table{border-collapse:collapse;width:100%;margin:8px 0;background:var(--card)}td,th{border:1px solid var(--line);padding:6px 10px;text-align:left;font-size:14px}
.row{display:grid;grid-template-columns:340px 1fr;gap:14px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px;margin:10px 0}
.row img{width:100%;border-radius:8px}@media (max-width:640px){.row{grid-template-columns:1fr}}
.tag{display:inline-block;font-size:12px;border-radius:6px;padding:1px 8px;background:#D4AF3733;margin-right:6px}"""
h = [f"<!doctype html><html lang=ms><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Storyboard BMONETHO</title><style>{css}</style></head><body>",
     "<header><div class=w><h1>Storyboard — <span>Video Asal + Intro & Outro Sinematik</span></h1><p>BMONETHO · Simulasi Pengajaran Mikro · jumlah tepat 30:00.000</p></div></header><main>",
     "<div class=box><b>Analisis video asal</b><table><tr><th>Fail</th><td>video pengajaran mikro (tekno).mp4</td></tr>"
     "<tr><th>Durasi</th><td>29:55.208 (1795.208 s)</td></tr><tr><th>Resolusi / nisbah</th><td>1920×1080 · 16:9</td></tr>"
     "<tr><th>Frame rate</th><td>30 fps (purata 30.0003 — sedikit berubah)</td></tr><tr><th>Video</th><td>H.264 High, yuv420p, BT.709, ~9.6 Mbps</td></tr>"
     "<tr><th>Audio</th><td>AAC-LC, 44.1 kHz, stereo, ~228 kbps</td></tr><tr><th>SHA-256</th><td style='word-break:break-all'>d54e70eb…ab36b366 (fail asal tidak diubah)</td></tr></table></div>",
     "<div class=box><b>Laporan durasi (dirancang)</b><table><tr><th>Bahagian</th><th>Masa dalam video akhir</th><th>Durasi</th></tr>"
     "<tr><td>Intro (grafik penuh)</td><td>00:00.000 – 00:03.400</td><td>3.400 s (0.8 s terakhir dissolve bertindih dengan permulaan video asal)</td></tr>"
     "<tr><td>Video asal (penuh, tidak dipotong)</td><td>00:02.600 – 29:57.808</td><td>1795.208 s</td></tr>"
     "<tr><td>Outro (grafik penuh)</td><td>29:57.808 – 30:00.000</td><td>2.192 s</td></tr>"
     "<tr><td><b>Jumlah</b></td><td>00:00.000 – 30:00.000</td><td><b>1800.000 s = 30:00</b> (2.600 + 1795.208 + 2.192)</td></tr></table>"
     "<p class=meta>Tindihan ringan atas video asal (dibenarkan): pengenalan diri & penerangan pada 00:03.5–00:16.0, kad pensyarah & BMONETHO pada 29:47.8–29:57.8. Selain itu video asal bersih. Audio asal tidak diubah; muzik hanya pada 0–2.6 s dan 29:57.8–30:00 (tidak bertindih dengan suara asal).</p></div>"]
for sec, t, txt, b in cards:
    h.append(f"<div class=row><img src='data:image/jpeg;base64,{b}' alt=''><div><span class=tag>{html.escape(sec)}</span><b>{mm(t)}</b><p>{html.escape(txt)}</p></div></div>")
h.append("</main></body></html>")
open(out, "w").write("\n".join(h)); print("ok")
