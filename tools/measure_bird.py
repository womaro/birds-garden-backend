#!/usr/bin/env python3
"""
measure_bird.py - pomiar wielkosci ptaka na klatce 4K + projekt siatki kafli (tiling).

TRYB POMIARU (domyslny):
    python measure_bird.py "captures/*.jpg"
  - SCROLL (kolko myszy) = zoom w punkcie kursora.
  - Klik LEWY 2x = dwa rogi prostokata wokol ptaka -> wymiar + tabela siatek.
  - COFNIJ ostatni pomiar: prawy klik  albo  'u' / 'z' / Backspace
       (jak masz niedokonczony box - kasuje go; jak nie - zdejmuje ostatni gotowy).
  - 'r' = reset zoomu.  'n' / Enter / spacja / zamkniecie okna = NASTEPNY plik.
  - RAPORT ZBIORCZY bierze NAJMNIEJSZEGO (najdalszego) ptaka.

TRYB PODGLADU SIATKI:
    python measure_bird.py klatka.jpg --grid 4x4

Opcje: --imgsz 640   --threshold 25
Zaleznosci (sa w venv z ultralytics): matplotlib, pillow.
"""

import argparse
import glob
import os
import sys

try:
    from PIL import Image
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
except ImportError:
    print("Brak zaleznosci. W venv: pip install matplotlib pillow")
    raise


GRIDS = [(2, 2), (3, 2), (3, 3), (4, 3), (4, 4), (5, 4), (6, 4)]


def downscale_factor(tile_long_px, imgsz):
    return max(tile_long_px / imgsz, 1.0)


def eff_after(bird_short_px, tile_long_px, imgsz):
    return bird_short_px / downscale_factor(tile_long_px, imgsz)


def verdict(eff_px, threshold):
    if eff_px >= threshold:
        return "OK"
    if eff_px >= threshold * 0.7:
        return "granicznie"
    return "ZA MALY"


def grid_table(bird_short_px, W, H, imgsz, threshold):
    print("\n  siatka | kafel (px)     | zejscie | ptak po zejsciu | werdykt")
    print("  -------|----------------|---------|-----------------|--------")
    for c, r in GRIDS:
        tw, th = W / c, H / r
        tl = max(tw, th)
        eff = eff_after(bird_short_px, tl, imgsz)
        f = downscale_factor(tl, imgsz)
        print(f"  {c}x{r:<3} | {tw:>6.0f}x{th:<6.0f} | {f:>5.2f}x  | "
              f"{eff:>11.1f} px | {verdict(eff, threshold)}")


def _zoom_at(ax, x, y, scale):
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    relx = (x - xlim[0]) / (xlim[1] - xlim[0])
    rely = (y - ylim[0]) / (ylim[1] - ylim[0])
    nx = (xlim[1] - xlim[0]) * scale
    ny = (ylim[1] - ylim[0]) * scale
    ax.set_xlim(x - nx * relx, x + nx * (1 - relx))
    ax.set_ylim(y - ny * rely, y + ny * (1 - rely))


