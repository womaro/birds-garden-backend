#!/usr/bin/env python3
"""
preannotate.py - wstepna anotacja klatek modelem bird_v0 (bootstrap).

Puszcza detektor na folder klatek i zapisuje ramki w formacie YOLO (.txt)
obok obrazow - gotowe do importu w CVAT (Ty tylko poprawiasz, nie rysujesz
od zera).

Uzycie (na Macu, w venv z ultralytics):
    python tools/preannotate.py --src ~/Desktop/grab_dedup --conf 0.35

Wynik: obok kazdego obrazu plik .txt (format YOLO: klasa cx cy w h, znormalizowane).
Klatki bez ptaka dostaja pusty .txt (poprawne w YOLO - klatka-tlo).
Na koniec: statystyka ile ptakow wykryto.
"""

import argparse
import glob
import os

from ultralytics import YOLO


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default=os.path.expanduser(
        "~/dev/birds-garden-backend/runs/detect/bird_v0/weights/best.pt"))
    p.add_argument("--src", required=True, help="folder z klatkami .jpg")
    p.add_argument("--conf", type=float, default=0.35, help="prog pewnosci")
    p.add_argument("--imgsz", type=int, default=1280)
    a = p.parse_args()

    src = os.path.expanduser(a.src)
    files = sorted(glob.glob(os.path.join(src, "*.jpg")))
    if not files:
        print("brak .jpg w", src)
        return

    model = YOLO(os.path.expanduser(a.model))
    print(f"model: {a.model}")
    print(f"klatek: {len(files)}  conf: {a.conf}  imgsz: {a.imgsz}\n")

    total_boxes = 0
    frames_with_birds = 0
    for i, f in enumerate(files, 1):
        r = model.predict(f, conf=a.conf, imgsz=a.imgsz, verbose=False)[0]
        txt_path = os.path.splitext(f)[0] + ".txt"
        lines = []
        for box in r.boxes:
            # xywhn = [cx, cy, w, h] znormalizowane 0-1 (format YOLO)
            cx, cy, w, h = box.xywhn[0].tolist()
            lines.append(f"0 {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
        with open(txt_path, "w") as out:
            out.write("\n".join(lines))
        if lines:
            frames_with_birds += 1
            total_boxes += len(lines)
        if i % 50 == 0:
            print(f"  {i}/{len(files)}...")

    print(f"\ngotowe.")
    print(f"  klatek z ptakami: {frames_with_birds}/{len(files)}")
    print(f"  wykrytych ptakow (wstepnie): {total_boxes}")
    print(f"  pliki .txt zapisane obok obrazow w {src}")

if __name__ == "__main__":
    main()