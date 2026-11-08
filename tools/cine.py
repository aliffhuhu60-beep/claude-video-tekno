"""Grafik sinematik untuk INTRO / OUTRO (BMONETHO) — versi 'video asal dikekalkan'.

Garis masa akhir (saat, 30 fps):
  0.000 – 3.400   INTRO penuh (latar gelap, partikel, cahaya, tajuk). Dissolve ke video asal 2.600 – 3.400.
  2.600 – 1797.808  VIDEO ASAL (1795.208 s) — dimainkan dari saat pertama hingga akhir, tanpa dipotong.
     Tindihan ringan (dibenarkan pemilik): pengenalan diri + penerangan pada 13 s awal,
     kad pensyarah + Keluarga BMONETHO pada 10 s akhir.
  1797.808 – 1800.000  OUTRO penuh: TERIMA KASIH -> hitam.
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1920, 1080, 30
FD = "/usr/share/fonts/opentype/inter/"
F = lambda n, s: ImageFont.truetype(FD + n + ".otf", s)
GOLD = (212, 175, 55)
GOLD_L = (240, 214, 140)
WHITE = (255, 255, 255)
INK = (7, 12, 10)

ORIG_DUR = 1795.208
S = 2.600                       # video asal bermula
E = S + ORIG_DUR                # 1797.808 video asal tamat
TOTAL = 1800.000
INTRO_END = 3.400               # intro selesai (dissolve 2.6 – 3.4)

NAMES = ["MOHAMAD ALIFF BIN AHMAD SHAHABUDDIN", "MUHAMMAD IMAN IRFAN BIN MOHD RAMZI", "AMIN NAJMI BIN MOHYIDIN"]
PENSYARAH = "PUAN JULINA BINTI TARIKAT"
DESC = ("Simulasi pengajaran mikro merupakan satu pengalaman latihan pengajaran yang memberikan peluang untuk "
        "mengaplikasikan kemahiran pedagogi, strategi pengajaran dan pengurusan pembelajaran dalam suasana simulasi.")
KEYS = ["KEMAHIRAN PEDAGOGI", "STRATEGI PENGAJARAN", "PENGURUSAN PEMBELAJARAN", "PENGALAMAN PENGAJARAN"]
HIGHLIGHT = ["kemahiran pedagogi", "strategi pengajaran", "pengurusan pembelajaran", "pengalaman latihan pengajaran"]


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return 1 - (1 - u) ** 3

def smooth(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)

def tw(f, s):
    return ImageDraw.Draw(Image.new("L", (1, 1))).textlength(s, font=f)


# ------------------------------------------------------------------ latar sinematik
_rng = np.random.default_rng(5)
PART = _rng.random((140, 5))            # x, y, saiz, kelajuan, fasa

def _icons():
    """Ikon garis pendidikan minimalis (buku, papan putih, topi graduasi) — lapisan pudar."""
    im = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(im)
    # buku terbuka
    cx, cy = 300, 760
    d.line([(cx - 120, cy), (cx, cy + 30), (cx + 120, cy)], fill=255, width=3)
    d.line([(cx - 120, cy - 90), (cx, cy - 60), (cx + 120, cy - 90)], fill=255, width=3)
    d.line([(cx - 120, cy - 90), (cx - 120, cy)], fill=255, width=3)
    d.line([(cx + 120, cy - 90), (cx + 120, cy)], fill=255, width=3)
    d.line([(cx, cy - 60), (cx, cy + 30)], fill=255, width=3)
    # papan putih
    d.rectangle((1500, 180, 1780, 360), outline=255, width=3)
    d.line([(1640, 360), (1600, 440)], fill=255, width=3); d.line([(1640, 360), (1680, 440)], fill=255, width=3)
    d.line([(1530, 230), (1700, 230)], fill=255, width=2); d.line([(1530, 270), (1660, 270)], fill=255, width=2)
    # topi graduasi
    gx, gy = 1600, 820
    d.polygon([(gx - 130, gy), (gx, gy - 55), (gx + 130, gy), (gx, gy + 55)], outline=255, width=3)
    d.line([(gx - 70, gy + 25), (gx - 70, gy + 85)], fill=255, width=3)
    d.line([(gx + 70, gy + 25), (gx + 70, gy + 85)], fill=255, width=3)
    d.arc((gx - 70, gy + 45, gx + 70, gy + 125), 0, 180, fill=255, width=3)
    d.line([(gx + 130, gy), (gx + 130, gy + 90)], fill=255, width=2)
    return im.filter(ImageFilter.GaussianBlur(0.8))
ICONS = _icons()

_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)

def background(t, warm=False, icons=True):
    # gradien jejari gelap + alur cahaya bergerak perlahan
    cx = W * (0.30 + 0.25 * math.sin(t * 0.25))
    cy = H * (0.35 + 0.05 * math.cos(t * 0.3))
    r = np.sqrt(((_xx - cx) / W) ** 2 + ((_yy - cy) / H) ** 2)
    glow = np.exp(-r * 3.2)[..., None]
    base = np.array(INK, np.float32)
    tint = np.array((38, 32, 14) if warm else (14, 46, 34), np.float32)
    img = base + tint * glow * 1.6
    # sinar cahaya pepenjuru
    band = np.exp(-(((_xx - _yy * 0.6) - (W * (0.1 + 0.08 * t))) / 220.0) ** 2)[..., None]
    img = img + np.array((60, 52, 30), np.float32) * band * 0.35
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    if icons:
        ic = Image.new("RGBA", (W, H), GOLD + (0,))
        ic.putalpha(ICONS.point(lambda v: int(v * 0.10)))
        dx = int(10 * math.sin(t * 0.4)); dy = int(-6 * t)
        im.alpha_composite(ic, (dx, dy))
    # partikel debu emas
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for x, y, s, sp, ph in PART:
        px = (x * W + 25 * math.sin(t * 0.6 + ph * 6)) % W
        py = (y * H - (10 + 30 * sp) * t) % H
        a = int(60 + 140 * (0.5 + 0.5 * math.sin(t * 1.5 + ph * 9)))
        rr = 1 + 2.5 * s
        d.ellipse((px - rr, py - rr, px + rr, py + rr), fill=GOLD_L + (a,))
    lay = lay.filter(ImageFilter.GaussianBlur(1.1))
    im.alpha_composite(lay)
    return im


def zoom(im, z):
    if abs(z - 1) < 1e-4:
        return im
    w, h = im.size
    nw, nh = int(w / z), int(h / z)
    x0, y0 = (w - nw) // 2, (h - nh) // 2
    return im.crop((x0, y0, x0 + nw, y0 + nh)).resize((w, h), Image.BICUBIC)


# ------------------------------------------------------------------ teks sinematik
def reveal_text(text, font, t, t0, dur=1.0, color=WHITE, track0=18, track1=4, blur0=6.0):
    """Huruf demi huruf: pudar masuk + jarak huruf mengecil + kabur gerakan berkurang."""
    n = len(text)
    tr = track1 + (track0 - track1) * (1 - ease((t - t0) / (dur + 0.4)))
    widths = [tw(font, ch) for ch in text]
    total = sum(widths) + tr * (n - 1)
    hgt = int(font.size * 1.35)
    pad = 30
    im = Image.new("RGBA", (int(total) + pad * 2, hgt + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = pad
    for i, ch in enumerate(text):
        ti = t0 + dur * (i / max(1, n - 1)) * 0.75
        a = ease((t - ti) / 0.35)
        if a > 0:
            d.text((x, pad), ch, font=font, fill=color + (int(255 * a),))
        x += widths[i] + tr
    bl = blur0 * (1 - ease((t - t0) / (dur + 0.3)))
    if bl > 0.3:
        im = im.filter(ImageFilter.GaussianBlur(bl))
    return im


def light_sweep(img, t, t0, dur=0.7, width=90, strength=110):
    """Sapuan cahaya melintasi alfa imej teks."""
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return img
    w, h = img.size
    a = np.array(img.getchannel("A"), np.float32) / 255
    xx = np.arange(w)[None, :] + np.arange(h)[:, None] * 0.35
    cx = -width + (w + 2 * width + h * 0.35) * u
    band = np.exp(-((xx - cx) / width) ** 2) * a
    arr = np.array(img, np.float32)
    arr[..., :3] = np.clip(arr[..., :3] + band[..., None] * strength, 0, 255)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


def glow(img, radius=14, k=1.0):
    g = img.filter(ImageFilter.GaussianBlur(radius))
    arr = np.array(g, np.float32); arr[..., 3] *= k
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    out.alpha_composite(img)
    return out


def fade(img, a):
    if a >= 1: return img
    img = img.copy(); img.putalpha(img.getchannel("A").point(lambda v: int(v * max(0, a))))
    return img


# ------------------------------------------------------------------ INTRO (0 – 3.4 s)
F_TITLE = F("InterDisplay-ExtraBold", 104)
F_SUB = F("InterDisplay-Medium", 38)

def intro_frame(t):
    z = 1.0 + 0.05 * smooth(t / INTRO_END)                      # zum perlahan
    im = background(t)
    title = reveal_text("SIMULASI PENGAJARAN MIKRO", F_TITLE, t, 0.35, dur=1.0, track0=26, track1=6)
    title = light_sweep(title, t, 1.45, 0.75)
    title = glow(title, 18, 0.45)
    im.alpha_composite(title, ((W - title.width) // 2, 400))
    # garisan cahaya emas di bawah tajuk
    lw = int(760 * ease((t - 1.0) / 0.8))
    if lw > 2:
        ln = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ln)
        d.rectangle(((W - lw) // 2, 556, (W + lw) // 2, 558), fill=GOLD + (230,))
        im.alpha_composite(ln.filter(ImageFilter.GaussianBlur(0.6)))
    sub = "Pengalaman Pengajaran, Pembelajaran dan Amalan Pedagogi"
    a = ease((t - 1.15) / 0.6)
    if a > 0:
        s = Image.new("RGBA", (int(tw(F_SUB, sub)) + 20, 60), (0, 0, 0, 0))
        ImageDraw.Draw(s).text((10, 4), sub, font=F_SUB, fill=GOLD_L + (255,))
        s = fade(s, a)
        im.alpha_composite(s, ((W - s.width) // 2, 584 + int(14 * (1 - a))))
    im = zoom(im, z)
    # pudar dari hitam
    if t < 0.5:
        im = Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 255)), im, smooth(t / 0.5))
    return im


# ------------------------------------------------------------------ TINDIHAN AWAL (atas video asal)
F_DESC = F("Inter-Medium", 30)
F_DESC_B = F("Inter-Bold", 30)
F_CHIP = F("Inter-Bold", 22)
F_LT_LABEL = F("Inter-SemiBold", 19)
F_LT_NAME = F("InterDisplay-Bold", 38)

DESC_T0, DESC_T1 = S + 0.9, S + 13.4          # penerangan + kata kunci (jalur atas)
NAME_T0, NAME_STEP = S + 1.6, 3.6             # pengenalan diri (kiri-tengah), 3 nama

def _wrap(text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        c = (cur + " " + w).strip()
        if tw(font, c) <= maxw: cur = c
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def desc_layer(t):
    a_in = ease((t - DESC_T0) / 0.6); a_out = 1 - ease((t - (DESC_T1 - 0.8)) / 0.8)
    a = a_in * a_out
    if a <= 0: return None
    lay = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
    # gradien gelap dari atas (tidak sampai ke paras muka)
    g = np.zeros((300, W, 4), np.uint8); g[..., 3] = (np.linspace(200, 0, 300) ** 1.0).astype(np.uint8)[:, None]
    lay.alpha_composite(Image.fromarray(g, "RGBA"))
    d = ImageDraw.Draw(lay)
    lines = _wrap(DESC, F_DESC, 1640)
    low = DESC.lower()
    # teks dengan kata kunci ditebalkan emas (muncul ikut masa)
    y = 34
    pos = 0
    hl_t = {k: DESC_T0 + 1.6 + 1.1 * i for i, k in enumerate(HIGHLIGHT)}
    for ln in lines:
        x = (W - tw(F_DESC, ln)) / 2
        i = 0
        while i < len(ln):
            hit = None
            for k in HIGHLIGHT:
                if ln.lower().startswith(k, i):
                    hit = k; break
            if hit and t >= hl_t[hit]:
                seg = ln[i:i + len(hit)]
                d.text((x, y), seg, font=F_DESC_B, fill=GOLD_L + (255,))
                x += tw(F_DESC_B, seg); i += len(hit)
            else:
                d.text((x, y), ln[i], font=F_DESC, fill=WHITE + (240,))
                x += tw(F_DESC, ln[i]); i += 1
        y += 44
    # cip kata kunci (kinetik): muncul satu demi satu
    chips = []
    for k in KEYS:
        chips.append((k, tw(F_CHIP, k) + 40))
    total = sum(c[1] for c in chips) + 18 * 3
    x = (W - total) / 2
    for i, (k, cw) in enumerate(chips):
        ti = DESC_T0 + 1.6 + 1.1 * i
        ca = ease((t - ti) / 0.45)
        if ca > 0:
            yy = y + 16 + int(16 * (1 - ca))
            d.rounded_rectangle((x, yy, x + cw, yy + 40), 20, fill=(10, 10, 10, int(170 * ca)), outline=GOLD + (int(255 * ca),), width=2)
            d.text((x + 20, yy + 8), k, font=F_CHIP, fill=GOLD_L + (int(255 * ca),))
        x += cw + 18
    return fade(lay, a)

def name_layer(t):
    for i, nm in enumerate(NAMES):
        t0 = NAME_T0 + i * NAME_STEP; t1 = t0 + NAME_STEP - 0.15
        if t0 <= t < t1:
            a_in = ease((t - t0) / 0.5); a_out = 1 - ease((t - (t1 - 0.45)) / 0.45)
            w = int(tw(F_LT_NAME, nm) + 1.5 * len(nm) + 110)
            lay = Image.new("RGBA", (w + 40, 130), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            d.rounded_rectangle((0, 0, w, 118), 10, fill=(8, 8, 8, 175))
            # garisan cahaya nipis yang tumbuh
            lw = int((w - 60) * ease((t - t0) / 0.7))
            d.rectangle((30, 46, 30 + lw, 47), fill=GOLD + (255,))
            d.text((30, 14), "PENGENALAN DIRI  ·  " + str(i + 1) + "/3", font=F_LT_LABEL, fill=GOLD_L + (255,))
            # pendedahan huruf
            nm_img = reveal_text(nm, F_LT_NAME, t, t0 + 0.15, dur=0.7, track0=8, track1=1.5, blur0=3)
            lay.alpha_composite(nm_img, (0, 30))
            lay = light_sweep(lay, t, t0 + 0.9, 0.6, 70, 70)
            return fade(lay, a_in * a_out), (70 + int(-30 * (1 - a_in)), 560)
    return None


# ------------------------------------------------------------------ TINDIHAN AKHIR + OUTRO
F_SMALL = F("Inter-SemiBold", 22)
F_LECT = F("InterDisplay-Bold", 48)
F_BMO = F("InterDisplay-Black", 92)
F_TK = F("InterDisplay-Bold", 110)
LECT_T0, LECT_T1 = E - 10.0, E - 5.2
BMO_T0, BMO_T1 = E - 5.0, E + 0.0

def card(t, t0, t1, lines):
    a_in = ease((t - t0) / 0.6); a_out = 1 - ease((t - (t1 - 0.5)) / 0.5)
    a = a_in * a_out
    if a <= 0: return None
    return a, a_in

def lecturer_layer(t):
    c = card(t, LECT_T0, LECT_T1, None)
    if not c: return None
    a, a_in = c
    lab = "PENSYARAH PEMBIMBING"
    track = 2 + 10 * (1 - ease((t - LECT_T0) / 1.2))       # animasi jarak huruf
    w = 820; h = 170
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, w, h), 12, fill=(5, 5, 5, 190), outline=GOLD + (200,), width=2)
    x = 34
    for ch in lab:
        d.text((x, 26), ch, font=F_SMALL, fill=GOLD_L + (255,)); x += tw(F_SMALL, ch) + track
    d.rectangle((34, 62, 34 + int(300 * ease((t - LECT_T0 - 0.2) / 0.8)), 63), fill=GOLD + (255,))
    nm = reveal_text(PENSYARAH, F_LECT, t, LECT_T0 + 0.3, dur=0.8, track0=10, track1=2, blur0=4)
    lay.alpha_composite(nm, (4, 64))
    lay = light_sweep(lay, t, LECT_T0 + 1.3, 0.8, 80, 90)
    return fade(lay, a), (70, 70)

def bmo_layer(t):
    c = card(t, BMO_T0, BMO_T1, None)
    if not c: return None
    a, a_in = c
    w, h = 820, 200
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, w, h), 12, fill=(5, 5, 5, 195), outline=GOLD + (200,), width=2)
    d.text((34, 22), "KELUARGA", font=F_SMALL, fill=WHITE + (235,))
    z = 1.08 - 0.08 * ease((t - BMO_T0) / 2.0)                # zum-keluar halus
    word = reveal_text("BMONETHO", F_BMO, t, BMO_T0 + 0.2, dur=0.8, color=GOLD_L, track0=24, track1=8, blur0=5)
    word = glow(word, 16, 0.8)
    if abs(z - 1) > 0.002:
        word = word.resize((int(word.width * z), int(word.height * z)), Image.BICUBIC)
    lay.alpha_composite(word, (6, 36))
    # garisan cahaya bergerak
    u = ((t - BMO_T0) * 0.45) % 1
    gx = int(34 + (w - 120) * u)
    d.rectangle((34, h - 26, w - 34, h - 25), fill=GOLD + (90,))
    d.rectangle((gx, h - 27, gx + 80, h - 24), fill=GOLD_L + (255,))
    return fade(lay, a), (70, 70)

def outro_frame(t, last_orig_frame=None):
    """t dalam masa akhir, untuk E <= t <= TOTAL (latar hitam/emas)."""
    u = t - E
    im = background(t, warm=True, icons=False)
    # dissolve dari bingkai terakhir video asal (0.5 s pertama)
    if last_orig_frame is not None and u < 0.5:
        im = Image.blend(last_orig_frame.convert("RGBA"), im, smooth(u / 0.5))
    tk = reveal_text("TERIMA KASIH", F_TK, t, E + 0.15, dur=0.6, track0=22, track1=10, blur0=6)
    tk = glow(light_sweep(tk, t, E + 0.85, 0.6), 16, 0.5)
    im.alpha_composite(tk, ((W - tk.width) // 2, (H - tk.height) // 2 - 10))
    # pudar ke hitam sepenuhnya
    k = smooth((t - (TOTAL - 0.7)) / 0.7)
    if k > 0:
        im = Image.blend(im, Image.new("RGBA", (W, H), (0, 0, 0, 255)), k)
    return im


def overlays_at(t):
    """Senarai (RGBA, (x, y)) untuk tindihan atas video asal pada masa akhir t."""
    out = []
    l = desc_layer(t)
    if l is not None: out.append((l, (0, 0)))
    n = name_layer(t)
    if n is not None: out.append(n)
    l = lecturer_layer(t)
    if l is not None: out.append(l)
    b = bmo_layer(t)
    if b is not None: out.append(b)
    return out
