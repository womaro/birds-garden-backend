"""
birds.garden — YOLOv8 service (osobny proces, port 8002).

TF (BirdNET w bird-api) + PyTorch (YOLO) w jednym procesie = SEGFAULT.
main.py woła ten serwis po HTTP na localhost (127.0.0.1).

Klasyfikator gatunku ładuje się tylko jeśli SPECIES_MODEL w .env wskazuje
istniejący plik wag — inaczej pipeline działa bez gatunku (detect + crop + None).

Uruchomienie (ten sam venv /opt/bird-env, inny proces):
    uvicorn vision.yolo_service:app --host 127.0.0.1 --port 8002
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile

from .detector import BirdDetector
from .species_classifier import load_from_env

_detector: BirdDetector | None = None
_has_species: bool = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _detector, _has_species
    classifier = load_from_env()
    _has_species = classifier is not None
    _detector = BirdDetector(
        model_path=os.getenv("YOLO_MODEL", "yolov8n.pt"),
        target_classes=os.getenv("YOLO_TARGET_CLASSES", "bird").split(","),
        min_conf=os.getenv("YOLO_MIN_CONFIDENCE", "0.35"),
        photos_dir=os.getenv("PHOTOS_DIR", "/opt/bird-api/photos"),
        species_classifier=classifier,
        max_crops=int(os.getenv("MAX_CROPS", "8")),
    )
    yield
    _detector = None


app = FastAPI(title="birds.garden · YOLO service", lifespan=lifespan)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": os.getenv("YOLO_MODEL", "yolov8n.pt"),
        "species_classifier": _has_species,            # True gdy gatunek aktywny
        "species_model": os.getenv("SPECIES_MODEL", ""),
        "loaded": _detector is not None,
    }


@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    if _detector is None:
        raise HTTPException(503, "model not loaded yet")
    data = await file.read()
    if not data:
        raise HTTPException(400, "empty file")
    try:
        return _detector.detect(data)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"detection failed: {e}")