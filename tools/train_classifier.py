#!/usr/bin/env python3
"""
birds.garden — trening klasyfikatora gatunku (YOLOv8-cls).

    python tools/train_classifier.py --data dataset --epochs 40 --device cpu

Po treningu najlepsze wagi lądują w:
    runs/classify/<name>/weights/best.pt

Wpięcie do produkcji (bez zmian w kodzie):
    1) skopiuj best.pt na VPS, np. /opt/bird-api/models/species.pt
    2) w /opt/bird-api/.env ustaw:
         SPECIES_MODEL=/opt/bird-api/models/species.pt
         SPECIES_MIN_CONFIDENCE=0.55
    3) systemctl restart bird-yolo
    4) sprawdź: curl 127.0.0.1:8002/health  → "species_classifier": true

Ten sam skrypt po dorzuceniu własnych cropów (build_dataset --include-own) =
retrening na danych z Twojego ogrodu.
"""

import argparse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="dataset", help="folder z train/ i val/")
    ap.add_argument("--model", default="yolov8s-cls.pt", help="n=szybszy, s=dokładniejszy")
    ap.add_argument("--epochs", type=int, default=40)
    ap.add_argument("--imgsz", type=int, default=224)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--name", default="birds_cls")
    ap.add_argument("--device", default="", help="np. cpu, mps, 0; puste = auto")
    args = ap.parse_args()

    from ultralytics import YOLO  # ciężki import — dopiero tutaj

    model = YOLO(args.model)
    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        name=args.name,
        device=args.device or None,
    )
    print(f"\nWagi: runs/classify/{args.name}/weights/best.pt")
    print("Wpięcie: SPECIES_MODEL=.../best.pt w /opt/bird-api/.env → restart bird-yolo")


if __name__ == "__main__":
    main()