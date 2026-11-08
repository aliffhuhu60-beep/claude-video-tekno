"""Intro / outro gaya hijau (seperti intro_v1/outro_v1 yang diluluskan) — versi 'video asal dikekalkan'.

Garis masa akhir (30 fps, jumlah 54000 bingkai = 30:00.000):
  0.000 – 2.600    INTRO penuh (kad hijau).
  2.600 – 1797.800 VIDEO ASAL (53856 bingkai, dari saat pertama hingga akhir, tidak dipotong).
       2.600 – 8.200   kad intro kekal sebagai tindihan lut sinar, kemudian pudar keluar (transisi lembut).
       E-10.6 – E      kad penghargaan (pensyarah, Keluarga BMONETHO) muncul secara lut sinar.
  1797.800 – 1800.000 OUTRO penuh: 'Disediakan oleh' + tajuk, pudar ke hitam.
Hanya satu nama individu dipaparkan (MOHAMAD ALIFF BIN AHMAD SHAHABUDDIN) + nama pensyarah.
"""
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__))
import intro_outro as IO
from gfx import W, H, FOREST, GOLD, SOFT, WHITE, SEMI, BOLD, XB, DSEMI

FPS = 30
S = 2.600
N_ORIG = 53856                       # bingkai video asal pada 30 fps (1795.208 s)
E = S + N_ORIG / FPS                 # 1797.800
TOTAL = 1800.000
INTRO_OVL_END = 8.2
OUTRO_OVL_START = E - 10.6

def ease(u):
    u = min(max(u, 0.0), 1.0); return 1 - (1 - u) ** 3
def smooth(u):
    u = min(max(u, 0.0), 1.0); return u * u * (3 - 2 * u)

# ---------------------------------------------------------------- elemen intro (susun atur intro_v1)
X = 210
B = IO.block
INTRO_ELS = [
    IO.Bar(160, 300, 470, 0.10, 99),
    IO.El(B([(IO.INSTITUSI.upper(), BOLD(26), SOFT, 4), (IO.KURSUS, SEMI(26), (200, 225, 210), 0)]), X, 300, 0.15, 99, fin=0.5),
    IO.El(B([("SIMULASI PENGAJARAN MIKRO", XB(88), WHITE, 0)]), X, 410, 0.35, 99, fin=0.5),
    IO.El(B([("(MICRO TEACHING)", DSEMI(44), GOLD, 0)]), X, 525, 0.60, 99, fin=0.5),
    IO.El(B([("Bahasa Melayu Tahun 5 · SP 5.3.3 Ayat Aktif dan Ayat Pasif", SEMI(30), (220, 232, 225), 0)]), X, 600, 0.85, 99, fin=0.5),
    IO.El(B([("DISEDIAKAN OLEH", BOLD(22), GOLD, 6), (IO.NAMA, XB(46), WHITE, 6), (IO.OPSYEN, SEMI(28), SOFT, 0)]), X, 680, 1.10, 99, fin=0.5),
]

def _centred(lines, t0, t1, fin=0.7, fout=0.7):
    im = IO.block(lines, align="center")
    return IO.El(im, (W - im.width) // 2, (H - im.height) // 2, t0, t1, dx=0, dy=36, fin=fin, fout=fout)

OUTRO_ELS = [
    _centred([("SETINGGI-TINGGI PENGHARGAAN", BOLD(30), GOLD, 26),
              ("kepada pensyarah yang dihormati", SEMI(30), (210, 228, 218), 22),
              (IO.PENSYARAH, XB(70), WHITE, 18),
              ("Pensyarah " + IO.KURSUS, SEMI(28), SOFT, 6),
              (IO.INSTITUSI, SEMI(28), SOFT, 0)], OUTRO_OVL_START + 0.5, E - 5.3),
    _centred([("TERIMA KASIH", BOLD(30), GOLD, 26),
              ("atas sokongan, kerjasama dan semangat", SEMI(30), (210, 228, 218), 22),
              (IO.KELUARGA, XB(84), WHITE, 0)], E - 5.1, E - 0.15),
    _centred([("DISEDIAKAN OLEH", BOLD(30), GOLD, 22),
              (IO.NAMA, XB(58), WHITE, 16),
              ("SIMULASI PENGAJARAN MIKRO (MICRO TEACHING)", DSEMI(32), GOLD, 0)], E + 0.05, TOTAL - 0.05, fin=0.5, fout=0.6),
]

def _bg_alpha(t):
    """Kelegapan latar hijau di atas video asal (1 = penuh)."""
    if t < S:
        return 1.0
    if t < INTRO_OVL_END:
        a = 1.0 - 0.30 * smooth((t - S) / 0.9)                    # dissolve ke lut sinar (0.70)
        return a * (1 - smooth((t - (INTRO_OVL_END - 1.0)) / 1.0))  # pudar keluar
    if t < OUTRO_OVL_START:
        return 0.0
    if t < E:
        return 0.80 * smooth((t - OUTRO_OVL_START) / 0.9)
    return 1.0

def _el_alpha(t):
    if S <= t < INTRO_OVL_END:
        return 1 - smooth((t - (INTRO_OVL_END - 1.0)) / 1.0)
    return 1.0

def graphic(t):
    """Lapisan RGBA (latar hijau + teks) pada masa akhir t, atau None jika tiada."""
    a_bg = _bg_alpha(t)
    els = INTRO_ELS if t < INTRO_OVL_END else (OUTRO_ELS if t >= OUTRO_OVL_START else [])
    if a_bg <= 0.001 and not els:
        return None
    bg = IO.background(t)
    if a_bg < 1:
        bg.putalpha(int(255 * a_bg))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for e in els:
        e.draw(lay, t)
    k = _el_alpha(t)
    if k < 1:
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * k)))
    bg.alpha_composite(lay)
    # pudar dari hitam (awal) dan ke hitam (akhir)
    if t < 0.4:
        bg = Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 255)), bg, smooth(t / 0.4))
    if t > TOTAL - 0.7:
        bg = Image.blend(bg, Image.new("RGBA", (W, H), (0, 0, 0, 255)), smooth((t - (TOTAL - 0.7)) / 0.7))
    return bg
