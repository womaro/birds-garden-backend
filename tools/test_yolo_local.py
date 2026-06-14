#!/usr/bin/env python3
"""
birds.garden — lokalny test vision pipeline BEZ kamery.

Cel: zwalidować, że YOLOv8 wykrywa ptaki i zapisuje cropy, zanim przyjedzie
Reolink. Wrzuć dowolne zdjęcia ptaków (telefon, neta, cokolwiek) do ./samples/
i odpal. To nie zastępuje walidacji w polu (P0), ale potwierdza, że rura
software'owa działa end-to-end.

Dwa tryby:
  python tools/test_yolo_local.py                 # tryb direct (import detektora)
  python tools/test_yolo_local.py --http           # przez działający serwis :8002

Direct nie wymaga uruchomionego serwisu — najszybsza walidacja.
"""

import argparse
import os
import sys
from pathlib import Path

SAMPLES = Path(os.getenv("SAMPLES_DIR", "samples"))
EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def run_direct(images):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from vision.detector import BirdDetector

    det = BirdDetector(
        model_path=os.getenv("YOLO_MODEL", "yolov8n.pt"),
        target_classes=os.getenv("YOLO_TARGET_CLASSES", "bird").split(","),
        min_conf=os.getenv("YOLO_MIN_CONFIDENCE", "0.35"),
        photos_dir=os.getenv("PHOTOS_DIR", "photos_test"),
    )
    for p in images:
        res = det.detect(p.read_bytes())
        _print(p, res)


def run_http(images):
    import requests  # tylko w trybie --http

    url = f"http://{os.getenv('YOLO_HOST', '127.0.0.1')}:{os.getenv('YOLO_PORT', '8002')}/detect"
    for p in images:
        with p.open("rb") as f:
            r = requests.post(url, files={"file": (p.name, f, "image/jpeg")}, timeout=60)
        r.raise_for_status()
        _print(p, r.json())


def _print(path, res):
    mark = "🐦" if res["detected"] else "··"
    print(
        f"{mark} {path.name:<28} "
        f"detected={res['detected']} count={res['count']} "
        f"conf={res['best_confidence']:.2f} photo={res['photo_path']}"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--http", action="store_true", help="testuj przez serwis :8002")
    ap.add_argument("paths", nargs="*", help="konkretne pliki (domyślnie ./samples/*)")
    args = ap.parse_args()

    if args.paths:
        images = [Path(p) for p in args.paths]
    else:
        if not SAMPLES.exists():
            print(f"Brak folderu {SAMPLES}/ — wrzuć tam zdjęcia ptaków i odpal ponownie.")
            sys.exit(1)
        images = sorted(p for p in SAMPLES.iterdir() if p.suffix.lower() in EXTS)

    if not images:
        print("Brak zdjęć do testu.")
        sys.exit(1)

    print(f"Testuję {len(images)} zdjęć ({'HTTP :8002' if args.http else 'direct'})...\n")
    (run_http if args.http else run_direct)(images)
    print("\nGotowe. Cropy zapisane w PHOTOS_DIR.")


if __name__ == "__main__":
    main()
