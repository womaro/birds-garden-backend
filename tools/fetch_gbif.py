#!/usr/bin/env python3
"""
birds.garden — pobieranie zdjęć treningowych z GBIF (bootstrap, Poziom 2).

Dla każdego z 35 gatunków: dopasowanie nazwy naukowej → taxonKey, potem
occurrence search z filtrem mediaType=StillImage + obserwacje ludzkie
(nie okazy muzealne) + kraje europejskie. Zapis do raw/<slug>/.

Tylko stdlib — działa wszędzie bez instalacji. GBIF agreguje m.in. iNaturalist.

    python tools/fetch_gbif.py --per-species 300
    python tools/fetch_gbif.py --only blue_tit,great_tit   # debug pojedyncze

Licencja: zdjęcia GBIF bywają CC0 / CC-BY / CC-BY-NC. Do bootstrapu i walidacji
OK. Model produkcyjny docelowo na WŁASNYCH cropach z ogrodu (Poziom 3) — patrz doc.
"""

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from vision.species_list import SPECIES

GBIF = "https://api.gbif.org/v1"
UA = "birds.garden-dataset/1.0 (research)"
EUROPE = ["PL", "DE", "CZ", "SK", "LT", "UA", "AT", "NL", "BE",
          "FR", "DK", "SE", "GB", "CH", "HU", "ES", "IT"]
EXTS_OK = (".jpg", ".jpeg", ".png", ".webp")


def _get(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def taxon_key(sci: str):
    q = urllib.parse.urlencode({"name": sci})
    d = _get(f"{GBIF}/species/match?{q}")
    return d.get("usageKey"), d.get("matchType", "NONE")


def image_urls(taxon: int, countries, want: int):
    urls, offset, limit = [], 0, 300
    cparams = "".join(f"&country={c}" for c in countries)
    while len(urls) < want and offset < 100000:
        base = urllib.parse.urlencode({
            "taxonKey": taxon, "mediaType": "StillImage",
            "basisOfRecord": "HUMAN_OBSERVATION", "limit": limit, "offset": offset,
        })
        d = _get(f"{GBIF}/occurrence/search?{base}{cparams}")
        results = d.get("results", [])
        if not results:
            break
        for occ in results:
            for m in occ.get("media", []):
                ident = m.get("identifier")
                if m.get("type") == "StillImage" and ident:
                    urls.append(ident)
        if d.get("endOfRecords"):
            break
        offset += limit
        time.sleep(0.2)
    # dedup zachowując kolejność
    seen, uniq = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq[:want]


def download(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        if len(data) < 2000:        # zbyt mały = prawdopodobnie błąd/placeholder
            return False
        dest.write_bytes(data)
        return True
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-species", type=int, default=300)
    ap.add_argument("--out", default="raw")
    ap.add_argument("--countries", default=",".join(EUROPE))
    ap.add_argument("--only", default="", help="csv slugów (debug)")
    args = ap.parse_args()

    countries = [c.strip() for c in args.countries.split(",") if c.strip()]
    only = {s.strip() for s in args.only.split(",") if s.strip()}
    out = Path(args.out)

    for sp in SPECIES:
        if only and sp["slug"] not in only:
            continue
        try:
            key, mt = taxon_key(sp["sci"])
        except Exception as e:
            print(f"⚠ {sp['slug']}: błąd match ({e})")
            continue
        if not key:
            print(f"⚠ {sp['slug']}: brak taxonKey dla {sp['sci']}")
            continue
        urls = image_urls(key, countries, args.per_species)
        d = out / sp["slug"]
        d.mkdir(parents=True, exist_ok=True)
        n = 0
        for i, u in enumerate(urls):
            if download(u, d / f"{i:04d}.jpg"):
                n += 1
            time.sleep(0.05)
        print(f"✓ {sp['slug']:<26} {sp['sci']:<30} {n:>4} zdjęć  (key={key}, {mt})")

    print(f"\nGotowe → {out}/. Następnie: python tools/build_dataset.py")


if __name__ == "__main__":
    main()
