# src/demo_steps.py
# Démo visuelle J5 : affiche toutes les étapes d'image côte à côte.
# Outil pédagogique, HORS contrat §6.

import sys

import cv2
import numpy as np

from imaging import (
    apply_blur,
    apply_otsu,
    apply_threshold,
    detect_edges,
    load_image,
    resize_image,
    to_grayscale,
)


def to_bgr3(img: np.ndarray) -> np.ndarray:
    """Force une image en 3 canaux BGR pour pouvoir l'empiler avec les autres."""
    if img.ndim == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return img


def label(img: np.ndarray, text: str) -> np.ndarray:
    """Ajoute une bande noire avec un texte au-dessus de l'image (pour l'affichage)."""
    band_h = 30
    w = img.shape[1]
    band = np.zeros((band_h, w, 3), dtype=np.uint8)
    cv2.putText(
        band,
        text,
        (8, 22),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )
    return np.vstack([band, img])


def make_grid(input_path: str) -> np.ndarray | None:
    """Construit la grille 2x3 des étapes : original, gris, flou, seuil, Otsu, Canny."""
    img = load_image(input_path)
    if img is None:
        return None

    # On réduit d'abord : sinon la fenêtre est plus grande que l'écran 8 Go.
    img = resize_image(img, 500, 315)
    if img is None:
        return None

    gray = to_grayscale(img)
    blurred = apply_blur(img, 5)
    thr_fixed = apply_threshold(gray, 127)
    otsu = apply_otsu(gray)
    edges = detect_edges(img, 50, 150)

    # Toutes les images doivent être en 3 canaux BGR et de même taille pour empiler.
    tiles = [
        label(to_bgr3(img), "1. Original"),
        label(to_bgr3(gray), "2. Gris"),
        label(to_bgr3(blurred), "3. Flou gaussien k=5"),
        label(to_bgr3(thr_fixed), "4. Seuil fixe 127"),
        label(to_bgr3(otsu), "5. Seuil Otsu"),
        label(to_bgr3(edges), "6. Canny 50/150"),
    ]

    row1 = np.hstack(tiles[0:3])
    row2 = np.hstack(tiles[3:6])
    return np.vstack([row1, row2])


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage : python demo_steps.py data/samples/carte_fictive_01.jpg")
        sys.exit(1)

    grid = make_grid(sys.argv[1])
    if grid is None:
        print("ERREUR : grille non générée.")
        sys.exit(1)

    print(
        f"Grille : {grid.shape[1]}x{grid.shape[0]} px — appuie sur une touche pour fermer."
    )
    cv2.imshow("Etapes J5", grid)
    cv2.waitKey(0)  # attend une touche
    cv2.destroyAllWindows()  # ferme la fenêtre proprement


if __name__ == "__main__":
    main()