def measure_mode(files, imgsz, threshold):
    all_short = []
    frame_size = None

    for path in files:
        try:
            img = Image.open(path)
        except Exception as e:
            print(f"  (pomijam {path}: {e})")
            continue
        W, H = img.size
        frame_size = (W, H)
        print(f"\n=== {path}  ({W}x{H}) ===")

        fig, ax = plt.subplots(figsize=(14, 8))
        ax.imshow(img)
        x0lim, y0lim = ax.get_xlim(), ax.get_ylim()
        ax.set_title(os.path.basename(path) +
                     "\nSCROLL=zoom | klik 2 rogi | prawy/'u'=cofnij | 'r'=reset | 'n'/zamknij=dalej")
        ax.axis("off")
        # pts/pending = biezacy (niedokonczony) pomiar; groups = gotowe pomiary
        state = {"pts": [], "pending": [], "groups": []}

        def undo():
            if state["pending"]:                      # niedokonczony box
                for a in state["pending"]:
                    a.remove()
                state["pending"] = []
                state["pts"] = []
                print("  (skasowano niedokonczony pomiar)")
            elif state["groups"]:                     # ostatni gotowy
                g = state["groups"].pop()
                for a in g["artists"]:
                    a.remove()
                print(f"  (cofnieto pomiar {g['short']:.0f} px)")
            else:
                return
            fig.canvas.draw_idle()

        def onclick(event):
            tb = getattr(fig.canvas, "toolbar", None)
            if tb is not None and getattr(tb, "mode", ""):
                return  # aktywny zoom/pan z paska
            if event.inaxes != ax or event.xdata is None:
                return
            if event.button == 3:                     # prawy = cofnij
                undo()
                return
            if event.button != 1:
                return
            marker = ax.plot(event.xdata, event.ydata, "r+", ms=12, mew=2)[0]
            state["pts"].append((event.xdata, event.ydata))
            state["pending"].append(marker)
            if len(state["pts"]) == 2:
                (bx0, by0), (bx1, by1) = state["pts"]
                w, h = abs(bx1 - bx0), abs(by1 - by0)
                short = min(w, h)
                rect = patches.Rectangle(
                    (min(bx0, bx1), min(by0, by1)), w, h,
                    linewidth=1.5, edgecolor="red", facecolor="none")
                ax.add_patch(rect)
                txt = ax.text(min(bx0, bx1), min(by0, by1) - 6, f"{w:.0f}x{h:.0f}",
                              color="red", fontsize=10, weight="bold")
                state["groups"].append(
                    {"artists": state["pending"] + [rect, txt], "short": short})
                state["pending"] = []
                state["pts"] = []
                print(f"\n  ptak: {w:.0f} x {h:.0f} px  (krotszy bok {short:.0f} px)")
                grid_table(short, W, H, imgsz, threshold)
            fig.canvas.draw_idle()

        def onscroll(event):
            if event.inaxes != ax or event.xdata is None:
                return
            scale = 1 / 1.3 if event.button == "up" else 1.3
            _zoom_at(ax, event.xdata, event.ydata, scale)
            fig.canvas.draw_idle()

        def onkey(event):
            if event.key in ("n", "enter", " "):
                plt.close(fig)
            elif event.key == "r":
                ax.set_xlim(x0lim)
                ax.set_ylim(y0lim)
                fig.canvas.draw_idle()
            elif event.key in ("u", "z", "backspace", "delete"):
                undo()

        fig.canvas.mpl_connect("button_press_event", onclick)
        fig.canvas.mpl_connect("scroll_event", onscroll)
        fig.canvas.mpl_connect("key_press_event", onkey)
        plt.show()   # blokuje do zamkniecia okna

        all_short.extend(g["short"] for g in state["groups"])

    if all_short and frame_size:
        worst = min(all_short)
        W, H = frame_size
        print("\n" + "=" * 62)
        print(f"RAPORT ZBIORCZY - {len(all_short)} pomiarow")
        print(f"najmniejszy (najdalszy) ptak: {worst:.0f} px krotszy bok")
        print("Projektuj siatke pod TEN rozmiar (najgorszy przypadek):")
        grid_table(worst, W, H, imgsz, threshold)
        print("\nWybierz NAJRZADSZA siatke dajaca 'OK' dla najmniejszego ptaka.")
    else:
        print("\nBrak pomiarow.")


def grid_mode(files, grid_str):
    try:
        c, r = (int(x) for x in grid_str.lower().split("x"))
    except Exception:
        print("Zly format --grid. Przyklad: --grid 4x4")
        sys.exit(1)
    for path in files:
        try:
            img = Image.open(path)
        except Exception as e:
            print(f"  (pomijam {path}: {e})")
            continue
        W, H = img.size
        fig, ax = plt.subplots(figsize=(14, 8))
        ax.imshow(img)
        ax.set_title(f"{os.path.basename(path)} - siatka {c}x{r}")
        ax.axis("off")
        for i in range(1, c):
            ax.axvline(i * W / c, color="lime", lw=1)
        for j in range(1, r):
            ax.axhline(j * H / r, color="lime", lw=1)
        plt.show()


def main():
    p = argparse.ArgumentParser(description="Pomiar ptaka + projekt siatki kafli.")
    p.add_argument("paths", nargs="+", help="klatka(i) .jpg (glob OK, w cudzyslowie)")
    p.add_argument("--grid", help="tryb podgladu siatki, np. 4x4")
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--threshold", type=int, default=25)
    a = p.parse_args()

    files = []
    for pat in a.paths:
        files.extend(sorted(glob.glob(pat)))
    if not files:
        print("Brak plikow pasujacych do sciezki. Sprawdz czy nie sa o poziom glebiej "
              "(np. ~/Desktop/grab/grab/).")
        sys.exit(1)

    if a.grid:
        grid_mode(files, a.grid)
    else:
        measure_mode(files, a.imgsz, a.threshold)


if __name__ == "__main__":
    main()