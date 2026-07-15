#!/usr/bin/env python3
"""train_v0.py - trening detektora ptakow (yolov8n) na Macu M1.
Transfer z COCO, imgsz 1280 (male ptaki), MPS. best.pt -> runs/detect/bird_v0/weights/.
Uruchom: PYTORCH_ENABLE_MPS_FALLBACK=1 python tools/train_v0.py"""
import os
from ultralytics import YOLO

DATA = os.path.expanduser("~/dev/birds-garden-backend/datasets/birds_v0/data.yaml")

def main():
    model = YOLO("yolov8n.pt")   # start z wag COCO (transfer learning)
    model.train(
        data=DATA,
        epochs=100,
        imgsz=1280,        # WAZNE: ptaki male, trenuj w duzej rozdzielczosci
        batch=4,
        device="mps",
        patience=25,
        name="bird_v0",
        fliplr=0.5, flipud=0.0, degrees=5, translate=0.1, scale=0.5, mosaic=1.0,
        hsv_h=0.015, hsv_s=0.7, hsv_v=0.4,
    )
    print("\nbest.pt -> runs/detect/bird_v0/weights/best.pt")

if __name__ == "__main__":
    main()
