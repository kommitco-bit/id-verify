import difflib
import re

import cv2
import pytesseract
from pytesseract import Output

try:
    import config

    # `config` est ton module de configuration existant (déjà importé dans ton fichier).
    TESSERACT_LANG = getattr(config, "TESSERACT_LANG", "fra")
    TESSERACT_PSM = getattr(config, "TESSERACT_PSM", 6)
    OCR_MIN_WIDTH = getattr(config, "OCR_MIN_WIDTH", 1500)
    OCR_MIN_CONF = getattr(
        config, "OCR_MIN_CONF", 40
    )  # confiance minimale d'un mot (0-100)
    OCR_USE_CLAHE = getattr(
        config, "OCR_USE_CLAHE", False
    )  # à tester si éclairage très inégal
    OCR_SPARSE_PSM = 11  # texte épars : adapté aux champs dispersés d'une carte
except ImportError:
    (
        TESSERACT_LANG,
        TESSERACT_PSM,
        OCR_MIN_WIDTH,
        OCR_MIN_CONF,
        OCR_USE_CLAHE,
        OCR_SPARSE_PSM,
    ) = ("fra", 6, 1500, 40, False, 11)


def _preprocess(card_img):
    """Niveaux de gris + agrandissement + binarisation ADAPTATIVE (par zone)."""
    if card_img.ndim == 3:
        gray = cv2.cvtColor(card_img, cv2.COLOR_BGR2GRAY)
    else:
        gray = card_img.copy()

    h, w = gray.shape
    if w < OCR_MIN_WIDTH:
        scale = OCR_MIN_WIDTH / w
        gray = cv2.resize(
            gray, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC
        )

    # Léger débruitage qui préserve les contours
    gray = cv2.bilateralFilter(gray, 5, 35, 35)

    if OCR_USE_CLAHE:
        gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)

    # Seuil calculé localement : garde le petit texte même si l'éclairage varie
    h, w = gray.shape
    block = max(15, (w // 60) | 1)  # taille de bloc impaire, proportionnelle à l'image
    return cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block, 15
    )


def _ocr_lines(img, psm):
    """Lance Tesseract et renvoie les lignes, en ignorant les mots peu fiables."""
    data = pytesseract.image_to_data(
        img,
        lang=TESSERACT_LANG,
        config=f"--psm {psm}",
        output_type=Output.DICT,
    )
    lines = {}
    for i, word in enumerate(data["text"]):
        word = word.strip()
        if not word:
            continue
        try:
            conf = float(data["conf"][i])
        except ValueError:
            continue
        if conf < OCR_MIN_CONF:
            continue
        key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        lines.setdefault(key, []).append((data["left"][i], word))

    return [" ".join(word for _, word in sorted(lines[key])) for key in sorted(lines)]


def _norm(text):
    return re.sub(r"[^0-9a-zà-ÿ]", "", text.lower())


def _is_known(norm, known):
    """Vrai si la ligne est déjà (quasiment) présente dans le texte retenu."""
    if not norm:
        return True
    for other in known:
        if norm in other:
            return True
        if difflib.SequenceMatcher(None, norm, other).ratio() >= 0.8:
            return True
    return False


def extract_raw_text(card_img):
    if card_img is None:
        return ""

    processed = _preprocess(card_img)

    # Passe 1 : mise en page en bloc (comme avant)
    lines = _ocr_lines(processed, TESSERACT_PSM)
    known = [_norm(line) for line in lines]

    # Passe 2 : texte épars -> récupère les champs manqués par la passe 1
    for line in _ocr_lines(processed, OCR_SPARSE_PSM):
        norm = _norm(line)
        if _is_known(norm, known):
            continue
        lines.append(line)
        known.append(norm)

    return "\n".join(lines)
