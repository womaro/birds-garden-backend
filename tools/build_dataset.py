#!/usr/bin/env python3
"""
birds.garden — budowa datasetu do YOLOv8-cls.

Bierze surowe zdjęcia raw/<slug>/, wycina ptaka TĄ SAMĄ logiką co produkcja
(BirdDetector.crop_best) i układa w strukturę klasyfikacji:

    dataset/train/<slug>/*.jpg
    dataset/val/<slug>/*.jpg

To kluczowe: model trenuje na cropach, nie na pełnych zdjęciach — bo w polu
też dostanie crop z YOLO. Spójność trening↔serwowanie.

RETRENING NA WŁASNYCH DANYCH: gdy uzbierasz cropy z ogrodu (detektor zapisuje je
do PHOTOS_DIR), posortuj je per gatunek do own/<slug>/ i dorzuć:

    python tools/build_dataset.py --include-own own
    python tools/train_classifier.py            # i już masz model na swoich danych

Własne cropy są już wycięte → trafiają wprost (bez ponownej detekcji).
"""

import argparse
import random
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from vision.detector import BirdDetector

EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="raw", help="surowe zdjęcia: raw/<slug>/")
    ap.add_argument("--out", default="dataset", help="wynik: dataset/{train,val}/<slug>/")
    ap.add_argument("--include-own", default="", help="własne cropy: own/<slug>/ (już wycięte)")
    ap.add_argument("--val-split", type=float, default=0.15)
    ap.add_argument("--min-per-class", type=int, default=30)
    ap.add_argument("--crop-conf", type=float, default=0.25, help="próg detekcji przy wycinaniu")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    random.seed(args.seed)

    det = BirdDetector(model_path="yolov8n.pt", target_classes=["bird"],
                       min_conf=args.crop_conf, photos_dir="/tmp/_bg_unused")
    raw = Path(args.raw)
    out = Path(args.out)
    own = Path(args.include_own) if args.include_own else None

    classes = {d.name for d in raw.iterdir() if d.is_dir()} if raw.exists() else set()
    if own and own.exists():
        classes |= {d.name for d in own.iterdir() if d.is_dir()}
    classes = sorted(classes)

    if not classes:
        print("Brak danych. Najpierw: python tools/fetch_gbif.py")
        return

    total, weak = 0, []
    for slug in classes:
        crops = []
        src = raw / slug
        if src.exists():
            for img in src.iterdir():
                if img.suffix.lower() not in EXTS:
                    continue
                try:
                    crop = det.crop_best(img.read_bytes())
                except Exception:
                    crop = None
                if crop is not None:
                    crops.append(("crop", crop))
        if own and (own / slug).exists():
            for img in (own / slug).iterdir():
                if img.suffix.lower() in EXTS:
                    crops.append(("file", img))

        if not crops:
            print(f"⚠ {slug:<26} 0 cropów — pomijam")
            continue
        if len(crops) < args.min_per_class:
            weak.append((slug, len(crops)))

        random.shuffle(crops)
        n_val = max(1, int(len(crops) * args.val_split))
        for i, (kind, obj) in enumerate(crops):
            split = "val" if i < n_val else "train"
            dest_dir = out / split / slug
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / f"{i:05d}.jpg"
            if kind == "crop":
                obj.save(dest, "JPEG", quality=90)
            else:
                shutil.copy(obj, dest)
        total += len(crops)
        print(f"✓ {slug:<26} {len(crops):>4} cropów  →  train {len(crops) - n_val} / val {n_val}")

    print(f"\nRazem {total} cropów w {out}/.")
    if weak:
        print("Mało danych (dozbieraj lub podnieś --per-species w fetch_gbif):")
        for slug, n in weak:
            print(f"   {slug}: {n}")
    print("Następnie: python tools/train_classifier.py --data", out)


if __name__ == "__main__":
    main()
