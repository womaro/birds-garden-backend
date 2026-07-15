#!/usr/bin/env python3
"""prepare_dataset.py - konwersja eksportu CVAT (YOLO 1.1) na strukture YOLOv8.
Zderza labelki z obrazami po nazwach, dzieli na train/val, generuje data.yaml."""
import argparse, os, random, shutil

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--labels", required=True, help="folder .txt z CVAT (obj_train_data)")
    p.add_argument("--images", required=True, help="folder z obrazami .jpg")
    p.add_argument("--out", required=True, help="folder wyjsciowy datasetu")
    p.add_argument("--val", type=float, default=0.15)
    p.add_argument("--seed", type=int, default=42)
    a = p.parse_args()

    labels_dir = os.path.expanduser(a.labels)
    images_dir = os.path.expanduser(a.images)
    out = os.path.expanduser(a.out)

    pairs, empty = [], 0
    for fn in sorted(os.listdir(labels_dir)):
        if not fn.endswith(".txt"):
            continue
        base = fn[:-4]
        img = os.path.join(images_dir, base + ".jpg")
        lbl = os.path.join(labels_dir, fn)
        if not os.path.exists(img):
            continue
        if os.path.getsize(lbl) == 0:
            empty += 1
        pairs.append((img, lbl))

    if not pairs:
        print("BLAD: zero par obraz+labelka."); return

    random.seed(a.seed); random.shuffle(pairs)
    n_val = max(1, int(len(pairs) * a.val))
    val, train = pairs[:n_val], pairs[n_val:]

    for split, items in [("train", train), ("val", val)]:
        for sub in ("images", "labels"):
            os.makedirs(os.path.join(out, sub, split), exist_ok=True)
        for img, lbl in items:
            base = os.path.splitext(os.path.basename(img))[0]
            shutil.copy2(img, os.path.join(out, "images", split, base + ".jpg"))
            shutil.copy2(lbl, os.path.join(out, "labels", split, base + ".txt"))

    with open(os.path.join(out, "data.yaml"), "w") as f:
        f.write(f"path: {out}\ntrain: images/train\nval: images/val\nnc: 1\nnames: ['bird']\n")

    print(f"gotowe. par: {len(pairs)} (tlo: {empty})  train: {len(train)}  val: {len(val)}")
    print(f"data.yaml: {os.path.join(out, 'data.yaml')}")

if __name__ == "__main__":
    main()
