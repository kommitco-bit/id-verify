# src/face.py — J8 étape 1 : détection de visage avec YuNet
import cv2
import numpy as np

# Chemins des modèles (à déplacer dans config.py plus tard, avec ton accord)
YUNET_MODEL = "models/face_detection_yunet_2023mar.onnx"
SFACE_MODEL = "models/face_recognition_sface_2021dec.onnx"  # réservé pour J9

# Seuils de détection (provisoires, ajustables dans config.py)
SCORE_THRESHOLD = 0.6
NMS_THRESHOLD = 0.3
TOP_K = 5000

# Détecteur YuNet chargé une seule fois (singleton paresseux)
_detector = None


def _get_detector():
    """Charge YuNet une seule fois et le réutilise."""
    global _detector
    if _detector is None:
        _detector = cv2.FaceDetectorYN.create(
            YUNET_MODEL,
            "",
            (320, 320),  # taille d'entrée par défaut
            SCORE_THRESHOLD,
            NMS_THRESHOLD,
            TOP_K,
        )
    return _detector


def _detect_faces(img: np.ndarray) -> list[dict]:
    """
    Détecte les visages dans une image BGR.
    Retourne une liste de dicts :
      - bbox : (x, y, w, h) en pixels
      - landmarks : tableau (5, 2) des 5 points de repère
      - score : confiance entre 0 et 1
    """
    if img is None or img.size == 0:
        return []

    h, w = img.shape[:2]
    detector = _get_detector()
    detector.setInputSize((w, h))  # adapte l'entrée à la taille réelle
    _, faces = detector.detect(img)

    if faces is None:
        return []

    results = []
    for face in faces:
        x, y, fw, fh = (int(v) for v in face[:4])
        landmarks = face[4:14].reshape(5, 2).astype(int)
        score = float(face[14])
        results.append(
            {
                "bbox": (x, y, fw, fh),
                "landmarks": landmarks,
                "score": score,
            }
        )
    return results


def _crop_face(
    img: np.ndarray, bbox: tuple[int, int, int, int], margin: float = 0.2
) -> np.ndarray | None:
    """
    Recadre le visage avec une marge relative autour de la boîte englobante.
    Retourne None si le recadrage est invalide.
    """
    if img is None:
        return None

    h, w = img.shape[:2]
    x, y, fw, fh = bbox
    mx, my = int(fw * margin), int(fh * margin)

    x1 = max(0, x - mx)
    y1 = max(0, y - my)
    x2 = min(w, x + fw + mx)
    y2 = min(h, y + fh + my)

    if x2 <= x1 or y2 <= y1:
        return None
    return img[y1:y2, x1:x2].copy()
