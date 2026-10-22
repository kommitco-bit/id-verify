"""OCR : extraire le texte brut et les champs d'une carte."""

import re

import cv2
import numpy as np
import pytesseract
from pytesseract import Output

try:
    import config

    TESSERACT_LANG = getattr(config, "TESSERACT_LANG", "fra")
    TESSERACT_PSM = getattr(config, "TESSERACT_PSM", 6)
    OCR_MIN_WIDTH = getattr(config, "OCR_MIN_WIDTH", 1500)
except ImportError:
    TESSERACT_LANG, TESSERACT_PSM, OCR_MIN_WIDTH = "fra", 6, 1500


MIN_CONF = 70  # ignore les mots peu fiables de la 2e passe
MIN_CONF_EXTRA = 70  # fiabilité minimale des mots ajoutés par la 2e passe
OVERLAP_MAX = 0.3  # au-delà, le mot est considéré déjà trouvé


def _get_words(img, psm, min_conf):
    h, w = img.shape[:2]
    d = pytesseract.image_to_data(
        img, lang=TESSERACT_LANG, config=f"--psm {psm}", output_type=Output.DICT
    )
    words = []
    for i, text in enumerate(d["text"]):
        text = text.strip()
        if not text:
            continue
        try:
            conf = float(d["conf"][i])
        except ValueError:
            continue
        if conf < min_conf:
            continue
        # coordonnées en fraction (0..1) : comparables entre les deux images
        x0, y0 = d["left"][i] / w, d["top"][i] / h
        x1, y1 = x0 + d["width"][i] / w, y0 + d["height"][i] / h
        words.append({"t": text, "box": (x0, y0, x1, y1)})
    return words


def _overlap(a, b):
    """Part de la boîte a recouverte par la boîte b."""
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    area = (a[2] - a[0]) * (a[3] - a[1])
    return (ix * iy) / area if area > 0 else 0.0


def _yc(w):
    return (w["box"][1] + w["box"][3]) / 2


def _words_to_text(words):
    if not words:
        return ""
    tol = 0.6 * float(np.median([w["box"][3] - w["box"][1] for w in words]))

    rows = []
    for w in sorted(words, key=_yc):
        if rows and abs(_yc(w) - rows[-1]["yc"]) <= tol:
            rows[-1]["w"].append(w)
            rows[-1]["yc"] = float(np.mean([_yc(x) for x in rows[-1]["w"]]))
        else:
            rows.append({"yc": _yc(w), "w": [w]})

    lines = []
    for r in rows:
        r["w"].sort(key=lambda w: w["box"][0])  # gauche -> droite
        lines.append(" ".join(w["t"] for w in r["w"]))
    return "\n".join(lines)


def _preprocess(card_img):
    # TON code d'origine, inchangé
    gray = cv2.cvtColor(card_img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    if w < OCR_MIN_WIDTH:
        scale = OCR_MIN_WIDTH / w
        gray = cv2.resize(
            gray, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC
        )
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


def _preprocess_gray(card_img):
    # Gris agrandi SANS binarisation : Tesseract binarise lui-même,
    # souvent mieux sur les petits textes
    gray = cv2.cvtColor(card_img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    scale = max(OCR_MIN_WIDTH / w, 1.0) * 1.5
    return cv2.resize(
        gray, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC
    )


def _key(line):
    return re.sub(r"\W+", "", line.lower())


def extract_raw_text(card_img):
    if card_img is None:
        return ""

    # Passe 1 : ton prétraitement actuel (tous les mots)
    words = _get_words(_preprocess(card_img), TESSERACT_PSM, min_conf=0)

    # Passe 2 : on ajoute seulement les mots qui n'existent pas déjà à cet endroit
    for w in _get_words(_preprocess_gray(card_img), 11, MIN_CONF_EXTRA):
        if all(_overlap(w["box"], k["box"]) < OVERLAP_MAX for k in words):
            words.append(w)

    return _words_to_text(words)
