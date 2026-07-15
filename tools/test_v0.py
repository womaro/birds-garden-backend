#!/usr/bin/env python3
"""test_v0.py - podglad detektora na klatkach. Zapisuje obrazy z ramkami.
Uruchom: python tools/test_v0.py"""
import argparse, glob, os
from ultralytics import YOLO

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default=os.path.expanduser(
        "~/dev/birds-garden-backend/runs/detect/bird_v0/weights/best.pt"))
    p.add_argument("--src", default=os.path.expanduser("~/Desktop/grab"))
    p.add_argument("--out", default=os.path.expanduser("~/Desktop/v0_preview"))
    p.add_argument("--n", type=int, default=8)
    p.add_argument("--conf", type=float, default=0.25)
    p.add_argument("--imgsz", type=int, default=1280)
    a = p.parse_args()

    files = sorted(glob.glob(os.path.join(os.path.expanduser(a.src), "*.jpg")))
    if not files:
        print("brak .jpg w", a.src); return
    step = max(1, len(files) // a.n)
    sample = files[::step][:a.n]
    os.makedirs(os.path.expanduser(a.out), exist_ok=True)
    model = YOLO(a.model)
    print(f"model: {a.model}\nklatek: {len(sample)} (z {len(files)})\n")
    for f in sample:
        r = model.predict(f, conf=a.conf, imgsz=a.imgsz, verbose=False)[0]
        out_path = os.path.join(os.path.expanduser(a.out), os.path.basename(f))
        r.save(filename=out_path)
        print(f"  {os.path.basename(f)}: {len(r.boxes)} ptakow")
    print(f"\nobrazy z ramkami -> {a.out}")

if __name__ == "__main__":
    main()
