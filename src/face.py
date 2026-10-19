# src/face.py — J8 étape 1 : détection de visage avec YuNet
import os

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


# ===== J9 : empreinte faciale (SFace) — À AJOUTER à la fin de src/face.py =====
# Si os / numpy / cv2 sont déjà importés en haut du fichier, NE PAS les réimporter.


# --- Singleton paresseux pour SFace (chargé une seule fois) ---
_recognizer = None


def _get_recognizer():
    """Charge le modèle SFace via OpenCV une seule fois, réutilisé ensuite."""
    global _recognizer
    if _recognizer is None:
        if not os.path.exists(SFACE_MODEL):
            print(f"[face] Modèle SFace introuvable : {SFACE_MODEL}")
            return None
        # FaceRecognizerSF.create(model_path, config="") : config vide = défaut
        _recognizer = cv2.FaceRecognizerSF.create(SFACE_MODEL, "")
    return _recognizer


# --- Empreinte faciale : 128 valeurs float32, ou None ---
def get_embedding(img):
    """
    Contrat §6 : image contenant un visage -> np.ndarray float32 (128,), sinon None.
    Étapes : détecter -> garder le plus grand visage -> aligner (112x112) -> feature.
    """
    if img is None:
        return None

    recognizer = _get_recognizer()
    if recognizer is None:
        return None

    faces = _detect_faces(img)
    if not faces:
        return None

    # On garde le plus grand visage (= le plus proche de la caméra).
    face = max(faces, key=lambda f: f["bbox"][2] * f["bbox"][3])

    # Reconstruire la ligne brute (1, 15) attendue par alignCrop :
    # [x, y, w, h, lm1x, lm1y, lm2x, lm2y, ..., lm5x, lm5y, score]
    x, y, w, h = face["bbox"]
    lms = np.asarray(face["landmarks"], dtype=np.float32).flatten()
    if lms.size != 10:
        print(f"[face] landmarks inattendus : taille={lms.size} (attendu 10)")
        return None
    row = np.concatenate([[x, y, w, h], lms, [float(face["score"])]])
    row = row.astype(np.float32).reshape(1, 15)

    # alignCrop : recadre ET aligne le visage à 112x112 (entrée attendue par SFace).
    aligned = recognizer.alignCrop(img, row)
    if aligned is None or aligned.size == 0:
        return None

    # feature : vecteur (1, 128) float32 -> on aplatit en (128,).
    feat = recognizer.feature(aligned).flatten().astype(np.float32)
    if feat.size != 128:
        print(f"[face] empreinte inattendue : taille={feat.size} (attendu 128)")
        return None
    return feat


# ===== J9 : comparaison cosinus — À AJOUTER à la fin de src/face.py =====


def compare(emb_a, emb_b):
    """
    Contrat §6 : deux empreintes -> float (similarité cosinus, plus haut = plus ressemblant).
    Renvoie None si l'une est absente/invalide (au lieu de planter).
    Résultat dans [-1, 1]. Seuil de décision : SEUIL_SFACE (config.py, à créer J9+).
    """
    # Garde-fous : None, types, tailles.
    if emb_a is None or emb_b is None:
        return None
    a = np.asarray(emb_a, dtype=np.float32).flatten()
    b = np.asarray(emb_b, dtype=np.float32).flatten()
    if a.size == 0 or b.size == 0 or a.size != b.size:
        return None

    # Normes L2 (longueurs des vecteurs). On évite la division par zéro.
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return None

    # Cosinus = produit scalaire divisé par le produit des normes.
    cos = float(np.dot(a, b) / (na * nb))

    # Petit garde-fou numérique : force dans [-1, 1] (erreurs flottantes ~1e-7).
    if cos > 1.0:
        cos = 1.0
    if cos < -1.0:
        cos = -1.0
    return cos
