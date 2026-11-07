"""Kesan orang (YOLOv8) pada video, simpan kotak setiap sampel -> JSON.
Guna: python3 detect.py VIDEO OUT.json FPS"""
import sys, json, cv2
from ultralytics import YOLO
vid, out, fps = sys.argv[1], sys.argv[2], float(sys.argv[3])
m = YOLO('/home/user/work/yolov8n.pt')
cap = cv2.VideoCapture(vid)
vf = cap.get(cv2.CAP_PROP_FPS); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
step = max(1, round(vf / fps)); res = {}
i = 0
while True:
    ok = cap.grab()
    if not ok: break
    if i % step == 0:
        ok, fr = cap.retrieve()
        r = m(fr, imgsz=960, conf=0.3, classes=[0], verbose=False)[0]
        res[f"{i / vf:.2f}"] = [[round(float(v)) for v in b.xyxy[0]] + [round(float(b.conf), 2)] for b in r.boxes]
    i += 1
json.dump(res, open(out, 'w'))
print('done', len(res))
