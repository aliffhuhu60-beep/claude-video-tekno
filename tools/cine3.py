"""Intro / outro LEGAP skrin penuh (sama seperti gambar rujukan pengguna) + sari kata baharu.

Garis masa akhir (30 fps, 54 000 bingkai = 30:00.000):
  0.000 – 2.600      Intro sahaja (video asal belum bermula).
  2.600 – 1797.800   Video asal tanpa sari kata (53 856 bingkai), dari saat pertama hingga akhir.
      0.000 – 7.000    kad intro legap (menutup 4.4 s pertama video asal: guru masuk, tiada ucapan)
      7.000 – 7.800    dissolve kad intro -> video asal
      1789.600 – 1790.200  dissolve video asal -> kad hijau legap
      1790.200 – 1794.800  kad PENSYARAH (gambar 2)
      1795.000 – 1800.000  kad KELUARGA BMONETHO (gambar 3), pudar ke hitam 1799.2 – 1800.0
  1797.800 – 1800.000  hanya kad (video asal telah tamat).
Audio video asal dikekalkan sepenuhnya (dimainkan dari 2.600 hingga 1797.800).
"""
import os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import intro_outro as IO
from gfx import W, H, GOLD, SOFT, WHITE, SEMI, BOLD, XB, DSEMI

FPS = 30
S = 2.600
N_ORIG = 53856
E = S + N_ORIG / FPS            # 1797.800
TOTAL = 1800.000
IN_HOLD, IN_FADE = 7.0, 0.8
OUT_IN0, OUT_IN1 = 1789.6, 1790.2
CARD1 = (1790.2, 1794.8)
CARD2 = (1795.0, TOTAL)
BLACK0 = 1799.2

def smooth(u):
    u = min(max(u, 0.0), 1.0); return u * u * (3 - 2 * u)

X = 210
B = IO.block
INTRO_ELS = [
    IO.Bar(160, 300, 470, 0.20, 99),
    IO.El(B([(IO.INSTITUSI.upper(), BOLD(26), SOFT, 4), (IO.KURSUS, SEMI(26), (200, 225, 210), 0)]), X, 300, 0.30, 99),
    IO.El(B([("SIMULASI PENGAJARAN MIKRO", XB(88), WHITE, 0)]), X, 410, 0.80, 99),
    IO.El(B([("(MICRO TEACHING)", DSEMI(44), GOLD, 0)]), X, 525, 1.20, 99),
    IO.El(B([("Bahasa Melayu Tahun 5 · SP 5.3.3 Ayat Aktif dan Ayat Pasif", SEMI(30), (220, 232, 225), 0)]), X, 600, 1.60, 99),
    IO.El(B([("DISEDIAKAN OLEH", BOLD(22), GOLD, 6), (IO.NAMA, XB(46), WHITE, 6), (IO.OPSYEN, SEMI(28), SOFT, 0)]), X, 680, 2.40, 99),
]

def _c(lines, t0, t1):
    im = IO.block(lines, align="center")
    return IO.El(im, (W - im.width) // 2, (H - im.height) // 2, t0, t1, dx=0, dy=40, fin=0.8, fout=0.8)

OUTRO_ELS = [
    _c([("SETINGGI-TINGGI PENGHARGAAN", BOLD(30), GOLD, 26),
        ("kepada pensyarah yang dihormati", SEMI(30), (210, 228, 218), 22),
        (IO.PENSYARAH, XB(70), WHITE, 18),
        ("Pensyarah " + IO.KURSUS, SEMI(28), SOFT, 6),
        (IO.INSTITUSI, SEMI(28), SOFT, 0)], CARD1[0], CARD1[1]),
    _c([("TERIMA KASIH", BOLD(30), GOLD, 26),
        ("atas sokongan, kerjasama dan semangat", SEMI(30), (210, 228, 218), 22),
        (IO.KELUARGA, XB(84), WHITE, 0)], CARD2[0], CARD2[1] + 5),
]

def graphic(t):
    """RGBA lapisan kad pada masa akhir t (None jika tiada)."""
    if t < IN_HOLD + IN_FADE:
        a = 1.0 - smooth((t - IN_HOLD) / IN_FADE)
        els = INTRO_ELS
    elif t >= OUT_IN0:
        a = smooth((t - OUT_IN0) / (OUT_IN1 - OUT_IN0))
        els = OUTRO_ELS
    else:
        return None
    if a <= 0.001:
        return None
    im = IO.background(t)
    for e in els:
        e.draw(im, t)
    if t < 0.5:   # pudar dari hitam
        im = Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 255)), im, smooth(t / 0.5))
    if t > BLACK0:
        im = Image.blend(im, Image.new("RGBA", (W, H), (0, 0, 0, 255)), smooth((t - BLACK0) / (TOTAL - BLACK0)))
    if a < 1:
        im.putalpha(int(255 * a))
    return im
