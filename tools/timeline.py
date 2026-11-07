"""Bina garis masa suntingan 30:00 -> timeline.json

Sumber:  A = pdp.mp4 (kamera utama, audio utama)   S = sokongan.mp4 (kamera kedua, pegang tangan)
         G = gameplay.mp4 (skrin tablet, tiada audio)
Struktur: INTRO 8 s | SET INDUKSI | LANGKAH 1 | LANGKAH 2 | PENUTUP | OUTRO 40 s
Peraturan utama (ikut arahan): ~70% guru, ~20% murid/aktiviti, ~10% wide; tiada klip berulang;
guru shot 6-15 s dipotong pada jeda ayat; cutaway 3-6 s; montaj: kelas <=5 s, close-up <=7 s.
"""
import json, os, sys, math, random
sys.path.insert(0, os.path.dirname(__file__))
from subs_data import SUBS

W = "/home/user/work/"
random.seed(42)
TOTAL = 1800.0
INTRO, OUTRO, XF = 8.0, 40.0, 0.3
BODY = TOTAL - INTRO - OUTRO            # 1752 s selepas 3 dissolve
SRCW = {"A": (1280, 720), "S": (1280, 720), "G": (1728, 1080)}

det_pdp = {float(k): v for k, v in json.load(open(W + "det_pdp.json")).items()}
det_sok = {float(k): v for k, v in json.load(open(W + "det_sok.json")).items()}
KP, KS = sorted(det_pdp), sorted(det_sok)
sync = json.load(open(W + "sync.json"))
sok_good = json.load(open(W + "sok_good.json"))
gp = {int(k): v for k, v in json.load(open(W + "gp_clean.json")).items()}

# ------------------------------------------------------------------ penyelarasan sokongan
def sync_runs():
    runs, i = [], 0
    while i < len(sync):
        j = i
        while j + 1 < len(sync) and abs(sync[j + 1][1] - sync[i][1]) < 0.1 and sync[j + 1][0] - sync[j][0] <= 3.01:
            j += 1
        zmax = max(s[2] for s in sync[i:j + 1])
        off = sync[i][1]
        if j > i and zmax >= 6.0 and not (2820 < sync[i][0] + off < 2845):
            runs.append((sync[i][0], sync[j][0] + 8.0, off))
        i = j + 1
    return runs
RUNS = sync_runs()

def sok_at(pdp_t0, pdp_t1):
    """Klip sokongan yang selari dengan [pdp_t0, pdp_t1] dan stabil -> masa sokongan atau None."""
    for a, b, off in RUNS:
        s0, s1 = pdp_t0 - off, pdp_t1 - off
        if a <= s0 and s1 <= b:
            for g0, g1 in sok_good:
                if g0 <= s0 and s1 <= g1:
                    return s0
    return None

# ------------------------------------------------------------------ guru
def teacher_boxes(t0, t1):
    out = []
    for k in KP:
        if k < t0 or k > t1: continue
        for x1, y1, x2, y2, c in det_pdp[k]:
            h, w = y2 - y1, x2 - x1
            if y1 < 270 and y2 < 500 and h > 95 and h / max(w, 1) > 1.2 and 250 < (x1 + x2) / 2 < 1050:
                out.append((k, x1, y1, x2, y2))
    return out

