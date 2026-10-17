"""
Détecte une carte (identité, électeur, etc.) dans une photo, la redresse
(correction de perspective) et ne garde que la carte, sans bord de fond.

Installation : pip install opencv-python numpy
Usage        : python extraire_carte.py photo.jpg
               python extraire_carte.py dossier_photos/
"""

import sys
from pathlib import Path

import cv2
import numpy as np

# Format ISO ID-1 (85,6 x 54 mm) -> ratio 1,586
L_OUT, H_OUT = 1011, 638
MARGE = 0.06  # marge de sécurité de la 1re passe (évite de couper la carte)
ROGNAGE = 3  # pixels rognés à l'intérieur de la carte (supprime le liseré de fond)
TAILLE_DETECTION = 1000


# ---------------------------------------------------------------- géométrie
def ordonner_points(pts):
    """Ordre : haut-gauche, haut-droite, bas-droite, bas-gauche."""
    pts = pts.reshape(4, 2).astype("float32")
    somme = pts.sum(axis=1)
    diff = np.diff(pts, axis=1).ravel()
    return np.array(
        [
            pts[np.argmin(somme)],
            pts[np.argmin(diff)],
            pts[np.argmax(somme)],
            pts[np.argmax(diff)],
        ],
        dtype="float32",
    )


def intersection(p1, d1, p2, d2):
    A = np.array([d1, -d2], dtype=np.float64).T
    if abs(np.linalg.det(A)) < 1e-6:
        return None
    s, _ = np.linalg.solve(A, (p2 - p1).astype(np.float64))
    return p1 + s * d1


def affiner_quad(contour, quad, tol):
    """Ajuste une droite sur chaque côté réel de la carte puis intersecte les
    droites : donne les vrais coins, même avec des coins arrondis."""
    pts = contour.reshape(-1, 2).astype(np.float64)
    lignes = []
    for i in range(4):
        p = quad[i].astype(np.float64)
        q = quad[(i + 1) % 4].astype(np.float64)
        d = q - p
        longueur = np.linalg.norm(d)
        if longueur < 1:
            return quad
        u = d / longueur
        n = np.array([-u[1], u[0]])
        rel = pts - p
        t = rel @ u / longueur
        dist = np.abs(rel @ n)
        sel = pts[(t > 0.15) & (t < 0.85) & (dist < tol)]  # milieu du côté seulement
        if len(sel) >= 10:
            vx, vy, x0, y0 = cv2.fitLine(
                sel.astype(np.float32), cv2.DIST_HUBER, 0, 0.01, 0.01
            ).ravel()
            lignes.append((np.array([x0, y0]), np.array([vx, vy])))
        else:
            lignes.append((p, u))
    coins = []
    for i in range(4):
        c = intersection(*lignes[i - 1], *lignes[i])
        coins.append(c if c is not None else quad[i])
    return np.array(coins, dtype="float32")


# ---------------------------------------------------------------- détection
def quad_depuis_contour(c):
    hull = cv2.convexHull(c)
    per = cv2.arcLength(hull, True)
    approx = hull
    for eps in np.arange(0.005, 0.12, 0.005):  # plus petit epsilon donnant 4 points
        approx = cv2.approxPolyDP(hull, eps * per, True)
        if len(approx) <= 4:
            break
    if len(approx) == 4:
        return hull, approx.reshape(4, 2).astype("float32")
    return hull, cv2.boxPoints(cv2.minAreaRect(hull)).astype("float32")


