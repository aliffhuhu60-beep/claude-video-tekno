"""Selaras audio video sokongan dengan kamera utama, tetingkap demi tetingkap.
Keluaran: senarai (t_sok, offset) dengan offset = t_pdp - t_sok."""
import sys, wave, json, numpy as np
def load(p):
    w = wave.open(p); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return a
def feat(a, sr=16000, hop=160):
    n = len(a) // hop
    fr = a[:n * hop].reshape(n, hop)
    sp = np.abs(np.fft.rfft(fr * np.hanning(hop), axis=1))
    bands = [(2, 8), (8, 20), (20, 40), (40, 80)]
    f = np.stack([np.log(sp[:, a_:b].sum(1) + 1e-4) for a_, b in bands], 1)
    f = np.diff(f, axis=0, prepend=f[:1])          # fluks (onset)
    return (f - f.mean(0)) / (f.std(0) + 1e-6)
A = feat(load(sys.argv[1])); B = feat(load(sys.argv[2]))   # A = sokongan, B = pdp
win, stepw = 800, 300     # 8 s, langkah 3 s
nfft = 1 << int(np.ceil(np.log2(len(B) + win)))
FB = np.fft.rfft(B, nfft, axis=0)
out = []
for s in range(0, len(A) - win, stepw):
    seg = A[s:s + win]
    if np.abs(seg).mean() < 0.3: continue
    FS = np.fft.rfft(seg[::-1], nfft, axis=0)
    c = np.fft.irfft(FB * FS, nfft, axis=0).sum(1)[win - 1:win - 1 + len(B) - win]
    k = int(np.argmax(c)); z = (c[k] - c.mean()) / (c.std() + 1e-9)
    out.append([s / 100, round(k / 100 - s / 100, 2), round(float(z), 1)])
json.dump(out, open(sys.argv[3], 'w'))
for o in out: print(*o)
