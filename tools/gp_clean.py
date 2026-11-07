"""Tanda saat gameplay yang 'bersih' (tiada muka sebenar dalam kawasan potongan 1440x810)."""
import sys, json, cv2
from ultralytics import YOLO
m = YOLO('/home/user/work/yolov8n.pt')
cap = cv2.VideoCapture(sys.argv[1]); fps = cap.get(cv2.CAP_PROP_FPS)
res = {}; i = 0; step = int(round(fps))
while True:
    ok = cap.grab()
    if not ok: break
    if i % step == 0:
        _, f = cap.retrieve(); f = f[0:810, 0:1440]
        r = m(f, imgsz=640, conf=0.3, classes=[0], verbose=False)[0]
        g = cv2.cvtColor(cv2.resize(f, (160, 90)), cv2.COLOR_BGR2GRAY)
        res[int(i / fps)] = [len(r.boxes), float(g.mean()), float(g.std())]
    i += 1
json.dump(res, open(sys.argv[2], 'w')); print('done', len(res))
