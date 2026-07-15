#!/usr/bin/env python3
"""dedup_frames.py - odsiewa near-duplikaty z folderu klatek (pod anotacje).
Zostawia klatki rozne od poprzednio zachowanej. Uruchom: python tools/dedup_frames.py"""
import argparse, glob, os, shutil
from PIL import Image

def thumb(path, size=128):
    im = Image.open(path)
    im.draft("L", (512, 288))
    return list(im.convert("L").resize((size, size)).getdata())

def mad(a, b):
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="src", default=os.path.expanduser("~/Desktop/grab"))
    p.add_argument("--out", dest="dst", default=os.path.expanduser("~/Desktop/grab_diverse"))
    p.add_argument("--thresh", type=float, default=6.0, help="wyzej=mniej klatek")
    a = p.parse_args()

    files = sorted(glob.glob(os.path.join(a.src, "*.jpg")))
    if not files:
        print("brak .jpg w", a.src); return
    os.makedirs(a.dst, exist_ok=True)
    kept, last = 0, None
    for f in files:
        try:
            t = thumb(f)
        except Exception as e:
            print("pomijam", f, e); continue
        if last is None or mad(t, last) > a.thresh:
            shutil.copy2(f, a.dst); kept += 1; last = t
    print(f"\nprzejrzano {len(files)} -> zachowano {kept}   folder: {a.dst}")

if __name__ == "__main__":
    main()
