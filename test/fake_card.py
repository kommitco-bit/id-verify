"""Generateur de cartes fictives style 'carte officielle' (RDC-like).

Outil de test uniquement. Hors contrat d'interfaces (brief section 6).
Genere 10 cartes fictives dans data/samples/ a partir de :
  - donnees 100% inventees (noms, dates, adresses, numeros) ;
  - 10 visages dans data/samples/faces/ (fictifs ou consentants).

Aucune donnee reelle. Aucune dependance en plus d'opencv + numpy + random.
"""

import random
from pathlib import Path

import cv2
import numpy as np

from config import CARD_HEIGHT, CARD_WIDTH, SAMPLES_DIR

SEED = 42
FACES_DIR = SAMPLES_DIR / "faces"

LAST_NAMES = ["DUPONT", "MARTIN", "NGOMA", "KABILA", "TRAORE",
              "BERNARD", "MUKENDI", "PETIT", "ROBERT", "DIALLO"]
FIRST_NAMES = ["Alice", "Bruno", "Chantal", "David", "Esther",
               "Firmin", "Grace", "Hugo", "Ines", "Joseph"]
BIRTH_PLACES = ["Kinshasa", "Paris", "Bruxelles", "Abidjan",
                "Montreal", "Lyon", "Dakar", "Lubumbashi"]
CITIES = ["Kinshasa", "Lubumbashi", "Goma", "Matadi", "Bukavu",
          "Paris", "Bruxelles", "Montreal"]
STREETS = ["Av. de la Paix", "Rue du Marche", "Bd. Lumumba",
           "Av. des Palmiers", "Rue 12", "Bd. Central"]


def _rand_date(rng: random.Random, y_min: int, y_max: int) -> str:
    """Retourne une date fictive JJ/MM/AAAA."""
    return f"{rng.randint(1,28):02d}/{rng.randint(1,12):02d}/{rng.randint(y_min,y_max)}"


def _rand_number(rng: random.Random) -> str:
    """Numero d'electeur fictif au format 'A 1234567'."""
    return f"{rng.choice('ABCDEFGH')} {rng.randint(1000000, 9999999)}"


def _rand_code(rng: random.Random) -> str:
    """Code fictif au format 'XXXXX/XXXX'."""
    return f"{rng.randint(10000,99999)}/{rng.randint(1000,9999)}"


def _draw_fake_qr(img, x: int, y: int, size: int, rng: random.Random) -> None:
    """Dessine un motif 'QR factice' (non scannable) dans la zone indiquee."""
    cv2.rectangle(img, (x, y), (x + size, y + size), (0, 0, 0), 2)
    cell = size // 12
    for row in range(12):
        for col in range(12):
            if rng.random() < 0.45:
                px = x + 4 + col * cell
                py = y + 4 + row * cell
                cv2.rectangle(img, (px, py), (px + cell - 1, py + cell - 1),
                              (0, 0, 0), -1)


def _paste_face(card, face_path: Path) -> None:
    """Colle le visage dans la zone photo (rognage centre + resize)."""
    face = cv2.imread(str(face_path))
    if face is None:
        return
    zx, zy, zw, zh = 40, 190, 260, 320  # zone photo
    target_ratio = zw / zh
    h, w = face.shape[:2]
    if w / h > target_ratio:                # image trop large -> rogner largeur
        new_w = int(h * target_ratio)
        x0 = (w - new_w) // 2
        face = face[:, x0:x0 + new_w]
    else:                                    # image trop haute -> rogner hauteur
        new_h = int(w / target_ratio)
        y0 = (h - new_h) // 2
        face = face[y0:y0 + new_h, :]
    face = cv2.resize(face, (zw, zh))
    card[zy:zy + zh, zx:zx + zw] = face
    cv2.rectangle(card, (zx, zy), (zx + zw, zy + zh), (30, 30, 30), 2)


