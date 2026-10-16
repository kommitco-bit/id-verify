"""Module imaging — opérations de base sur les images.

J1 : charger une image, afficher sa taille, la passer en niveaux de gris
et la sauvegarder. Le redressement de carte (prepare_card) viendra plus tard.
"""

from pathlib import Path

import cv2
import numpy as np

from config import SAMPLES_DIR, ensure_dirs


def load_image(path: str) -> np.ndarray | None:
    """Charge une image depuis le disque.

    Entrée : chemin vers un fichier image.
    Sortie : tableau numpy BGR, ou None si le fichier est introuvable/illisible.
    """
    p = Path(path)
    if not p.exists():
        print(f"[imaging] Fichier introuvable : {p}")
        return None

    img = cv2.imread(str(p), cv2.IMREAD_COLOR)
    if img is None:
        print(f"[imaging] Impossible de lire l'image : {p}")
        return None

    return img


def describe_image(img: np.ndarray) -> tuple[int, int, int]:
    """Renvoie (hauteur, largeur, nombre_de_canaux) d'une image BGR."""
    h, w = img.shape[:2]
    c = img.shape[2] if img.ndim == 3 else 1
    return h, w, c


def to_grayscale(img: np.ndarray) -> np.ndarray:
    """Convertit une image BGR en niveaux de gris (1 canal)."""
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def save_image(img: np.ndarray, path: str) -> bool:
    """Sauvegarde une image sur le disque.

    Renvoie True si l'écriture a réussi, False sinon.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    ok = cv2.imwrite(str(p), img)
    if not ok:
        print(f"[imaging] Échec de l'écriture : {p}")
    return ok


def demo_gray(input_path: str) -> None:
    """Scénario J1 : charge, décrit, passe en gris, sauvegarde."""
    ensure_dirs()

    img = load_image(input_path)
    if img is None:
        return

    h, w, c = describe_image(img)
    print(f"Image chargée : {w} x {h} pixels, {c} canal(aux).")

    gray = to_grayscale(img)

    stem = Path(input_path).stem
    out_path = SAMPLES_DIR / f"{stem}_gray.jpg"
    if save_image(gray, str(out_path)):
        print(f"Image grise sauvegardée : {out_path}")


if __name__ == "__main__":
    # Test rapide : remplace par le chemin d'une image de test.
    # Exemple : une photo quelconque dans data/samples/.
    import sys

    if len(sys.argv) < 2:
        print("Usage : python src/imaging.py <chemin_image>")
    else:
        demo_gray(sys.argv[1])
