"""Storyboard penuh v4: kad intro/outro legap + video asal tanpa sari kata + sari kata baharu + jadual semakan CapCut."""
import base64, html, io, json, os, re, subprocess, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import cine3 as C
import gfx
from subs3 import items, wrap2, colorize, KEY

CLEAN = "/home/user/raw2/video_tanpa_sk.mp4"
OLD = "/home/user/raw2/video_asal.mp4"
ITEMS = items()

def grab(src, t, w=1920):
    seek = ["-sseof", "-0.25"] if t > 1795.0 else ["-ss", f"{t:.3f}"]
    p = subprocess.run(["ffmpeg", "-v", "error", *seek, "-i", src, "-frames:v", "1", "-vf", f"scale={w}:-2",
                        "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
    return Image.open(io.BytesIO(p.stdout)).convert("RGBA")

def sub_at(t):
    for a, b, txt, *_ in ITEMS:
        if a <= t < b:
            return txt

def sub_img(txt):
    lines = []
    for ln in wrap2(txt):
        parts, col, bold = [], gfx.WHITE, False
        for tok in re.split(r"(\{[^}]*\})", colorize(ln)):
            if tok.startswith("{"):
                if "37AFD4" in tok: col, bold = gfx.GOLD, True
                elif "62B06E" in tok: col, bold = gfx.SOFT, True
                else: col, bold = gfx.WHITE, False
            elif tok:
                parts.append((tok, col, bold))
        lines.append(parts)
    return gfx.subtitle(lines)

def frame(t):
    im = grab(CLEAN, t - C.S) if C.S <= t < C.E else Image.new("RGBA", (1920, 1080), (0, 0, 0, 255))
    g = C.graphic(t)
    if g is not None:
        im.alpha_composite(g)
    s = sub_at(t)
    if s:
        im.alpha_composite(sub_img(s))
    return im.convert("RGB")

def b64(im, w=640):
    b = io.BytesIO(); im.resize((w, int(w * 9 / 16)), Image.LANCZOS).save(b, "JPEG", quality=78)
    return base64.b64encode(b.getvalue()).decode()

def mm(t):
    return f"{int(t // 60):02d}:{t % 60:06.3f}"

# ---------------------------------------------------------------- babak storyboard
def mid(i):
    a, b = ITEMS[i][0], ITEMS[i][1]; return (a + b) / 2
def find(sub):
    for i, it in enumerate(ITEMS):
        if sub.lower() in it[2].lower(): return mid(i)
    raise KeyError(sub)

SCENES = [
 ("INTRO", 0.25, "Pudar dari hitam ke latar hijau, partikel emas; jalur emas tumbuh."),
 ("INTRO", 3.2, "Kad intro lengkap seperti gambar rujukan (legap skrin penuh). Video asal sudah bermula di belakang pada 00:02.600 — 4.4 s pertama (guru masuk, tiada ucapan) ditutup kad."),
 ("INTRO → VIDEO", 7.4, "Dissolve 0.8 s dari kad ke video asal."),
 ("SET INDUKSI", find("Assalamualaikum, cikgu"), "Salam pembukaan — sari kata baharu bermula."),
 ("SET INDUKSI", find("Waalaikumussalam"), "Diubah: 'cikgu' di hadapan dibuang (sebahagian salam murid)."),
 ("SET INDUKSI", find("Ayat aktif menunjukkan subjek"), "Video tayangan: kata kunci ayat aktif (emas) & subjek/perbuatan (hijau)."),
 ("SET INDUKSI", find("mari kita terokai ayat aktif"), "Diubah: 'air … air aktif dan air aktif' → ayat aktif dan ayat pasif."),
 ("SET INDUKSI", find("iaitu ciri-ciri ayat pasif"), "Diubah: 'ciri ciri air masin' → ciri-ciri ayat pasif."),
 ("SET INDUKSI", find("Kata kerja transitif"), "Diubah: 'kata kerja transit' → kata kerja transitif."),
 ("SET INDUKSI", find("Minecraft Education dengan betul"), "Objektif — diubah: 'Microsoft education' → Minecraft Education."),
 ("LANGKAH 1", find("Kod dia: llama"), "Diubah: 'kod dia lama / epal lama lama' → kod sertai bergambar: llama, epal, llama, llama."),
 ("LANGKAH 1", find("Misi Penyelamat Ayat, iaitu"), "Penerangan Bahagian A."),
 ("LANGKAH 1", find("Di sini ada 8 stesen"), "Diubah: '8 fesyen' → 8 stesen (ikut slaid Cara Bermain)."),
 ("LANGKAH 1", find("Kumpulan ini akan pergi ke warna merah"), "Nama murid dibuang daripada sari kata."),
 ("LANGKAH 1", find("iaitu ayat tanpa subjek. Jadi"), "Diubah: 'ayat tanpa hujung' → ayat tanpa subjek."),
 ("LANGKAH 1", find("nanti akan letak di bahagian bingkai"), "Jenis 2 — nama murid dibuang; 'frame' → bingkai (istilah permainan)."),
 ("LANGKAH 1", find("panggil parkour"), "Jenis 3 — diubah: 'bakau' → parkour."),
 ("LANGKAH 1", find("Kumpulan biru sedang mendahului"), "Diubah: 'bulan biru' → kumpulan biru."),
 ("LANGKAH 2", find("Okey, sekarang ni kita akan beralih kepada bahagian 2"), "Peralihan ke Bahagian B."),
 ("LANGKAH 2", find("Akan keluar paparan bina ayat"), "Diubah: 'paparan ini ayat' → paparan bina ayat."),
 ("LANGKAH 2", find("tercapailah objektif"), "Cabaran Akhir."),
 ("PENUTUP", find("Refleksi. Cikgu nak"), "Diubah: 'teksi' → Refleksi."),
 ("PENUTUP", find("Saya boleh membina ayat pasif"), "Diubah: 'ayat basic' → ayat pasif."),
 ("VIDEO → OUTRO", 1789.9, "Dissolve 0.6 s dari video asal ke kad hijau legap (audio asal diteruskan)."),
 ("OUTRO", 1792.4, "Kad PENSYARAH seperti gambar rujukan: SETINGGI-TINGGI PENGHARGAAN · PUAN JULINA BINTI TARIKAT. Sari kata salam penutup masih dipaparkan di bawah."),
 ("OUTRO", 1797.0, "Kad KELUARGA BMONETHO seperti gambar rujukan."),
 ("OUTRO", 1799.6, "Pudar ke hitam sepenuhnya tepat pada 30:00.000."),
]

if __name__ == "__main__":
    out = sys.argv[1]
    css = open(os.path.join(os.path.dirname(__file__), "board.css")).read() + """
table{border-collapse:collapse;width:100%;background:var(--card)}td,th{border:1px solid var(--line);padding:5px 8px;text-align:left;font-size:13px;vertical-align:top}
.row{display:grid;grid-template-columns:360px 1fr;gap:14px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px;margin:10px 0}
.row img{width:100%;border-radius:8px}@media (max-width:700px){.row{grid-template-columns:1fr}.cmp{grid-template-columns:1fr!important}}
.tag{display:inline-block;font-size:12px;border-radius:6px;padding:1px 8px;background:#D4AF3733;margin-right:6px}
.K{color:#3c8d40;font-weight:700}.U{color:#b8860b;font-weight:700}.B{color:#c0392b;font-weight:700}
.cmp{display:grid;grid-template-columns:1fr 1fr;gap:10px}.cmp figure{margin:0}.cmp img{width:100%;border-radius:8px}
.scroll{overflow-x:auto}"""
    from capcut_review import R
    from collections import Counter
    cnt = Counter(r[2] for r in R)
    h = [f"<!doctype html><html lang=ms><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Storyboard Penuh v4</title><style>{css}</style></head><body>",
         "<header><div class=w><h1>Storyboard Penuh — <span>Versi Akhir 30:00</span></h1><p>Video asal tanpa sari kata + sari kata baharu + intro & outro seperti gambar rujukan</p></div></header><main>"]
    h.append("<div class=box><b>Analisis video</b><table>"
             "<tr><th>Video digunakan</th><td>video pdp tekno tanpa sarikata.mp4 — 29:55.208, 1920×1080, 30 fps tetap (53 856 bingkai), H.264 High, AAC 44.1 kHz stereo</td></tr>"
             "<tr><th>Rujukan sari kata</th><td>video pengajaran mikro (tekno).mp4 — 293 selang sari kata CapCut dikesan dengan membandingkan kedua-dua video bingkai demi bingkai, kemudian dibaca satu per satu</td></tr></table></div>")
    h.append("<div class=box><b>Laporan durasi</b><table><tr><th>Bahagian</th><th>Masa</th><th>Durasi</th></tr>"
             "<tr><td>Intro sahaja</td><td>00:00.000 – 00:02.600</td><td>2.600 s</td></tr>"
             "<tr><td>Video asal (penuh, tidak dipotong, audio asal)</td><td>00:02.600 – 29:57.800</td><td>1795.200 s (53 856 bingkai)</td></tr>"
             "<tr><td>Outro sahaja</td><td>29:57.800 – 30:00.000</td><td>2.200 s</td></tr>"
             "<tr><td><b>Jumlah</b></td><td></td><td><b>1800.000 s = 30:00</b></td></tr></table>"
             "<p class=meta>Kad legap menutup gambar video asal pada 00:02.6–00:07.8 (guru berjalan masuk, tiada ucapan) dan 29:49.6–29:57.8 (ucapan selamat tinggal — audio tetap kedengaran dan sari katanya tetap dipaparkan). Selain itu gambar video asal tidak disentuh, kecuali sari kata baharu.</p></div>")
    h.append(f"<div class=box><b>Ringkasan semakan sari kata CapCut</b> — 293 selang → {len(R)} baris: "
             f"<span class=K>KEKAL {cnt['KEKAL']}</span> · <span class=U>UBAH {cnt['UBAH']}</span> · <span class=B>BUANG {cnt['BUANG']}</span>."
             "<ul><li><b>KEKAL</b>: perkataan sama; hanya huruf besar, tanda baca, sempang (ciri-ciri) dan nombor dikemas.</li>"
             "<li><b>UBAH</b>: salah dengar dibetulkan ikut bunyi sebenar & istilah permainan (ayat pasif, Minecraft Education, stesen, PETI, bingkai, parkour, Galeri Isu); semua nama murid dibuang.</li>"
             "<li><b>BUANG</b>: serpihan tidak jelas, kiraan, bunyi bising, atau baris yang hanya mengandungi nama murid.</li>"
             "<li>Gaya: kotak hijau gelap separa lut sinar, bawah-tengah, maks 2 baris; <span style='color:#D4AF37'><b>ayat aktif</b></span> emas, <span style='color:#6EB062'><b>ayat pasif</b></span> & istilah hijau.</li></ul></div>")
    # perbandingan sebelum/selepas
    h.append("<h2>Sebelum (CapCut) vs Selepas (baharu)</h2>")
    for lab, sub in (("air aktif / air aktif", "mari kita terokai ayat aktif"), ("ciri ciri air masin", "iaitu ciri-ciri ayat pasif"),
                     ("Microsoft education", "Minecraft Education dengan betul"), ("Fadli … frame", "nanti akan letak di bahagian bingkai")):
        t = find(sub)
        old = grab(OLD, t - C.S).convert("RGB"); new = frame(t)
        h.append(f"<div class=cmp><figure><img src='data:image/jpeg;base64,{b64(old, 560)}'><figcaption>Sebelum: “{html.escape(lab)}”</figcaption></figure>"
                 f"<figure><img src='data:image/jpeg;base64,{b64(new, 560)}'><figcaption>Selepas · {mm(t)}</figcaption></figure></div>")
    h.append("<h2>Storyboard ikut masa</h2>")
    for sec, t, txt in SCENES:
        h.append(f"<div class=row><img src='data:image/jpeg;base64,{b64(frame(t))}' alt=''><div><span class=tag>{html.escape(sec)}</span><b>{mm(t)}</b><p>{html.escape(txt)}</p></div></div>")
    # jadual penuh
    h.append("<h2>Jadual penuh sari kata (293 selang CapCut)</h2><div class=scroll><table><tr><th>#</th><th>Masa (video akhir)</th><th>Sari kata CapCut</th><th>Keputusan</th><th>Sari kata baharu</th></tr>")
    SEG = json.load(open("/home/user/work/cap_segs.json"))
    for idx, cap, dec, new in sorted(R, key=lambda r: r[0][0]):
        a = SEG[idx[0]][0] + C.S
        cls = dec[0]
        h.append(f"<tr><td>{'/'.join(map(str, idx))}</td><td>{mm(a)}</td><td>{html.escape(cap)}</td><td class={cls}>{dec}</td><td>{html.escape(new or '—')}</td></tr>")
    h.append("</table></div></main></body></html>")
    open(out, "w").write("\n".join(h)); print("ok")
