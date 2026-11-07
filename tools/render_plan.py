"""Daripada timeline.json -> overlays.json (grafik + kedudukan anti-muka), subs.ass, subs.srt.

Semua kandungan panel disalin daripada rakaman / papan putih / slaid 'Cara Bermain' (PDF).
"""
import json, os, sys, re
sys.path.insert(0, os.path.dirname(__file__))
from subs_data import SUBS, KEY
import gfx

W = "/home/user/work/"
TL = json.load(open(W + "timeline.json"))
SH = TL["shots"]
NAMA = "MOHAMAD ALIFF BIN AHMAD SHAHABUDDIN"
PERANAN = "Guru Pelatih · Opsyen Bahasa Melayu"

def p2o(p):
    for x in SH:
        if x.get("pdp") and x["pdp"][0] <= p < x["pdp"][1]:
            return x["out_start"] + (p - x["pdp"][0])
    return None

def tag_shot(tag):
    for x in SH:
        if x.get("tag") == tag:
            return x
def phase_start(ph):
    for x in SH:
        if x["phase"] == ph:
            return x["out_start"] + (0.35 if x.get("xfade_in") else 0.3)

def heads_between(t0, t1):
    hb = []
    for x in SH:
        if x["out_end"] > t0 and x["out_start"] < t1:
            hb += x["heads"]
    return hb

def overlap(box, heads):
    x0, y0, x1, y1 = box
    a = 0
    for h in heads:
        ix = max(0, min(x1, h[2]) - max(x0, h[0])); iy = max(0, min(y1, h[3]) - max(y0, h[1]))
        a += ix * iy
    return a

def place(size, t0, t1, zones):
    w, h = size
    hb = heads_between(t0, t1)
    best = None
    for zi, (zx, zy) in enumerate(zones):
        x = zx if zx >= 0 else 1920 + zx - w
        y = zy
        sc = overlap((x - 20, y - 20, x + w + 20, y + h + 20), hb) + zi * 50   # keutamaan susunan zon
        if best is None or sc < best[0]:
            best = (sc, x, y)
    return best[1], best[2], best[0]

TOPZ = [(60, 64), (-60, 64), (60, 300), (-60, 300)]
RIGHTZ = [(-60, 64), (-60, 260), (60, 64), (60, 260)]

OV = []
def ov(kind, t0, dur, spec, zones):
    if t0 is None:
        print("LANGKAU", kind); return
    blk = build(kind, spec, full=True)
    x, y, sc = place(blk.size, t0, t0 + dur, zones)
    OV.append(dict(kind=kind, t0=round(t0, 3), dur=dur, spec=spec, x=x, y=y, w=blk.size[0], h=blk.size[1], clash=sc))

def _tup(v):
    if isinstance(v, list):
        if len(v) in (3, 4) and all(isinstance(i, int) for i in v):
            return tuple(v)
        return [_tup(i) for i in v]
    if isinstance(v, tuple):
        return tuple(_tup(i) for i in v)
    if isinstance(v, dict):
        return {k: _tup(i) for k, i in v.items()}
    return v

def build(kind, spec, full=True, n=None, shine=0.0):
    spec = _tup(spec)
    if kind == "phase":
        return gfx.phase_block(*spec)
    if kind == "popup":
        return gfx.popup_block(*spec, shine=shine)
    if kind == "steps":
        return gfx.steps_block(spec[0], spec[1:], n_visible=None if full else n)
    if kind == "key":
        return gfx.keypoint_panel(spec[0], spec[1], n_visible=None if full else n)
    if kind == "ayat":
        return gfx.sentence_block(spec["items"], width=spec.get("width", 600), n_visible=None if full else n)

