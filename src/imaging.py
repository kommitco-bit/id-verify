# src/imaging.py
# Outils d'image : chargement, gris, sauvegarde, flou, resize, seuillage, Canny (J5).

import sys
from pathlib import Path

import cv2
import numpy as np

from config import SAMPLES_DIR


def load_image(path: str) -> np.ndarray | None:
    img = cv2.imread(path)
    if img is None:
        print(f"ERREUR : impossible de lire {path}")
        return None
    return img


def describe_image(img: np.ndarray) -> tuple[int, int, int]:
    h, w = img.shape[:2]
    c = img.shape[2] if img.ndim == 3 else 1
    return h, w, c


def to_grayscale(img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def save_image(img: np.ndarray, path: str) -> bool:
    ok = cv2.imwrite(path, img)
    if not ok:
        print(f"ERREUR : impossible d'écrire {path}")
    return ok


def apply_blur(img: np.ndarray, kernel_size: int = 5) -> np.ndarray | None:
    if img is None:
        return None
    k = max(3, kernel_size)
    if k % 2 == 0:
        k += 1
    return cv2.GaussianBlur(img, (k, k), 0)


def resize_image(img: np.ndarray, width: int, height: int) -> np.ndarray | None:
    if img is None or width <= 0 or height <= 0:
        return None
    h0, w0 = img.shape[:2]
    interp = cv2.INTER_AREA if (width * height) < (w0 * h0) else cv2.INTER_LINEAR
    return cv2.resize(img, (width, height), interpolation=interp)


def apply_threshold(gray: np.ndarray, threshold: int = 127) -> np.ndarray | None:
    if gray is None:
        return None
    if gray.ndim == 3:
        gray = to_grayscale(gray)
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    return binary


def apply_otsu(gray: np.ndarray) -> np.ndarray | None:
    if gray is None:
        return None
    if gray.ndim == 3:
        gray = to_grayscale(gray)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


def detect_edges(img: np.ndarray, low: int = 50, high: int = 150) -> np.ndarray | None:
    """Canny : contours blancs sur fond noir. Flou léger préalable recommandé."""
    if img is None:
        return None
    # Canny n'accepte qu'une image 1 canal.
    if img.ndim == 3:
        img = to_grayscale(img)
    # Flou léger pour atténuer le bruit avant le calcul du gradient.
    img = cv2.GaussianBlur(img, (5, 5), 0)
    return cv2.Canny(img, low, high)


def demo_gray(input_path: str) -> None:
    img = load_image(input_path)
    if img is None:
        return
    h, w, c = describe_image(img)
    print(f"Image chargée : {w}x{h}, {c} canaux")
    gray = to_grayscale(img)
    out = str(Path(input_path).with_name(Path(input_path).stem + "_gray.jpg"))
    if save_image(gray, out):
        print(f"OK : gris sauvegardé -> {out}")


def demo_blur(input_path: str, kernel_size: int = 5) -> None:
    img = load_image(input_path)
    if img is None:
        return
    blurred = apply_blur(img, kernel_size)
    if blurred is None:
        return
    out = str(Path(input_path).with_name(Path(input_path).stem + "_blur.jpg"))
    if save_image(blurred, out):
        print(f"OK : flou (k={kernel_size}) sauvegardé -> {out}")


def demo_resize(input_path: str, width: int = 500, height: int = 315) -> None:
    img = load_image(input_path)
    if img is None:
        return
    resized = resize_image(img, width, height)
    if resized is None:
        return
    out = str(
        Path(input_path).with_name(
            Path(input_path).stem + f"_resize_{width}x{height}.jpg"
        )
    )
    if save_image(resized, out):
        print(f"OK : resize {width}x{height} sauvegardé -> {out}")


def demo_threshold(input_path: str, threshold_value: int = 127) -> None:
    img = load_image(input_path)
    if img is None:
        return
    gray = to_grayscale(img)
    bin_fixed = apply_threshold(gray, threshold_value)
    bin_otsu = apply_otsu(gray)
    if bin_fixed is None or bin_otsu is None:
        return
    out_fixed = str(
        Path(input_path).with_name(
            Path(input_path).stem + f"_thr_{threshold_value}.jpg"
        )
    )
    out_otsu = str(Path(input_path).with_name(Path(input_path).stem + "_otsu.jpg"))
    if save_image(bin_fixed, out_fixed):
        print(f"OK : seuil fixe {threshold_value} -> {out_fixed}")
    if save_image(bin_otsu, out_otsu):
        print(f"OK : seuil Otsu -> {out_otsu}")


def demo_canny(input_path: str, low: int = 50, high: int = 150) -> None:
    img = load_image(input_path)
    if img is None:
        return
    edges = detect_edges(img, low, high)
    if edges is None:
        return
    out = str(
        Path(input_path).with_name(Path(input_path).stem + f"_canny_{low}_{high}.jpg")
    )
    if save_image(edges, out):
        print(f"OK : Canny ({low},{high}) -> {out}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage : python imaging.py data/samples/carte_fictive_01.jpg [kernel] [seuil] [low] [high]"
        )
        sys.exit(1)
    kernel = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    seuil = int(sys.argv[3]) if len(sys.argv) > 3 else 127
    low = int(sys.argv[4]) if len(sys.argv) > 4 else 50
    high = int(sys.argv[5]) if len(sys.argv) > 5 else 150
    src = sys.argv[1]
    demo_gray(src)
    demo_blur(src, kernel)
    demo_resize(src, 500, 315)
    demo_threshold(src, seuil)
    demo_canny(src, low, high)
