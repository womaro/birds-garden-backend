"""
birds.garden — vision detector (YOLOv8).

Dla każdego wykrytego ptaka (do MAX_CROPS, posortowane po confidence):
  • zapisuje SZEROKI, kwadratowy kadr z kontekstem  → zdjęcie na kartę (photo_path),
  • do klasyfikatora podaje CIASNY crop po bounding boxie → lepsze rozpoznanie
    (klasyfikator chce ptaka wypełniającego kadr, tło mu szkodzi).
main.py tworzy jeden wiersz detekcji na ptaka.

`crop_best()` (jeden, najpewniejszy ptak, CIASNY) zostaje — używa go build_dataset.py.
Dzięki temu trening (ciasne cropy) jest spójny z wejściem klasyfikatora przy inferencji.
"""

import io
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional, Tuple

from PIL import Image
from ultralytics import YOLO

SpeciesFn = Callable[[Image.Image], Optional[Tuple[str, float]]]


class BirdDetector:
    def __init__(
        self,
        model_path: str,
        target_classes,
        min_conf: float,
        photos_dir: str,
        species_classifier: Optional[SpeciesFn] = None,
        max_crops: int = 8,
    ):
        self.model = YOLO(model_path)
        self.names = {int(k): str(v).lower() for k, v in self.model.names.items()}
        self.target = {c.strip().lower() for c in target_classes if c.strip()}
        self.min_conf = float(min_conf)
        self.photos_dir = Path(photos_dir)
        self.photos_dir.mkdir(parents=True, exist_ok=True)
        self.species_classifier = species_classifier
        self.max_crops = int(max_crops)

    def _birds(self, img: Image.Image):
        out = []
        for r in self.model.predict(img, imgsz=1280, verbose=False):
            for box in r.boxes:
                name = self.names.get(int(box.cls[0]), "")
                conf = float(box.conf[0])
                if name in self.target and conf >= self.min_conf:
                    out.append({"class": name, "confidence": conf,
                                "bbox": [float(v) for v in box.xyxy[0].tolist()]})
        out.sort(key=lambda b: b["confidence"], reverse=True)
        return out

    def _classify(self, crop: Image.Image):
        if self.species_classifier is None:
            return None, None
        try:
            res = self.species_classifier(crop)
        except Exception:
            res = None
        return res if res is not None else (None, None)

    def detect(self, image_bytes: bytes) -> dict:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        birds = self._birds(img)

        out = []
        for b in birds[: self.max_crops]:
            wide = self._crop(img, b["bbox"])             # szeroki kadr → karta
            photo_path = self._save_crop(wide)
            tight = self._crop_tight(img, b["bbox"])      # ciasny → klasyfikator
            species, sconf = self._classify(tight)
            out.append({
                "confidence": b["confidence"],
                "bbox": b["bbox"],
                "photo_path": photo_path,
                "species": species,
                "species_confidence": sconf,
            })

        return {
            "detected": bool(out),
            "count": len(birds),
            "saved": len(out),
            "birds": out,
        }

    def crop_best(self, image_bytes: bytes) -> Optional[Image.Image]:
        """Najpewniejszy ptak, CIASNY crop — dla build_dataset.py (spójny z klasyfikatorem)."""
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        birds = self._birds(img)
        return self._crop_tight(img, birds[0]["bbox"]) if birds else None

    @staticmethod
    def _crop(img: Image.Image, bbox, context: float = 1.9, min_side: int = 80) -> Image.Image:
        """Szeroki, kwadratowy kadr wyśrodkowany na ptaku — na kartę (cały ptak + margines)."""
        w, h = img.size
        x1, y1, x2, y2 = bbox
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        side = max(max(x2 - x1, y2 - y1) * context, float(min_side))
        half = side / 2
        left   = max(0, int(cx - half))
        top    = max(0, int(cy - half))
        right  = min(w, int(cx + half))
        bottom = min(h, int(cy + half))
        return img.crop((left, top, right, bottom))

    @staticmethod
    def _crop_tight(img: Image.Image, bbox, pad: float = 0.12) -> Image.Image:
        """Ciasny crop po bounding boxie — wejście klasyfikatora / dane treningowe."""
        w, h = img.size
        x1, y1, x2, y2 = bbox
        bw, bh = x2 - x1, y2 - y1
        x1 = max(0, int(x1 - bw * pad))
        y1 = max(0, int(y1 - bh * pad))
        x2 = min(w, int(x2 + bw * pad))
        y2 = min(h, int(y2 + bh * pad))
        return img.crop((x1, y1, x2, y2))

    def _save_crop(self, crop: Image.Image) -> str:
        now = datetime.now(timezone.utc)
        day = now.strftime("%Y-%m-%d")
        day_dir = self.photos_dir / day
        day_dir.mkdir(parents=True, exist_ok=True)
        fname = f"{now.strftime('%H%M%S')}_{int(time.time() * 1000) % 1000:03d}_{id(crop) % 1000:03d}.jpg"
        crop.save(day_dir / fname, "JPEG", quality=88)
        return f"{day}/{fname}"