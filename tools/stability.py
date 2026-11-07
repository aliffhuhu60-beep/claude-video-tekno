"""Skor ketajaman & gerakan kamera setiap 0.5 s -> JSON [t, sharp, motion]."""
import sys, json, cv2, numpy as np
cap = cv2.VideoCapture(sys.argv[1]); fps = cap.get(cv2.CAP_PROP_FPS)
step = int(fps / 2); prev = None; out = []; i = 0
while True:
    ok = cap.grab()
    if not ok: break
    if i % step == 0:
        _, f = cap.retrieve(); g = cv2.cvtColor(cv2.resize(f, (320, 180)), cv2.COLOR_BGR2GRAY)
        sharp = cv2.Laplacian(g, cv2.CV_64F).var()
        mot = 0.0
        if prev is not None:
            fl = cv2.calcOpticalFlowFarneback(prev, g, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            mot = float(np.median(np.linalg.norm(fl, axis=2)))
        out.append([round(i / fps, 2), round(sharp, 1), round(mot, 2)]); prev = g
    i += 1
json.dump(out, open(sys.argv[2], 'w'))
