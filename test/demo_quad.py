# test/demo_quad.py
# v5 : seuil d'aire en % ET taille minimale en pixels absolus.
#       On accepte le plus grand quad si sa taille reelle est exploitable.

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


def quad_min_side(corners: np.ndarray) -> float:
    """Longueur du plus petit cote du quadrilatere."""
    sides = []
    for i in range(4):
        p1 = corners[i]
        p2 = corners[(i + 1) % 4]
        sides.append(float(np.linalg.norm(p1 - p2)))
    return min(sides)


def find_card_quad(img: np.ndarray, debug: bool = False):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    _, otsu = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    edges = cv2.Canny(otsu, 50, 150)
    kernel = np.ones((5, 5), np.uint8)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    img_area = img.shape[0] * img.shape[1]

    quads = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < 0.02 * img_area:  # < 2% = bruit
            continue
        hull = cv2.convexHull(c)
        peri = cv2.arcLength(hull, True)
        for eps_ratio in (0.01, 0.02, 0.03, 0.05, 0.08):
            approx = cv2.approxPolyDP(hull, eps_ratio * peri, True)
            if len(approx) != 4 or not cv2.isContourConvex(approx):
                continue
            x, y, w, h = cv2.boundingRect(approx)
            if w * h == 0:
                continue
            rect = cv2.contourArea(approx) / (w * h)
            if rect < 0.55:
                continue
            quads.append(approx)

    if not quads:
        print("[debug] aucun candidat")
        return None

    quads.sort(key=cv2.contourArea, reverse=True)
    best = quads[0]
    area_best = cv2.contourArea(best)
    ordered = order_corners(best)
    min_side = quad_min_side(ordered)

    if debug:
        print(
            f"[debug] meilleur : aire={area_best:.0f} ({area_best / img_area * 100:.1f}%) "
            f"cote_min={min_side:.0f}px"
        )
        for lab, (xx, yy) in zip(["TL", "TR", "BR", "BL"], ordered):
            print(f"[debug]   {lab} = ({xx:.0f}, {yy:.0f})")

    # Double critere : la carte doit etre assez grande EN % ET en PIXELS
    if area_best < 0.05 * img_area:
        print("[debug] rejete : trop petit en %")
        return None
    if min_side < 150:
        print("[debug] rejete : cote trop court (< 150 px)")
        return None
    return ordered


def draw_quad(img: np.ndarray, corners: np.ndarray) -> np.ndarray:
    out = img.copy()
    cv2.polylines(out, [corners.astype(np.int32)], True, (0, 255, 0), 3)
    colors = [(0, 0, 255), (0, 255, 255), (255, 0, 0), (255, 0, 255)]
    labels = ["TL", "TR", "BR", "BL"]
    for (x, y), col, lab in zip(corners, colors, labels):
        cv2.circle(out, (int(x), int(y)), 8, col, -1)
        cv2.putText(
            out, lab, (int(x) + 10, int(y) - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.7, col, 2
        )
    return out


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage : python test/demo_quad.py <image>")
        return
    img = imaging.load_image(sys.argv[1])
    if img is None:
        print("Impossible de lire l'image.")
        return
    print(f"Image chargee : {img.shape}")
    corners = find_card_quad(img, debug=True)
    if corners is None:
        print("Aucun quadrilatere trouve.")
        return
    print("4 coins (TL, TR, BR, BL) :")
    for lab, (x, y) in zip(["TL", "TR", "BR", "BL"], corners):
        print(f"  {lab} = ({x:.0f}, {y:.0f})")
    cv2.imshow("Coins detectes", draw_quad(img, corners))
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
