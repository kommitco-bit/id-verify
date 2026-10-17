# test/demo_perspective.py
# Demo : a partir de 4 coins connus, on redresse la carte en 1000x630.
# Ne fait PAS de detection : les coins sont fournis (ici, cadre central simule).
# Ne fait PAS partie du contrat §6.

import sys
from pathlib import Path

import cv2
import numpy as np

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

import imaging  # noqa: E402


def order_corners(pts: np.ndarray) -> np.ndarray:
    pts = pts.reshape(4, 2).astype(np.float32)
    s = pts.sum(axis=1)
    tl = pts[np.argmin(s)]
    br = pts[np.argmax(s)]
    d = np.diff(pts, axis=1).ravel()
    tr = pts[np.argmin(d)]
    bl = pts[np.argmax(d)]
    return np.array([tl, tr, br, bl], dtype=np.float32)


def warp_card(
    img: np.ndarray, corners: np.ndarray, width: int = 1000, height: int = 630
) -> np.ndarray:
    """Applique la transformation de perspective : 4 coins -> rectangle width x height."""
    dst = np.array(
        [
            [0, 0],
            [width - 1, 0],
            [width - 1, height - 1],
            [0, height - 1],
        ],
        dtype=np.float32,
    )
    matrix = cv2.getPerspectiveTransform(corners, dst)
    return cv2.warpPerspective(img, matrix, (width, height))


def central_frame(img: np.ndarray, margin: float = 0.10) -> np.ndarray:
    """Simule un cadre-guide : 4 coins d'une zone centrale (10% de marge)."""
    h, w = img.shape[:2]
    mx, my = int(w * margin), int(h * margin)
    pts = np.array(
        [
            [mx, my],
            [w - mx, my],
            [w - mx, h - my],
            [mx, h - my],
        ],
        dtype=np.float32,
    )
    return order_corners(pts)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage : python test/demo_perspective.py <image>")
        return
    img = imaging.load_image(sys.argv[1])
    if img is None:
        print("Impossible de lire l'image.")
        return
    print(f"Image chargee : {img.shape}")

    # 1. Simule un cadre-guide (10% de marge) -- equivalent d'un utilisateur qui aligne la carte
    corners = central_frame(img, margin=0.10)
    print("Coins du cadre simule (TL, TR, BR, BL) :")
    for lab, (x, y) in zip(["TL", "TR", "BR", "BL"], corners):
        print(f"  {lab} = ({x:.0f}, {y:.0f})")

    # 2. Dessine le cadre sur l'original pour verifier visuellement
    vis = img.copy()
    cv2.polylines(vis, [corners.astype(np.int32)], True, (0, 255, 0), 3)
    cv2.imshow("1/2 - Cadre simule (appuie pour continuer)", vis)
    cv2.waitKey(0)

    # 3. Redresse en 1000x630
    flat = warp_card(img, corners)
    print(f"Carte redressee : {flat.shape}")
    cv2.imshow("2/2 - Carte redressee 1000x630 (appuie pour fermer)", flat)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # 4. Sauvegarde pour inspection
    out_path = Path("test") / (Path(sys.argv[1]).stem + "_flat.jpg")
    cv2.imwrite(str(out_path), flat)
    print(f"Sauvegarde : {out_path}")


if __name__ == "__main__":
    main()
