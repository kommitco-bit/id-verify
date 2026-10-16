# src/capture.py
# Recupere une image BGR depuis une webcam, une URL ESP32-CAM ou un fichier.
# Contrat §6 : get_frame(source) -> np.ndarray BGR, ou None en cas d'echec.

from __future__ import annotations

import os

import cv2
import numpy as np
import requests

from config import ESP32_URL, HTTP_TIMEOUT_SECONDS


def _frame_from_http(url: str) -> np.ndarray | None:
    """Telecharge une image JPEG via HTTP et la decode en BGR."""
    try:
        response = requests.get(url, timeout=HTTP_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"[capture] Echec HTTP sur {url} : {error}")
        return None

    data = np.frombuffer(response.content, dtype=np.uint8)
    frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if frame is None:
        print(f"[capture] Contenu recu non decodable en image (URL={url})")
    return frame


def _frame_from_webcam(index: int) -> np.ndarray | None:
    """Ouvre la webcam, lit une frame, la libere aussitot."""
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        print(f"[capture] Webcam {index} introuvable")
        return None
    ok, frame = cap.read()
    cap.release()
    if not ok or frame is None:
        print(f"[capture] Lecture webcam {index} echouee")
        return None
    return frame


def _frame_from_file(path: str) -> np.ndarray | None:
    """Charge une image depuis le disque."""
    if not os.path.isfile(path):
        print(f"[capture] Fichier introuvable : {path}")
        return None
    frame = cv2.imread(path, cv2.IMREAD_COLOR)
    if frame is None:
        print(f"[capture] Fichier non decodable : {path}")
    return frame


def get_frame(source: str) -> np.ndarray | None:
    """
    source accepte trois formes :
      - 'webcam:0'          -> webcam locale
      - 'http://IP/capture' -> ESP32-CAM (ou toute URL d'image)
      - 'file:/chemin.jpg'  -> image locale
    Renvoie une image BGR, ou None si echec. Ne leve jamais d'exception.
    """
    if source.startswith("webcam:"):
        try:
            index = int(source.split(":", 1)[1])
        except ValueError:
            print(f"[capture] Index webcam invalide : {source}")
            return None
        return _frame_from_webcam(index)

    if source.startswith("http://") or source.startswith("https://"):
        return _frame_from_http(source)

    if source.startswith("file:"):
        return _frame_from_file(source.split(":", 1)[1])

    print(f"[capture] Source non reconnue : {source}")
    return None


if __name__ == "__main__":
    # Test rapide : on essaie l'ESP32 configuree dans config.py.
    frame = get_frame(ESP32_URL)
    if frame is None:
        print("ECHEC : aucune image recuperee.")
    else:
        h, w, c = frame.shape
        print(f"OK : image {w}x{h}, {c} canaux, dtype={frame.dtype}")
        cv2.imwrite("capture_test.jpg", frame)
        print("Sauvegardee : capture_test.jpg")
