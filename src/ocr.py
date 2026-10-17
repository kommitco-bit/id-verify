"""OCR : extraire le texte brut et les champs d'une carte."""

import re

import cv2
import numpy as np
import pytesseract

try:
    import config

    TESSERACT_LANG = getattr(config, "TESSERACT_LANG", "fra")
    TESSERACT_PSM = getattr(config, "TESSERACT_PSM", 6)
    OCR_MIN_WIDTH = getattr(config, "OCR_MIN_WIDTH", 1500)
except ImportError:
    TESSERACT_LANG, TESSERACT_PSM, OCR_MIN_WIDTH = "fra", 6, 1500


def _preprocess(card_img):
    gray = cv2.cvtColor(card_img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    if w < OCR_MIN_WIDTH:
        scale = OCR_MIN_WIDTH / w
        gray = cv2.resize(
            gray, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC
        )
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


def extract_raw_text(card_img):
    if card_img is None:
        return ""
    processed = _preprocess(card_img)
    return pytesseract.image_to_string(
        processed, lang=TESSERACT_LANG, config=f"--psm {TESSERACT_PSM}"
    )


_RE_NOM = re.compile(r"Nom\s*:\s*([A-Za-zÀ-ÿ]+)")
_RE_PP = re.compile(r"Postnom\s*/\s*Prenom\s*:\s*([A-Za-zÀ-ÿ]+)\s*/\s*([A-Za-zÀ-ÿ]+)")
_RE_DATE = re.compile(r"Date\s*/\s*Lieu\s*de\s*naissance\s*:\s*(\d{2}/\d{2}/\d{4})")
_RE_NUM = re.compile(r"N\.?[IL1]\.?\s*:?\s*([A-Z])\s*(\d{6,8})")


def extract_fields(card_img):
    """Renvoie dict(nom, postnom, prenom, date_naissance, numero, raw_text)."""
    raw = extract_raw_text(card_img)
    fields = {
        "nom": None,
        "postnom": None,
        "prenom": None,
        "date_naissance": None,
        "numero": None,
        "raw_text": raw,
    }
    if not raw:
        return fields
    if m := _RE_NOM.search(raw):
        fields["nom"] = m.group(1)
    if m := _RE_PP.search(raw):
        fields["postnom"], fields["prenom"] = m.group(1), m.group(2)
    if m := _RE_DATE.search(raw):
        fields["date_naissance"] = m.group(1)
    if m := _RE_NUM.search(raw):
        fields["numero"] = m.group(1) + m.group(2)
    return fields


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        sys.exit("Usage: python src/ocr.py chemin.jpg")
    img = cv2.imread(sys.argv[1])
    if img is None:
        sys.exit(f"Impossible de lire : {sys.argv[1]}")
    for k, v in extract_fields(img).items():
        if k != "raw_text":
            print(f"{k:16s} = {v!r}")
