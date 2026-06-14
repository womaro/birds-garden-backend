#!/usr/bin/env python3
"""
birds.garden — eksport zweryfikowanych detekcji do own/<slug>/ (flywheel).

User w aplikacji poprawia/potwierdza gatunek → backend zapisuje verified_species.
Ten skrypt kopiuje cropy tych detekcji do own/<slug>/, gotowe pod retrening:

    python tools/export_labeled.py
    python tools/build_dataset.py --include-own own
    python tools/train_classifier.py

Czyta DB_* z /opt/bird-api/.env (env-driven — działa po rotacji sekretów).
"""

import argparse
import os
import shutil
import sys
from pathlib import Path

import psycopg2

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from vision.species_list import EN_TO_SLUG


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="own")
    ap.add_argument("--photos-dir", default=os.getenv("PHOTOS_DIR", "/opt/bird-api/photos"))
    args = ap.parse_args()

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "birddb"),
        user=os.getenv("DB_USER", "bird"),
        password=os.getenv("DB_PASSWORD", ""),
    )
    photos = Path(args.photos_dir)
    out = Path(args.out)
    exported, skipped = 0, 0

    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, verified_species, photo_path FROM detections "
            "WHERE verified_species IS NOT NULL AND photo_path IS NOT NULL"
        )
        for det_id, en, rel in cur.fetchall():
            slug = EN_TO_SLUG.get(en)
            src = photos / rel
            if not slug:
                print(f"⚠ id={det_id}: nieznany gatunek '{en}'"); skipped += 1; continue
            if not src.exists():
                print(f"⚠ id={det_id}: brak pliku {src}"); skipped += 1; continue
            d = out / slug
            d.mkdir(parents=True, exist_ok=True)
            shutil.copy(src, d / f"{det_id}.jpg")
            exported += 1
    conn.close()

    print(f"\nWyeksportowano {exported} zweryfikowanych cropów → {out}/ (pominięto {skipped})")
    print("Retrening: build_dataset.py --include-own", args.out, "→ train_classifier.py")


if __name__ == "__main__":
    main()