G, S = gfx.GOLD, gfx.SOFT
# ---------------------------------------------------------------- fasa
ov("phase", phase_start("SET INDUKSI"), 4.0, ("SET INDUKSI", "Tayangan video & soal jawab ciri ayat aktif dan pasif"), TOPZ)
ov("phase", phase_start("LANGKAH 1"), 4.0, ("LANGKAH 1", "Misi Penyelamat Ayat: baiki 3 jenis kesalahan ayat"), TOPZ)
ov("phase", phase_start("LANGKAH 2"), 4.0, ("LANGKAH 2", "Ekspedisi Ayat Aktif & Pasif: bina ayat di stesen"), TOPZ)
ov("phase", phase_start("PENUTUP (REFLEKSI)"), 4.0, ("PENUTUP (REFLEKSI)", "Refleksi & murid membina ayat sendiri"), TOPZ)
# ---------------------------------------------------------------- pop-up guru (close-up pertama)
t_pop = p2o(76.5)
mm = int(76.5 // 60); ss = int(76.5 % 60)
ov("popup", t_pop, 6.8, (NAMA, PERANAN, f"Mengajar minit {mm:02d}:{ss:02d} · Fasa: Set Induksi"), [(64, 650), (-64, 650)])
# ---------------------------------------------------------------- panel ayat (video set induksi)
ov("ayat", p2o(44.0), 14.0, {"items": [("AYAT AKTIF", G, "Ali menanam pokok."), ("AYAT PASIF", S, "Pokok ditanam oleh Ali.")],
                              "second_at": 51.0 - 44.0, "width": 560}, [(-60, 120), (60, 120), (-60, 330)])
# ---------------------------------------------------------------- titik utama: ciri
ov("key", p2o(340.5), 13.0, ("TITIK UTAMA · CIRI AYAT", [
    ("AYAT AKTIF", G, ["Subjek ialah PELAKU (yang membuat).", "Pelaku + kata kerja meN- + penerima. Tiada perkataan \"oleh\"."]),
    ("AYAT PASIF", S, ["Subjek ialah PENERIMA (yang dibuat).", "Penerima + kata kerja di- + oleh + pelaku."])]), RIGHTZ)
ov("steps", p2o(376.0), 12.0, ["OBJEKTIF PdP",
    "Menjawab 5 soalan bagi 3 jenis kesalahan ayat dengan betul",
    "Membina sekurang-kurangnya 2 ayat aktif dan pasif berdasarkan situasi di stesen Minecraft Education"], RIGHTZ)
# ---------------------------------------------------------------- langkah 1
ov("steps", p2o(510.5), 11.0, ["BAHAGIAN A · MISI PENYELAMAT AYAT", "Ayat Tanpa Subjek", "Ayat Tidak Lengkap", "Bahasa Rojak"], RIGHTZ)
ov("key", p2o(685.5), 12.0, ("JENIS 1 · AYAT TANPA SUBJEK", [
    ("KESALAHAN", G, ["Ayat dimulakan dengan kata seperti Kepada, Bagi, Dalam, Di, Daripada, Untuk."]),
    ("CARA MENJAWAB", S, ["Baca soalan, pijak blok warna jawapan: Oren = A, Biru muda = B, Magenta = C."])]), RIGHTZ)
ov("steps", p2o(862.5), 12.0, ["JENIS 2 · AYAT TIDAK LENGKAP",
    "Buka PETI 1 dan ambil satu kepingan (subjek)", "Buka PETI 2 dan ambil satu kepingan (predikat)",
    "Letak dalam BINGKAI 1 dan BINGKAI 2"], RIGHTZ)
ov("steps", p2o(1367.0), 11.0, ["JENIS 3 · BAHASA ROJAK", "Baca soalan dan pilihan jawapan",
    "Lompat (Space) melalui batu ke platform jawapan A, B atau C"], RIGHTZ)
# ---------------------------------------------------------------- langkah 2
ov("steps", p2o(2040.0), 12.0, ["CARA MENJAWAB DI STESEN", "Perhatikan situasi: siapa membuat apa?",
    "Pilih podium: biru = aktif, tembaga = pasif", "Taip ayat lengkap, kemudian hantar",
    "Baca keputusan: betul +100, salah −50"], RIGHTZ)
a1 = tag_shot("AYAT1")
ov("ayat", a1["out_start"] + 6.0 if a1 else None, 7.0, {"items": [("AYAT AKTIF · JAWAPAN MURID", G, "Pak Tani sedang menanam padi")],
                                                          "width": 560}, [(60, 64), (-60, 64)])
a2 = tag_shot("AYAT2")
ov("ayat", a2["out_start"] if a2 else None, 14.0, {"items": [("AYAT AKTIF · AYAT DIBERI", G, "Kucing itu mengejar tikus di dapur."),
                                                             ("AYAT PASIF · JAWAPAN MURID", S, "Tikus dikejar oleh kucing di dapur.")],
                                                   "second_at": 12.0, "width": 560}, [(60, 64)])
ov("key", p2o(2424.0), 13.0, ("INGAT · PELAKU SAYA / KAMI", [
    ("AYAT PASIF", S, ["Pelaku saya / kami: Kelas itu kami bersihkan."]),
    ("SALAH", (176, 70, 60), ["Kereta itu dibasuh oleh saya."]),
    ("BETUL", G, ["Kereta itu saya basuh."])]), RIGHTZ)

json.dump(OV, open(W + "overlays.json", "w"), indent=1)
for o in OV:
    print(f"{o['t0']:8.2f} {o['kind']:6s} x={o['x']:5d} y={o['y']:4d} {o['w']}x{o['h']} bertindih={o['clash']}")

# ---------------------------------------------------------------- sari kata
def colorize(text):
    keys = sorted(KEY, key=lambda k: -len(k[0]))
    col = {"gold": r"{\b1\c&H37AFD4&}", "green": r"{\b1\c&H62B06E&}"}
    out, i = "", 0
    while i < len(text):
        for k, c in keys:
            if text.startswith(k, i) and (i == 0 or not text[i - 1].isalnum()):
                out += col[c] + k + r"{\b0\c&HFFFFFF&}"
                i += len(k)
                break
        else:
            out += text[i]; i += 1
    return out

def wrap2(text, n=50):
    if len(text) <= n:
        return [text]
    words = text.split(); best = None
    for k in range(1, len(words)):
        a, b = " ".join(words[:k]), " ".join(words[k:])
        sc = max(len(a), len(b))
        if best is None or sc < best[0]:
            best = (sc, a, b)
    return [best[1], best[2]]

def split_long(a, b, text, n=100):
    if len(text) <= n:
        return [(a, b, text)]
    parts = re.split(r"(?<=[,.?!])\s+", text)
    if len(parts) == 1:
        words = text.split(); h = len(words) // 2
        parts = [" ".join(words[:h]), " ".join(words[h:])]
    # gabung ke dua bahagian seimbang
    best = None
    for k in range(1, len(parts)):
        x, y = " ".join(parts[:k]), " ".join(parts[k:])
        sc = max(len(x), len(y)) + (1000 if min(len(x), len(y)) < 25 else 0)
        if best is None or sc < best[0]:
            best = (sc, x, y)
    x, y = best[1], best[2]
    m = a + (b - a) * len(x) / (len(x) + len(y))
    return split_long(a, m, x, n) + split_long(m, b, y, n)

items = []
for a, b, text in SUBS:
    for a2_, b2_, t in split_long(a, b, text):
        o = p2o(a2_ + 0.05)
        if o is None:
            continue
        ob = p2o(min(b2_, a2_ + 7) - 0.05)
        # tempoh bacaan
        rd = min(7.0, 1.2 + 0.075 * len(t))
        end = max(o + rd, ob if ob else o + rd)
        items.append([o, end, t])
items.sort()
for i in range(len(items) - 1):
    if items[i][1] > items[i + 1][0] - 0.05:
        items[i][1] = items[i + 1][0] - 0.05
# jangan melepasi hujung segmen guru
def seg_end(t):
    for x in SH:
        if x["out_start"] <= t < x["out_end"]:
            j = SH.index(x)
            while j + 1 < len(SH) and SH[j + 1]["audio"] == "A" and abs(SH[j + 1]["out_start"] - SH[j]["out_end"]) < 0.01:
                j += 1
            return SH[j]["out_end"]
    return t + 7
for it in items:
    it[1] = min(it[1], seg_end(it[0]) - 0.05)

def ts(t, ass=True):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}" if ass else f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}"

ass = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1920", "PlayResY: 1080", "WrapStyle: 2", "ScaledBorderAndShadow: yes", "",
       "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: Sub,Inter SemiBold,44,&H00FFFFFF,&H00FFFFFF,&H3A2C3B0B,&H3A2C3B0B,0,0,0,0,100,100,0,0,3,14,0,2,120,120,64,1",
       "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
srt = []
for i, (a, b, t) in enumerate(items):
    lines = wrap2(t)
    ass.append(f"Dialogue: 0,{ts(a)},{ts(b)},Sub,,0,0,0,,{(chr(92) + 'N').join(colorize(l) for l in lines)}")
    srt += [str(i + 1), f"{ts(a, False)} --> {ts(b, False)}", "\n".join(lines), ""]
open(W + "subs.ass", "w").write("\n".join(ass) + "\n")
open(W + "subs.srt", "w").write("\n".join(srt))
print("sari kata", len(items))
