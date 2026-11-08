"""Kesan selang sari kata CapCut: banding video bersari kata dengan video tanpa sari kata (bingkai demi bingkai).
Keluaran: JSON [[mula, tamat], ...] (saat video asal)."""
import subprocess, numpy as np, json, sys
A, B, OUT = sys.argv[1:4]
w, h = 480, 270
y0, y1 = int(h * 0.62), int(h * 0.97)          # zon sari kata bawah
def reader(p, extra):
    return subprocess.Popen(["ffmpeg", "-v", "error", "-i", p, "-vf", f"{extra}scale={w}:{h},format=gray", "-f", "rawvideo", "-"],
                            stdout=subprocess.PIPE)
ra, rb = reader(A, "fps=30,"), reader(B, "")
n = w * h
masks, i = [], 0
prev = None
segs = []; cur = None
while True:
    a = ra.stdout.read(n); b = rb.stdout.read(n)
    if len(a) < n or len(b) < n: break
    fa = np.frombuffer(a, np.uint8).reshape(h, w)[y0:y1].astype(np.int16)
    fb = np.frombuffer(b, np.uint8).reshape(h, w)[y0:y1].astype(np.int16)
    m = np.abs(fa - fb) > 40
    on = m.sum() > 60
    t = i / 30
    if on:
        if cur is None:
            cur = [t, t, m]
        else:
            inter = (m & cur[2]).sum(); uni = (m | cur[2]).sum()
            if uni and inter / uni < 0.45:        # teks bertukar
                segs.append([cur[0], t]); cur = [t, t, m]
            else:
                cur[1] = t; cur[2] = cur[2] | m if (t - cur[0]) < 0.3 else cur[2]
    elif cur is not None:
        segs.append([cur[0], t]); cur = None
    i += 1
if cur is not None: segs.append([cur[0], i / 30])
segs = [[round(a, 3), round(b, 3)] for a, b in segs if b - a >= 0.2]
json.dump(segs, open(OUT, "w")); print(len(segs), "selang; bingkai", i)
