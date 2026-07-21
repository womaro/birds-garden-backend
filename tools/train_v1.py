"""train_v1.py - trening detektora v1 na powiekszonym zbiorze (660 klatek).
Batch 1 (157, recznie) + batch 2 (507, poprawiona pre-anotacja v0).
Uruchom: PYTORCH_ENABLE_MPS_FALLBACK=1 python tools/train_v1.py"""
import os
from ultralytics import YOLO

DATA = os.path.expanduser("~/dev/birds-garden-backend/datasets/birds_v1/data.yaml")

def main():
    model = YOLO("yolov8n.pt")   # transfer z COCO
    model.train(
        data=DATA,
        epochs=150,        # wiekszy zbior -> wiecej epok, early-stop utnie
        imgsz=1280,
        batch=4,
        device="mps",
        patience=30,
        name="bird_v1",
        fliplr=0.5, flipud=0.0, degrees=5, translate=0.1, scale=0.5, mosaic=1.0,
        hsv_h=0.015, hsv_s=0.7, hsv_v=0.4,
    )
    print("\nbest.pt -> runs/detect/bird_v1/weights/best.pt")

if __name__ == "__main__":
    main()