def make_one_card(index: int, rng: random.Random, face_path: Path) -> Path:
    """Genere une carte fictive style 'carte officielle'. Retourne le chemin."""
    card = np.full((CARD_HEIGHT, CARD_WIDTH, 3), 245, dtype=np.uint8)

    # Bandeau titre (bleu fonce) + sous-bandeau.
    cv2.rectangle(card, (0, 0), (CARD_WIDTH, 110), (140, 60, 20), -1)
    cv2.rectangle(card, (0, 110), (CARD_WIDTH, 145), (200, 200, 200), -1)
    cv2.putText(card, "REPUBLIQUE FICTIVE", (20, 45),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(card, "COMMISSION ELECTORALE FICTIVE", (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(card, "CARTE D'ELECTEUR", (20, 135),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (20, 20, 20), 2, cv2.LINE_AA)
    cv2.putText(card, "DUPLICATA", (CARD_WIDTH - 230, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

    # Champs fictifs.
    nom = rng.choice(LAST_NAMES)
    postnom = rng.choice(LAST_NAMES)
    prenom = rng.choice(FIRST_NAMES)
    sexe = rng.choice(["M", "F"])
    naiss = _rand_date(rng, 1960, 2005)
    deliv = _rand_date(rng, 2018, 2024)
    numero = _rand_number(rng)
    code = _rand_code(rng)
    adresse = f"{rng.randint(1,200)}, {rng.choice(STREETS)}, {rng.choice(CITIES)}"
    origine = f"{rng.choice(CITIES)}/{rng.choice(CITIES)}"
    pere = f"{rng.choice(LAST_NAMES)} {rng.choice(FIRST_NAMES)}"
    mere = f"{rng.choice(LAST_NAMES)} {rng.choice(FIRST_NAMES)}"

    # Colonne droite (texte).
    x = 330
    y = 185
    def line(txt, dy=38, scale=0.75):
        nonlocal y
        cv2.putText(card, txt, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                    scale, (20, 20, 20), 2, cv2.LINE_AA)
        y += dy

    line(f"Nom : {nom}", dy=34)
    line(f"Postnom/Prenom : {postnom}/{prenom}", dy=34)
    line(f"Date / Lieu de naissance : {naiss}", dy=34)
    line(f"Sexe : {sexe}", dy=34)
    line(f"Adresse : {adresse}", scale=0.62, dy=34)
    line(f"Origine : {origine}", scale=0.62, dy=34)

    # Colonne gauche : code + numero sous le bandeau.
    cv2.putText(card, f"CODE : {code}", (330, 165),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (60, 60, 60), 1, cv2.LINE_AA)
    cv2.putText(card, f"N.I. : {numero}", (330, 430),
                cv2.FONT_HERSHEY_SIMPLEX, 0.85, (20, 20, 20), 2, cv2.LINE_AA)

    # Zone photo (gauche) + QR factice (droite).
    _paste_face(card, face_path)
    _draw_fake_qr(card, CARD_WIDTH - 240, 200, 200, rng)

    # Bas de carte : filiation + delivrance.
    cv2.rectangle(card, (0, 500), (CARD_WIDTH, CARD_HEIGHT), (235, 235, 235), -1)
    cv2.putText(card, f"Nom du pere : {pere}", (20, 540),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (30, 30, 30), 1, cv2.LINE_AA)
    cv2.putText(card, f"Nom de la mere : {mere}", (20, 575),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (30, 30, 30), 1, cv2.LINE_AA)
    cv2.putText(card, f"Lieu et date de delivrance : {rng.choice(CITIES)} {deliv}",
                (500, 540), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (30, 30, 30),
                1, cv2.LINE_AA)

    out_path = SAMPLES_DIR / f"carte_fictive_{index:02d}.jpg"
    cv2.imwrite(str(out_path), card)
    return out_path


def main() -> None:
    """Genere 10 cartes fictives en associant 10 visages."""
    rng = random.Random(SEED)
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

    faces = sorted([p for p in FACES_DIR.iterdir()
                    if p.suffix.lower() in (".jpg", ".jpeg", ".png")])
    if not faces:
        print(f"Aucun visage dans {FACES_DIR}. Rectangle gris a la place.")
    else:
        print(f"{len(faces)} visage(s) trouve(s) dans {FACES_DIR}.")

    for i in range(1, 11):
        face = faces[(i - 1) % len(faces)] if faces else None
        path = make_one_card(i, rng, face) if face else None
        if path is None:
            # Pas de visage dispo : on genere quand meme la carte sans photo.
            path = make_one_card(i, rng, FACES_DIR / "_absent_")
        print(f"OK : {path.name}")

    print(f"\n10 cartes fictives generees dans : {SAMPLES_DIR}")


if __name__ == "__main__":
    main()