def evaluer(masque, taille):
    """Retourne (score, forme, quad, contour) du meilleur contour du masque."""
    H, W = taille
    contours, _ = cv2.findContours(masque, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    meilleur = None
    for c in sorted(contours, key=cv2.contourArea, reverse=True)[:3]:
        aire = cv2.contourArea(c)
        frac = aire / (H * W)
        if frac < 0.08 or frac > 0.97:
            continue
        x, y, bw, bh = cv2.boundingRect(c)
        if x <= 2 and y <= 2 and x + bw >= W - 2 and y + bh >= H - 2:
            continue  # contour = toute l'image
        hull, quad = quad_depuis_contour(c)
        aire_hull = cv2.contourArea(hull)
        qa = cv2.contourArea(quad) / max(aire_hull, 1)
        forme = (aire / max(aire_hull, 1)) * min(qa, 1 / max(qa, 1e-6))
        score = forme * np.sqrt(frac)
        if meilleur is None or score > meilleur[0]:
            meilleur = (score, forme, quad, c)
    return meilleur


def detecter_quad(img):
    h, w = img.shape[:2]
    echelle = min(1.0, TAILLE_DETECTION / max(h, w))
    petit = cv2.resize(img, None, fx=echelle, fy=echelle, interpolation=cv2.INTER_AREA)
    H, W = petit.shape[:2]
    gris = cv2.GaussianBlur(cv2.cvtColor(petit, cv2.COLOR_BGR2GRAY), (7, 7), 0)
    ell = lambda k: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    candidats = []

    # A : contours (Canny) refermés
    bords = cv2.Canny(gris, 40, 120)
    candidats.append(evaluer(cv2.morphologyEx(bords, cv2.MORPH_CLOSE, ell(15)), (H, W)))

    # B : seuillage d'Otsu (fond uni clair ou sombre)
    _, m = cv2.threshold(gris, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cadre = np.concatenate([m[0], m[-1], m[:, 0], m[:, -1]])
    if cadre.mean() > 127:  # le fond est devenu blanc -> inverser
        m = 255 - m
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, ell(25))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, ell(9))
    candidats.append(evaluer(m, (H, W)))

    candidats = [c for c in candidats if c is not None]

    # C : GrabCut, seulement si A et B ne sont pas convaincants
    if not candidats or max(c[1] for c in candidats) < 0.93:
        masque = np.zeros((H, W), np.uint8)
        rect = (int(0.03 * W), int(0.03 * H), int(0.94 * W), int(0.94 * H))
        cv2.grabCut(
            petit,
            masque,
            rect,
            np.zeros((1, 65)),
            np.zeros((1, 65)),
            4,
            cv2.GC_INIT_WITH_RECT,
        )
        m = np.where((masque == 1) | (masque == 3), 255, 0).astype("uint8")
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, ell(9))
        c = evaluer(m, (H, W))
        if c is not None:
            candidats.append(c)

    if not candidats:
        return None
    _, _, quad, contour = max(candidats, key=lambda c: c[0])
    quad = affiner_quad(contour, ordonner_points(quad), tol=0.02 * max(H, W))
    return quad / echelle


# ---------------------------------------------------------------- extraction
def calculer_matrice(img):
    quad = detecter_quad(img)
    if quad is None:
        return None
    src = ordonner_points(quad)
    if np.linalg.norm(src[3] - src[0]) > np.linalg.norm(src[1] - src[0]):
        src = np.roll(src, -1, axis=0)  # carte en portrait -> la mettre à plat

    # Passe 1 : on redresse avec une marge de fond autour de la carte
    mx, my = int(MARGE * L_OUT), int(MARGE * H_OUT)
    CW, CH = L_OUT + 2 * mx, H_OUT + 2 * my
    dst1 = np.array(
        [
            [mx, my],
            [mx + L_OUT - 1, my],
            [mx + L_OUT - 1, my + H_OUT - 1],
            [mx, my + H_OUT - 1],
        ],
        "float32",
    )
    M1 = cv2.getPerspectiveTransform(src, dst1)
    canevas = cv2.warpPerspective(
        img, M1, (CW, CH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE
    )

    # Passe 2 : la carte est maintenant droite -> on resserre exactement sur ses bords
    quad2 = detecter_quad(canevas)
    if quad2 is not None:
        s2 = ordonner_points(quad2)
        if 0.6 < cv2.contourArea(s2) / (CW * CH) < 0.95:
            r = ROGNAGE
            dst2 = np.array(
                [
                    [-r, -r],
                    [L_OUT - 1 + r, -r],
                    [L_OUT - 1 + r, H_OUT - 1 + r],
                    [-r, H_OUT - 1 + r],
                ],
                "float32",
            )
            return cv2.getPerspectiveTransform(s2, dst2) @ M1

    T = np.array([[1, 0, -mx], [0, 1, -my], [0, 0, 1]], dtype=np.float64)  # secours
    return T @ M1


def extraire_carte(chemin, sortie=None, ameliorer=True):
    chemin = Path(chemin)
    img = cv2.imread(str(chemin))
    if img is None:
        print(f"Impossible de lire {chemin}")
        return False
    M = calculer_matrice(img)
    if M is None:
        print(f"Carte non détectée : {chemin.name}")
        return False

    carte = cv2.warpPerspective(
        img, M, (L_OUT, H_OUT), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )
    if ameliorer:  # contraste local sans brûler les couleurs (canal L uniquement)
        l, a, b = cv2.split(cv2.cvtColor(carte, cv2.COLOR_BGR2LAB))
        l = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(l)
        carte = cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2BGR)

    sortie = Path(sortie) if sortie else chemin.with_name(f"{chemin.stem}_carte.jpg")
    cv2.imwrite(str(sortie), carte, [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"OK : {sortie}")
    return str(sortie)


if __name__ == "__main__":
    cible = Path(sys.argv[1] if len(sys.argv) > 1 else "photo.jpg")
    if cible.is_dir():
        for f in sorted(cible.iterdir()):
            if (
                f.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
                and "_carte" not in f.stem
            ):
                extraire_carte(f)
    else:
        extraire_carte(cible)
