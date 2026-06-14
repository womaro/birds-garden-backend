"""
birds.garden — klasyfikator gatunku na cropie (YOLOv8-cls).

Ładuje wytrenowany model (best.pt), klasyfikuje wycinek ptaka, mapuje slug klasy
na nazwę EN spójną z BIRD_BIO / detections.species. Poniżej progu confidence
zwraca None → detekcja zostaje jako "ptak + zdjęcie" bez gatunku (świadomy fallback).

Wpięcie: yolo_service.py woła load_from_env() i podaje wynik jako
BirdDetector(species_classifier=...). Brak modelu → None → pipeline działa bez gatunku.
"""

import os
from typing import Optional, Tuple

from PIL import Image

from .species_list import SLUG_TO_EN


class SpeciesClassifier:
    def __init__(self, model_path: str, min_conf: float = 0.55):
        from ultralytics import YOLO  # import lokalnie — nieładowany gdy brak modelu
        self.model = YOLO(model_path)
        self.min_conf = float(min_conf)
        self.names = {int(k): str(v) for k, v in self.model.names.items()}

    def __call__(self, crop: Image.Image) -> Optional[Tuple[str, float]]:
        res = self.model.predict(crop, verbose=False)[0]
        probs = getattr(res, "probs", None)
        if probs is None:
            return None
        conf = float(probs.top1conf)
        if conf < self.min_conf:
            return None
        slug = self.names.get(int(probs.top1), "")
        return SLUG_TO_EN.get(slug, slug), conf


def load_from_env() -> Optional["SpeciesClassifier"]:
    path = os.getenv("SPECIES_MODEL", "").strip()
    if not path or not os.path.exists(path):
        return None
    return SpeciesClassifier(path, float(os.getenv("SPECIES_MIN_CONFIDENCE", "0.55")))
