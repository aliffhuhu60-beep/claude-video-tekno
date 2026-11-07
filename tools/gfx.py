"""Grafik overlay (PNG RGBA 1920x1080) untuk video pengajaran mikro.

Palet: hijau hutan #0B3B2C, emas #D4AF37, hijau lembut #6EB062, putih.
Fon: Inter / Inter Display (SemiBold teks, ExtraBold kata kunci).
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
FOREST = (11, 59, 44)
GOLD = (212, 175, 55)
SOFT = (110, 176, 98)
WHITE = (255, 255, 255)
FD = "/usr/share/fonts/opentype/inter/"


def font(name, size):
    return ImageFont.truetype(FD + name + ".otf", size)


SEMI = lambda s: font("Inter-SemiBold", s)
BOLD = lambda s: font("Inter-Bold", s)
XB = lambda s: font("InterDisplay-ExtraBold", s)
DSEMI = lambda s: font("InterDisplay-SemiBold", s)


def blank():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def rrect(d, box, r, fill, outline=None, width=0):
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)


def text_w(d, s, f):
    return d.textlength(s, font=f)


# ---------------------------------------------------------------- tajuk
def title_card(lines_top, title, subtitle, info_lines):
    im = Image.new("RGBA", (W, H), FOREST + (255,))
    d = ImageDraw.Draw(im)
    # corak halus: jalur emas nipis
    d.rectangle((160, 300, 168, 780), fill=GOLD)
    y = 300
    f = SEMI(30)
    for s in lines_top:
        d.text((210, y), s, font=f, fill=SOFT)
        y += 44
    y += 20
    for s in title:
        d.text((206, y), s, font=XB(96), fill=WHITE)
        y += 108
    d.text((210, y + 6), subtitle, font=DSEMI(44), fill=GOLD)
    y += 90
    for s in info_lines:
        d.text((210, y), s, font=SEMI(30), fill=(220, 230, 225))
        y += 42
    return im


# ---------------------------------------------------------------- kad fasa
def phase_card(phase, activity):
    im = blank()
    d = ImageDraw.Draw(im)
    x, y = 64, 56
    fl, fp, fa = BOLD(22), XB(46), SEMI(26)
    w = max(text_w(d, phase, fp), text_w(d, activity, fa)) + 76
    rrect(d, (x, y, x + w, y + 168), 18, FOREST + (235,))
    d.rectangle((x, y + 18, x + 8, y + 150), fill=GOLD)
    d.text((x + 36, y + 20), "FASA PdP", font=fl, fill=GOLD)
    d.text((x + 34, y + 50), phase, font=fp, fill=WHITE)
    d.text((x + 36, y + 114), activity, font=fa, fill=(215, 235, 210))
    return im


# ---------------------------------------------------------------- pop-up guru
def teacher_popup(name, role, minute_phase, shine=0.0):
    """Bawah-kiri, ~45% lebar, di atas zon sari kata."""
    im = blank()
    d = ImageDraw.Draw(im)
    x0, y0, w, h = 64, 640, 860, 200
    rrect(d, (x0, y0, x0 + w, y0 + h), 20, FOREST + (240,))
    d.rectangle((x0, y0 + 20, x0 + 10, y0 + h - 20), fill=GOLD)
    d.text((x0 + 40, y0 + 22), "GURU SEDANG MENGAJAR", font=BOLD(24), fill=GOLD)
    d.text((x0 + 38, y0 + 56), name, font=XB(50), fill=WHITE)
    d.text((x0 + 40, y0 + 120), role, font=SEMI(28), fill=(220, 235, 225))
    d.text((x0 + 40, y0 + 158), minute_phase, font=SEMI(24), fill=SOFT)
    if shine > 0:  # kilauan ringan menyapu panel
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sx = x0 - 200 + int((w + 400) * shine)
        sd.polygon([(sx, y0), (sx + 70, y0), (sx + 10, y0 + h), (sx - 60, y0 + h)],
                   fill=(255, 255, 255, 60))
        mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mask).rounded_rectangle((x0, y0, x0 + w, y0 + h), 20, fill=255)
        im.paste(Image.alpha_composite(im, sh), (0, 0), mask)
    return im


# ---------------------------------------------------------------- panel langkah
def steps_panel(title, steps, n_visible=None):
    im = blank()
    d = ImageDraw.Draw(im)
    n_visible = len(steps) if n_visible is None else n_visible
    x0, w = 1240, 620
    rows = []
    for s in steps:
        rows.append(wrap(d, s, SEMI(28), w - 130))
    h = 110 + sum(36 * len(r) + 30 for r in rows)
    y0 = 120
    rrect(d, (x0, y0, x0 + w, y0 + h), 22, FOREST + (235,))
    d.text((x0 + 34, y0 + 28), title, font=XB(34), fill=GOLD)
    y = y0 + 92
    for i, r in enumerate(rows):
        if i < n_visible:
            d.ellipse((x0 + 34, y, x0 + 80, y + 46), fill=GOLD)
            num = str(i + 1)
            d.text((x0 + 57 - text_w(d, num, XB(28)) / 2, y + 6), num, font=XB(28), fill=FOREST)
            for j, line in enumerate(r):
                d.text((x0 + 100, y + 4 + j * 36), line, font=SEMI(28), fill=WHITE)
        y += 36 * len(r) + 30
    return im


def wrap(d, s, f, maxw):
    words, lines, cur = s.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if text_w(d, t, f) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    lines.append(cur)
    return lines


# ---------------------------------------------------------------- panel ayat
def draw_rich(d, x, y, parts, size):
    """parts: senarai (teks, gaya) gaya: 'n' biasa, 'v' kata kerja (tebal, berwarna)."""
    for s, st, col in parts:
        f = XB(size) if st == "v" else SEMI(size)
        d.text((x, y), s, font=f, fill=col)
        x += text_w(d, s, f)
    return x


def sentence_panel(items, pos=(1180, 120), width=700, n_visible=None):
    """items: [(label, warna_chip, parts)] ; parts seperti draw_rich."""
    im = blank()
    d = ImageDraw.Draw(im)
    n_visible = len(items) if n_visible is None else n_visible
    x0, y0 = pos
    h = 40 + 130 * len(items)
    rrect(d, (x0, y0, x0 + width, y0 + h), 22, FOREST + (235,))
    y = y0 + 30
    for i, (label, chip, parts) in enumerate(items):
        if i < n_visible:
            cw = text_w(d, label, BOLD(22)) + 36
            rrect(d, (x0 + 30, y, x0 + 30 + cw, y + 38), 19, chip)
            d.text((x0 + 48, y + 6), label, font=BOLD(22), fill=FOREST if chip == GOLD else WHITE)
            draw_rich(d, x0 + 30, y + 52, parts, 34)
        y += 130
    return im


# ---------------------------------------------------------------- sari kata
def subtitle(lines):
    """lines: senarai baris; setiap baris senarai (teks, warna, tebal?)."""
    im = blank()
    d = ImageDraw.Draw(im)
    size = 40
    widths = [sum(text_w(d, s, XB(size) if b else SEMI(size)) for s, c, b in ln) for ln in lines]
    bw = max(widths) + 64
    bh = 24 + 54 * len(lines)
    x0 = (W - bw) / 2
    y0 = H - 70 - bh
    rrect(d, (x0, y0, x0 + bw, y0 + bh), 14, FOREST + (200,))
    y = y0 + 14
    for ln, lw in zip(lines, widths):
        x = (W - lw) / 2
        for s, c, b in ln:
            f = XB(size) if b else SEMI(size)
            d.text((x, y), s, font=f, fill=c)
            x += text_w(d, s, f)
        y += 54
    return im


# ---------------------------------------------------------------- penghargaan
def credits_card(bg, blocks):
    """bg: Image RGB 1920x1080 (bingkai kelas) -> dikaburkan + hijau gelap."""
    b = bg.convert("RGB").resize((W, H)).filter(ImageFilter.GaussianBlur(18))
    ov = Image.new("RGB", (W, H), FOREST)
    im = Image.blend(b, ov, 0.72).convert("RGBA")
    d = ImageDraw.Draw(im)
    total = sum(70 + 52 * len(v) for k, v in blocks)
    y = (H - total) / 2
    for head, lines in blocks:
        d.text(((W - text_w(d, head, BOLD(28))) / 2, y), head, font=BOLD(28), fill=GOLD)
        y += 52
        for s in lines:
            d.text(((W - text_w(d, s, DSEMI(40))) / 2, y), s, font=DSEMI(40), fill=WHITE)
            y += 52
        y += 18
    return im


# ---------------------------------------------------------------- panel titik utama
def keypoint_panel(title, rows, width=660, n_visible=None):
    """rows: [(label_chip, warna_chip, [baris teks...])] -> panel tanpa kedudukan (saiz rapat)."""
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    body = []
    for label, chip, lines in rows:
        wl = []
        for ln in lines:
            wl += wrap(tmp, ln, SEMI(27), width - 70)
        body.append((label, chip, wl))
    h = 96 + sum(56 + 36 * len(wl) + 18 for _, _, wl in body)
    im = Image.new("RGBA", (width, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rrect(d, (0, 0, width, h), 22, FOREST + (238,))
    d.rectangle((0, 22, 8, h - 22), fill=GOLD)
    d.text((34, 26), title, font=XB(32), fill=GOLD)
    y = 88
    n_visible = len(body) if n_visible is None else n_visible
    for i, (label, chip, wl) in enumerate(body):
        if i < n_visible:
            cw = text_w(d, label, BOLD(22)) + 36
            rrect(d, (34, y, 34 + cw, y + 38), 19, chip)
            d.text((52, y + 6), label, font=BOLD(22), fill=FOREST if chip == GOLD else WHITE)
            for j, ln in enumerate(wl):
                d.text((36, y + 50 + j * 36), ln, font=SEMI(27), fill=WHITE)
        y += 56 + 36 * len(wl) + 18
    return im


def steps_block(title, steps, n_visible=None, width=640):
    """Panel langkah bernombor (saiz rapat, tanpa kedudukan)."""
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    rows = [wrap(tmp, s, SEMI(28), width - 130) for s in steps]
    th = wrap(tmp, title, XB(32), width - 60)
    h = 50 + 42 * len(th) + sum(36 * len(r) + 30 for r in rows) + 10
    im = Image.new("RGBA", (width, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rrect(d, (0, 0, width, h), 22, FOREST + (238,))
    d.rectangle((0, 22, 8, h - 22), fill=GOLD)
    for j, ln in enumerate(th):
        d.text((34, 26 + j * 42), ln, font=XB(32), fill=GOLD)
    y = 40 + 42 * len(th) + 6
    n_visible = len(steps) if n_visible is None else n_visible
    for i, r in enumerate(rows):
        if i < n_visible:
            d.ellipse((34, y, 80, y + 46), fill=GOLD)
            num = str(i + 1)
            d.text((57 - text_w(d, num, XB(28)) / 2, y + 6), num, font=XB(28), fill=FOREST)
            for j, line in enumerate(r):
                d.text((100, y + 4 + j * 36), line, font=SEMI(28), fill=WHITE)
        y += 36 * len(r) + 30
    return im


def sentence_block(items, width=820, n_visible=None):
    """Panel ayat (saiz rapat). items: [(label, chip, teks)] ; kata kerja meN-/di- ditebalkan."""
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    def parts(s):
        out = []
        for w in s.split():
            core = w.strip(".,!?").lower()
            verb_a = core.startswith(("men", "mem", "meng", "meny", "me")) and len(core) > 4 and core not in ("menunjukkan",)
            verb_p = core.startswith("di") and len(core) > 4
            if verb_a:
                out.append((w + " ", "v", GOLD))
            elif verb_p:
                out.append((w + " ", "v", SOFT))
            elif core == "oleh":
                out.append((w + " ", "v", SOFT))
            else:
                out.append((w + " ", "n", WHITE))
        return out
    size = 36
    widths = [sum(text_w(tmp, s, XB(size) if st == "v" else SEMI(size)) for s, st, c in parts(t)) for _, _, t in items]
    width = int(max(width, max(widths) + 70))
    h = 30 + 128 * len(items)
    im = Image.new("RGBA", (width, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rrect(d, (0, 0, width, h), 22, FOREST + (238,))
    y = 26
    n_visible = len(items) if n_visible is None else n_visible
    for i, (label, chip, text) in enumerate(items):
        if i < n_visible:
            cw = text_w(d, label, BOLD(22)) + 36
            rrect(d, (30, y, 30 + cw, y + 38), 19, chip)
            d.text((48, y + 6), label, font=BOLD(22), fill=FOREST if chip == GOLD else WHITE)
            draw_rich(d, 32, y + 50, parts(text), size)
        y += 128
    return im


def phase_block(phase, activity):
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    fl, fp, fa = BOLD(22), XB(46), SEMI(26)
    w = int(max(text_w(tmp, phase, fp), text_w(tmp, activity, fa)) + 76)
    im = Image.new("RGBA", (w, 168), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rrect(d, (0, 0, w, 168), 18, FOREST + (238,))
    d.rectangle((0, 18, 8, 150), fill=GOLD)
    d.text((36, 20), "FASA PdP", font=fl, fill=GOLD)
    d.text((34, 50), phase, font=fp, fill=WHITE)
    d.text((36, 114), activity, font=fa, fill=(215, 235, 210))
    return im


def popup_block(name, role, minute_phase, shine=0.0):
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    w = int(max(820, text_w(tmp, name, XB(36)) + 80)); h = 180
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rrect(d, (0, 0, w, h), 20, FOREST + (242,))
    d.rectangle((0, 20, 10, h - 20), fill=GOLD)
    d.text((40, 20), "GURU SEDANG MENGAJAR", font=BOLD(24), fill=GOLD)
    d.text((38, 54), name, font=XB(36), fill=WHITE)
    d.text((40, 104), role, font=SEMI(26), fill=(220, 235, 225))
    d.text((40, 140), minute_phase, font=SEMI(23), fill=SOFT)
    if shine > 0:
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sx = -200 + int((w + 400) * shine)
        sd.polygon([(sx, 0), (sx + 70, 0), (sx + 10, h), (sx - 60, h)], fill=(255, 255, 255, 70))
        mask = im.getchannel("A")
        im2 = Image.alpha_composite(im, sh)
        im2.putalpha(mask)
        im = im2
    return im
