#!/usr/bin/env python3
"""grab.py - zbieranie klatek z kamery. Detektor SKUPIONEGO ruchu + flaga pauzy.
Uruchamiany na Pi. Zapisuje klatke 4K tylko gdy zmiana jest zwarta (ptak),
pomija rozlany szum (wiatr w trawie). Pauza: touch ~/birds-relay/PAUSE."""
import argparse, asyncio, io, os, time
from reolink_aio.api import Host
from PIL import Image, ImageChops

BASE = "/home/wojtek/birds-relay"
GRAB_DIR = f"{BASE}/grab"
PAUSE_FILE = f"{BASE}/PAUSE"
THUMB, CELLS, DELTA = 160, 16, 30

def load_env():
    c = {}
    for line in open(f"{BASE}/.env"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            c[k.strip()] = v.strip().strip('"').strip("'")
    return c

def to_thumb(jpeg_bytes):
    im = Image.open(io.BytesIO(jpeg_bytes))
    im.draft("L", (640, 360))
    return im.convert("L").resize((THUMB, THUMB))

def blob_score(cur, prev):
    diff = ImageChops.difference(cur, prev)
    binm = diff.point(lambda p: 255 if p > DELTA else 0)
    return max(binm.resize((CELLS, CELLS), Image.BILINEAR).getdata())

async def main(args):
    c = load_env()
    HOST = c.get("CAM_HOST") or c.get("CAM_IP")
    USER = c.get("CAM_USER")
    PASS = c.get("CAM_PASSWORD") or c.get("CAM_PASS") or c.get("CAM_PWD")
    os.makedirs(GRAB_DIR, exist_ok=True)
    cam = Host(HOST, USER, PASS)
    await cam.get_host_data()
    prev = None; saved = checked = win_max = 0; paused_note = False
    print(f"start. zapis gdy skupienie > {args.min_blob}. interwal {args.interval}s.")
    try:
        while True:
            if os.path.exists(PAUSE_FILE):
                if not paused_note:
                    print("PAUZA - nie zapisuje..."); paused_note = True
                prev = None; await asyncio.sleep(2); continue
            paused_note = False
            img = await cam.get_snapshot(0)
            if not img:
                await asyncio.sleep(args.interval); continue
            checked += 1
            try:
                thumb = to_thumb(img)
            except Exception as e:
                print("blad miniatury:", e); await asyncio.sleep(args.interval); continue
            if prev is not None:
                score = blob_score(thumb, prev); win_max = max(win_max, score)
                if score > args.min_blob:
                    fn = f"{GRAB_DIR}/{int(time.time())}_{saved}.jpg"
                    open(fn, "wb").write(img); saved += 1
                    print(f"[{saved:4}] zapis (skupienie {score})  {fn}")
            prev = thumb
            if checked % 100 == 0:
                print(f"  ...zyje: sprawdzonych {checked}, zapisanych {saved}, max {win_max}")
                win_max = 0
            await asyncio.sleep(args.interval)
    except KeyboardInterrupt:
        print(f"\nkoniec. sprawdzonych: {checked}, zapisanych: {saved}")
    finally:
        await cam.logout()

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--min-blob", type=int, default=90)
    p.add_argument("--interval", type=float, default=3.0)
    asyncio.run(main(p.parse_args()))