def teacher_crop(t0, t1, zoom_pref):
    bx = teacher_boxes(t0, t1)
    n = sum(1 for k in KP if t0 <= k <= t1) or 1
    if len(bx) < 0.5 * n:
        return None
    # pilih guru: kotak paling hampir median kedudukan
    xs = sorted((b[1] + b[3]) / 2 for b in bx)
    mx = xs[len(xs) // 2]
    near = [b for b in bx if abs((b[1] + b[3]) / 2 - mx) < 150]
    cx = sorted((b[1] + b[3]) / 2 for b in near)
    top = sorted(b[2] for b in near)[len(near) // 2]
    hh = sorted(b[4] - b[2] for b in near)[len(near) // 2]
    spread = cx[-1] - cx[0]
    for z in ([zoom_pref, 1.45, 1.2] if zoom_pref > 1.45 else [zoom_pref, 1.2]):
        w, h = 1280 / z, 720 / z
        if spread < 0.45 * w:
            break
    c = cx[len(cx) // 2]
    x0 = min(max(c - w / 2, 0), 1280 - w)
    y0 = min(max(top - 0.16 * h, 0), 720 - h)
    return [round(x0), round(y0), round(w), round(h)]

# ------------------------------------------------------------------ penghalang kamera (orang dekat lensa)
def occluded(t0, t1, crop):
    x0, y0, w, h = crop if crop else (0, 0, 1280, 720)
    for k in KP:
        if k < t0 - 0.5 or k > t1 + 0.5: continue
        for x1, y1, x2, y2, c in det_pdp[k]:
            if (y1 < 200 and y2 > 640) or (y2 - y1) > 540:
                ov = max(0, min(x2, x0 + w) - max(x1, x0))
                if ov > 0.15 * w:
                    return True
    return False

PHASE_POOL = {"LANGKAH 1": (30, 1500), "LANGKAH 2": (1560, 2400)}

# ------------------------------------------------------------------ kesan kepala (untuk letak grafik)
def heads(src, t0, t1, crop):
    det, ks = (det_pdp, KP) if src == "A" else (det_sok, KS)
    if src == "G":
        return []
    sw, sh = SRCW[src]
    x0, y0, w, h = crop if crop else (0, 0, sw, sh)
    sx, sy = 1920 / w, 1080 / h
    out = []
    for k in ks:
        if k < t0 or k > t1: continue
        for x1, y1, x2, y2, c in det[k]:
            hb = (y2 - y1) * 0.3
            box = [(x1 - x0) * sx, (y1 - y0) * sy, (x2 - x0) * sx, (y1 + hb - y0) * sy]
            if box[2] < 0 or box[0] > 1920 or box[3] < 0 or box[1] > 1080: continue
            out.append([round(v) for v in box])
    return out

# ------------------------------------------------------------------ titik potong pada jeda ayat
SPANS = [(a, b) for a, b, _ in SUBS]
def in_speech(t):
    return any(a + 0.2 < t < b - 0.2 for a, b in SPANS)
def cut_near(t, lo, hi):
    best = None
    for d in [i * 0.1 for i in range(0, 41)]:
        for c in (t + d, t - d):
            if lo <= c <= hi and not in_speech(c):
                return round(c, 2)
    return round(min(max(t, lo), hi), 2)

# ------------------------------------------------------------------ kolam B-roll
USED = {"A": [], "S": [], "G": []}
def free(src, a, b):
    return all(b <= u0 or a >= u1 for u0, u1 in USED[src])
def use(src, a, b):
    USED[src].append((a, b))

def gp_clean(a, b):
    for s in range(int(a), int(math.ceil(b)) + 1):
        v = gp.get(s)
        if v is None or v[0] > 0 or v[2] < 12 or (len(v) > 3 and v[3]):   # muka dikesan / skrin kosong
            return False
    return True

def take_gameplay(pool, dur, prefer=None):
    lo, hi = pool
    starts = list(range(int(lo), int(hi - dur)))
    if prefer is not None:
        starts.sort(key=lambda s: abs(s - prefer))
    else:
        random.shuffle(starts)
    for s in starts:
        if free("G", s - 2, s + dur + 2) and gp_clean(s, s + dur):
            use("G", s, s + dur)
            return float(s)
    return None

def sok_unsynced_free(dur, pdp_used):
    """Klip sokongan stabil yang belum digunakan & tidak memaparkan saat yang sudah dipapar."""
    cands = []
    for g0, g1 in sok_good:
        t = g0 + 0.3
        while t + dur <= g1 - 0.2:
            if free("S", t - 1, t + dur + 1):
                ok = True
                for a, b, off in RUNS:
                    if a <= t <= b and any(u0 - 2 < t + off < u1 + 2 for u0, u1 in pdp_used):
                        ok = False
                if ok:
                    cands.append(t)
            t += 1.0
    if not cands:
        return None
    t = random.choice(cands)
    use("S", t, t + dur)
    return t

# ------------------------------------------------------------------ segmen
# ("G", fasa, pdp_mula, pdp_tamat, opsyen)  G = guru (suara asal)
# ("M", fasa, dur, opsyen)                  M = montaj (muzik, suara disenyapkan)
SEG = [
    ("G", "SET INDUKSI", 20.5, 30.0, {}),
    ("G", "SET INDUKSI", 30.0, 72.5, {"fixed": [("A", 30.0, 36.0, "wide"), ("A", 36.0, 48.0, [180, 20, 760, 428]),
                                               ("S?", 48.0, 53.0, None), ("A", 53.0, 62.0, [180, 20, 760, 428])]}),
    ("G", "SET INDUKSI", 75.5, 118.0, {"popup_at": 76.5}),
    ("M", "SET INDUKSI", 48.0, {"pdp": (120, 330), "sok": (505, 548), "gp": None, "board": True}),
    ("G", "SET INDUKSI", 320.0, 414.5, {}),
    ("G", "LANGKAH 1", 436.0, 561.5, {"broll": (0, 30)}),
    ("M", "LANGKAH 1", 18.0, {"pdp": (562, 628), "gp": (30, 200)}),
    ("G", "LANGKAH 1", 630.0, 759.0, {"broll": (200, 420)}),
    ("M", "LANGKAH 1", 36.0, {"pdp": (760, 838), "gp": (240, 700)}),
    ("G", "LANGKAH 1", 840.0, 960.0, {"broll": (700, 900)}),
    ("G", "LANGKAH 1", 988.0, 1016.0, {}),
    ("G", "LANGKAH 1", 1016.0, 1060.0, {"broll": (900, 1100)}),
    ("M", "LANGKAH 1", 36.0, {"pdp": (1060, 1105), "gp": (700, 1150)}),
    ("G", "LANGKAH 1", 1105.0, 1182.0, {}),
    ("M", "LANGKAH 1", 36.0, {"pdp": (1182, 1350), "gp": (1100, 1300)}),
    ("G", "LANGKAH 1", 1354.0, 1410.0, {"broll": (1200, 1300)}),
    ("M", "LANGKAH 1", 40.0, {"pdp": (1410, 1680), "gp": (1300, 1520)}),
    ("G", "LANGKAH 1", 1680.0, 1800.0, {}),
    ("G", "LANGKAH 2", 1946.0, 1966.0, {}),
    ("G", "LANGKAH 2", 2038.0, 2063.0, {"broll": (1560, 1700)}),
    ("G", "LANGKAH 2", 2094.0, 2235.0, {"broll": (1690, 1900)}),
    ("M", "LANGKAH 2", 44.0, {"pdp": (1800, 2030), "gp": (1700, 1910), "force_gp": [(1747.0, 13.5, "AYAT1")]}),
    ("G", "LANGKAH 2", 2248.0, 2353.0, {}),
    ("M", "LANGKAH 2", 30.0, {"pdp": (2353, 2420), "gp": (1930, 2100), "force_gp": [(1924.0, 14.0, "AYAT2")]}),
    ("G", "LANGKAH 2", 2420.0, 2460.0, {}),
    ("M", "LANGKAH 2", 30.0, {"pdp": (2460, 2608), "gp": (2100, 2400)}),
    ("G", "LANGKAH 2", 2486.0, 2546.0, {}),
    ("G", "LANGKAH 2", 2608.0, 2633.0, {}),
    ("G", "PENUTUP (REFLEKSI)", 2730.0, 2857.5, {}),
]

# ------------------------------------------------------------------ penjanaan shot
shots = []
def add(src, tin, tout, crop, phase, kind, audio, pdp_range=None, tag=None):
    shots.append(dict(src=src, tin=round(tin, 2), tout=round(tout, 2), dur=round(tout - tin, 2), crop=crop,
                      phase=phase, kind=kind, audio=audio, pdp=pdp_range, tag=tag))

pdp_used = [(s[2], s[3]) for s in SEG if s[0] == "G"]

def guru_segment(phase, a, b, opt):
    t = a
    cut_i = 0
    # bahagian tetap
    for f in opt.get("fixed", []):
        src, x0, x1, crop = f
        if src == "S?":
            st = sok_at(x0, x1)
            if st is not None and free("S", st, st + (x1 - x0)):
                use("S", st, st + x1 - x0)
                add("S", st, st + x1 - x0, None, phase, "reaksi", "A", (x0, x1)); t = x1; continue
            src = "A"; crop = "wide"
        if crop == "wide":
            add("A", x0, x1, None, phase, "wide", "A", (x0, x1))
        else:
            add("A", x0, x1, crop, phase, "guru", "A", (x0, x1))
        t = x1
    n = 0
    while t < b - 0.5:
        # shot guru
        L = random.uniform(9.0, 13.5)
        if opt.get("popup_at") and n == 0:
            L = 12.0
        end = cut_near(t + L, t + 6.0, min(t + 15.0, b))
        if b - end < 4.0:
            end = b
        z = 1.75 if n % 2 == 0 else 1.45
        crop = teacher_crop(t, end, z)
        if crop and occluded(t, end, crop):
            crop2 = teacher_crop(t, end, 2.0)
            crop = crop2 if crop2 and not occluded(t, end, crop2) else None
            if crop is None:
                pool = opt.get("broll") or PHASE_POOL.get(phase)
                g = take_gameplay(pool, end - t) if pool else None
                st = sok_at(t, end)
                if st is not None and free("S", st, st + end - t):
                    use("S", st, st + end - t); add("S", st, st + end - t, None, phase, "reaksi", "A", (t, end))
                elif g is not None:
                    add("G", g, g + end - t, None, phase, "broll", "A", (t, end))
                else:
                    add("A", t, end, None, phase, "guru-wide", "A", (t, end))
                t = end; n += 1
                continue
        if crop:
            add("A", t, end, crop, phase, "guru", "A", (t, end))
        elif not occluded(t, end, [107, 40, 1067, 600]):
            add("A", t, end, [107, 40, 1067, 600], phase, "guru-wide", "A", (t, end))
        else:
            pool = opt.get("broll") or PHASE_POOL.get(phase)
            g = take_gameplay(pool, end - t) if pool else None
            if g is not None:
                add("G", g, g + end - t, None, phase, "broll", "A", (t, end))
            else:
                add("A", t, end, [320, 0, 640, 360], phase, "guru", "A", (t, end))
        t = end
        n += 1
        if t >= b - 0.5:
            break
        if n % 2 == 1 and b - t > 12:
            continue
        # cutaway
        cl = random.uniform(3.0, 4.5)
        cend = cut_near(t + cl, t + 3.0, min(t + 6.0, b))
        if b - cend < 4.0:
            cend = b
        st = sok_at(t, cend)
        if st is not None and free("S", st - 0.5, st + cend - t + 0.5):
            use("S", st, st + cend - t)
            add("S", st, st + cend - t, None, phase, "reaksi", "A", (t, cend))
        elif opt.get("broll") and (cut_i := cut_i + 1) % 2 == 1:
            g = take_gameplay(opt["broll"], cend - t)
            if g is not None:
                add("G", g, g + cend - t, None, phase, "broll", "A", (t, cend))
            else:
                add("A", t, cend, None, phase, "wide", "A", (t, cend))
        elif not occluded(t, cend, None):
            add("A", t, cend, None, phase, "wide", "A", (t, cend))
        else:
            c2 = teacher_crop(t, cend, 1.75)
            if c2 and not occluded(t, cend, c2):
                add("A", t, cend, c2, phase, "guru", "A", (t, cend))
            else:
                pool = opt.get("broll") or PHASE_POOL.get(phase)
                g = take_gameplay(pool, cend - t) if pool else None
                if g is not None:
                    add("G", g, g + cend - t, None, phase, "broll", "A", (t, cend))
                else:
                    add("A", t, cend, [320, 0, 640, 360], phase, "guru", "A", (t, cend))
        t = cend

def montage(phase, dur, opt):
    t, i = 0.0, 0
    order = ["S", "G", "A", "S", "G", "Acu"] if opt.get("sok") or True else ["G", "A"]
    forced = list(opt.get("force_gp", []))
    pa, pb = opt["pdp"]
    apos = pa
    while t < dur - 0.5:
        if forced:
            g0, gl, tag = forced.pop(0)
            add("G", g0, g0 + gl, None, phase, "montaj", "M", tag=tag); t += gl; continue
        kind = order[i % len(order)]; i += 1
        L = min(random.uniform(4.0, 6.5), dur - t)
        if L < 2.0:
            # sambung shot terakhir
            shots[-1]["tout"] = round(shots[-1]["tout"] + L, 2); shots[-1]["dur"] = round(shots[-1]["dur"] + L, 2)
            t += L; break
        if kind == "S":
            if opt.get("sok"):
                s0, s1 = opt["sok"]
                st = None
                for g0, g1 in sok_good:
                    x = max(g0 + 0.3, s0)
                    while x + L <= min(g1 - 0.2, s1):
                        if free("S", x - 0.5, x + L + 0.5):
                            st = x; break
                        x += 1.0
                    if st is not None: break
                if st is None:
                    st = sok_unsynced_free(L, pdp_used)
                else:
                    use("S", st, st + L)
            else:
                st = sok_unsynced_free(L, pdp_used)
            if st is not None:
                add("S", st, st + L, None, phase, "montaj", "M"); t += L; continue
            kind = "G"
        if kind == "G" and opt.get("gp"):
            L = min(L, 5.5)
            g = take_gameplay(opt["gp"], L)
            if g is not None:
                add("G", g, g + L, None, phase, "montaj", "M"); t += L; continue
        # kamera utama: wide <=5 s atau close-up aktiviti
        L = min(L, 5.0)
        step = (pb - pa) / max(1, dur / 5.0)
        x = apos
        while x + L < pb and (not free("A", x, x + L) or occluded(x, x + L, None)):
            x += 1
        if x + L >= pb:
            x = pa
            while x + L < pb and (not free("A", x, x + L) or occluded(x, x + L, None)):
                x += 1
        apos = x + max(step, L + 1)
        if kind == "Acu":
            crop = [560, 60, 640, 360] if opt.get("board") else [200, 300, 760, 428]
            use("A", x, x + L); add("A", x, x + L, crop, phase, "montaj", "M")
        else:
            use("A", x, x + L); add("A", x, x + L, None, phase, "montaj", "M")
        t += L

for s in SEG:
    if s[0] == "G":
        use("A", s[2], s[3])
RESERVED = []
for s in SEG:
    if s[0] == "M":
        for g0, gl, tag in s[3].get("force_gp", []):
            use("G", g0 - 1, g0 + gl + 1); RESERVED.append((g0 - 1, g0 + gl + 1))
for s in SEG:
    if s[0] == "G":
        guru_segment(s[1], s[2], s[3], s[4])
    else:
        montage(s[1], s[2], s[3])

# ------------------------------------------------------------------ laraskan kepada 30:00 tepat
def body_len():
    return sum(x["dur"] for x in shots) - 3 * XF
diff = BODY - body_len()
mshots = [x for x in shots if x["kind"] == "montaj" and x["src"] != "G" and x.get("tag") is None]
# agih beza ke shot montaj (+/- maks 1.5 s setiap satu)
i = 0
while abs(diff) > 0.005 and i < 10000:
    x = mshots[i % len(mshots)]
    d = max(-1.0, min(1.0, diff))
    if d > 0 and x["dur"] + d > 6.9: d = max(0, 6.9 - x["dur"])
    if d < 0 and x["dur"] + d < 2.5: d = min(0, 2.5 - x["dur"])
    x["tout"] = round(x["tout"] + d, 3); x["dur"] = round(x["tout"] - x["tin"], 3)
    diff = BODY - body_len(); i += 1

# ------------------------------------------------------------------ masa keluaran
t = INTRO
prev_phase = None
for x in shots:
    if prev_phase is not None and x["phase"] != prev_phase:
        t -= XF
        x["xfade_in"] = True
    x["out_start"] = round(t, 3)
    t += x["dur"]
    x["out_end"] = round(t, 3)
    prev_phase = x["phase"]
    x["heads"] = heads(x["src"], x["tin"], x["tout"], x["crop"])
body_end = t

json.dump(dict(shots=shots, body_end=body_end, intro=INTRO, outro=OUTRO, total=TOTAL, runs=RUNS),
          open(W + "timeline.json", "w"), indent=1)

# ringkasan
from collections import Counter, defaultdict
c = defaultdict(float)
for x in shots:
    c[x["kind"]] += x["dur"]
tot = sum(c.values())
print("shot", len(shots), "body", round(body_end, 3), "jumlah", round(body_end + OUTRO, 3))
print({k: f"{v:.0f}s {100 * v / tot:.0f}%" for k, v in c.items()})
ph = defaultdict(float)
for x in shots: ph[x["phase"]] += x["dur"]
print({k: round(v) for k, v in ph.items()})
