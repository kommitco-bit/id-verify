# src/imaging.py
# Outils d'image : chargement, gris, sauvegarde, et (J5) flou gaussien.
# Identifiants en anglais (snake_case), commentaires en français.

import sys
from pathlib import Path

import cv2
import numpy as np

from config import SAMPLES_DIR


def load_image(path: str) -> np.ndarray | None:
    """Charge une image en BGR. Renvoie None en cas d'échec."""
    img = cv2.imread(path)
    if img is None:
        print(f"ERREUR : impossible de lire {path}")
        return None
    return img


def describe_image(img: np.ndarray) -> tuple[int, int, int]:
    """Renvoie (hauteur, largeur, canaux) d'une image."""
    h, w = img.shape[:2]
    c = img.shape[2] if img.ndim == 3 else 1
    return h, w, c


def to_grayscale(img: np.ndarray) -> np.ndarray:
    """Convertit une image BGR en niveaux de gris (1 canal)."""
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def save_image(img: np.ndarray, path: str) -> bool:
    """Sauvegarde une image. Renvoie True si succès, False sinon."""
    ok = cv2.imwrite(path, img)
    if not ok:
        print(f"ERREUR : impossible d'écrire {path}")
    return ok


def apply_blur(img: np.ndarray, kernel_size: int = 5) -> np.ndarray | None:
    """Applique un flou gaussien. kernel_size doit être impair (3, 5, 7...)."""
    if img is None:
        return None
    # Un noyau gaussien doit être impair et >= 3, sinon OpenCV lève une erreur.
    k = max(3, kernel_size)
    if k % 2 == 0:
        k += 1
    return cv2.GaussianBlur(img, (k, k), 0)


def demo_gray(input_path: str) -> None:
    """Démo existante (J1) : charge, décrit, convertit en gris, sauvegarde."""
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
    """Démo J5 : flou gaussien et sauvegarde pour comparaison visuelle."""
    img = load_image(input_path)
    if img is None:
        return
    blurred = apply_blur(img, kernel_size)
    if blurred is None:
        return
    out = str(Path(input_path).with_name(Path(input_path).stem + "_blur.jpg"))
    if save_image(blurred, out):
        print(f"OK : flou (k={kernel_size}) sauvegardé -> {out}")


if __name__ == "__main__":
    # Usage : python imaging.py <chemin_image> [kernel]
    if len(sys.argv) < 2:
        print("Usage : python imaging.py data/samples/carte_fictive_01.jpg [kernel]")
        sys.exit(1)
    kernel = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    src = sys.argv[1]
    demo_gray(src)
    demo_blur(src, kernel)
