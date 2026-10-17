"""OCR V1 : extraire le texte brut d'une carte avec Tesseract."""

import cv2
import numpy as np
import pytesseract

try:
    import config

    TESSERACT_LANG = getattr(config, "TESSERACT_LANG", "fra")
    TESSERACT_PSM = getattr(config, "TESSERACT_PSM", 6)
    OCR_MIN_WIDTH = getattr(config, "OCR_MIN_WIDTH", 1500)
except ImportError:
    TESSERACT_LANG = "fra"
    TESSERACT_PSM = 6
    OCR_MIN_WIDTH = 1500


def _preprocess(card_img: np.ndarray) -> np.ndarray:
    """Gris -> upscale si trop petit -> binarisation Otsu."""
    gray = cv2.cvtColor(card_img, cv2.COLOR_BGR2GRAY)

    h, w = gray.shape
    if w < OCR_MIN_WIDTH:
        scale = OCR_MIN_WIDTH / w
        new_size = (int(w * scale), int(h * scale))
        gray = cv2.resize(gray, new_size, interpolation=cv2.INTER_CUBIC)

    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


def extract_raw_text(card_img: np.ndarray) -> str:
    """Renvoie le texte brut lu par Tesseract (chaîne vide si rien)."""
    if card_img is None:
        return ""
    processed = _preprocess(card_img)
    tesseract_config = f"--psm {TESSERACT_PSM}"
    text = pytesseract.image_to_string(
        processed, lang=TESSERACT_LANG, config=tesseract_config
    )
    return text


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python src/ocr.py chemin/vers/image.jpg")
        sys.exit(1)

    img = cv2.imread(sys.argv[1])
    if img is None:
        print(f"Impossible de lire : {sys.argv[1]}")
        sys.exit(1)

    print("=== TEXTE BRUT ===")
    print(extract_raw_text(img))
