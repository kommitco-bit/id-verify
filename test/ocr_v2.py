import re

import cv2
import numpy as np
import pytesseract

OCR_MIN_WIDTH = 2000  # un peu plus grand pour les petits textes
TESSERACT_LANG = "fra"
PSM_LIST = (6, 11)  # 6 = bloc, 11 = texte épars (champs isolés)


def _resize(gray):
    h, w = gray.shape
    if w < OCR_MIN_WIDTH:
        scale = OCR_MIN_WIDTH / w
        gray = cv2.resize(
            gray, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC
        )
    return gray


def _normalize_illumination(gray):
    """Supprime ombres et reflets : divise l'image par son fond estimé."""
    bg = cv2.dilate(gray, np.ones((7, 7), np.uint8))  # efface le texte sombre
    bg = cv2.medianBlur(bg, 21)  # lisse le fond
    return cv2.divide(gray, bg, scale=255)


def _deskew(gray, max_angle=5.0, step=0.5):
    """Redresse l'image par profil de projection (léger pour ton CPU)."""
    small = cv2.resize(gray, None, fx=0.25, fy=0.25)
    _, bw = cv2.threshold(small, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    h, w = bw.shape
    center = (w // 2, h // 2)

    best_angle, best_score = 0.0, -1.0
    for angle in np.arange(-max_angle, max_angle + step, step):
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rot = cv2.warpAffine(bw, M, (w, h), flags=cv2.INTER_NEAREST)
        score = np.var(rot.sum(axis=1))  # lignes de texte nettes = variance haute
        if score > best_score:
            best_score, best_angle = score, angle

    if abs(best_angle) < 0.3:
        return gray
    H, W = gray.shape
    M = cv2.getRotationMatrix2D((W // 2, H // 2), best_angle, 1.0)
    return cv2.warpAffine(
        gray, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )


def _sharpen(gray):
    blur = cv2.GaussianBlur(gray, (0, 0), 1.5)
    return cv2.addWeighted(gray, 1.6, blur, -0.6, 0)


def _preprocess_variants(card_img):
    """Retourne plusieurs versions de l'image pour maximiser la lecture."""
    gray = cv2.cvtColor(card_img, cv2.COLOR_BGR2GRAY)
    gray = _resize(gray)
    gray = _normalize_illumination(gray)
    gray = _deskew(gray)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = _sharpen(clahe.apply(cv2.bilateralFilter(gray, 5, 50, 50)))

    # Variante 1 : seuil adaptatif (bon pour petits textes / éclairage inégal)
    adaptive = cv2.adaptiveThreshold(
        enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15
    )
    # Variante 2 : Otsu sur l'image normalisée (bon pour gros textes propres)
    _, otsu = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    variants = []
    for img in (adaptive, otsu):
        # marge blanche : Tesseract ignore souvent le texte collé au bord
        img = cv2.copyMakeBorder(img, 30, 30, 30, 30, cv2.BORDER_CONSTANT, value=255)
        variants.append(img)
    return variants


def _clean_line(line):
    return re.sub(r"\s+", " ", line).strip()


def _key(line):
    return re.sub(r"\W+", "", line.lower())


def extract_raw_text(card_img):
    if card_img is None:
        return ""

    seen, lines = [], []
    for img in _preprocess_variants(card_img):
        for psm in PSM_LIST:
            config = f"--oem 1 --psm {psm} -c preserve_interword_spaces=1"
            text = pytesseract.image_to_string(img, lang=TESSERACT_LANG, config=config)
            for raw in text.splitlines():
                line = _clean_line(raw)
                k = _key(line)
                if len(k) < 3:
                    continue
                # ignore si déjà présent (ou contenu dans une ligne existante)
                if any(k in s for s in seen):
                    continue
                seen.append(k)
                lines.append(line)
    return "\n".join(lines)
