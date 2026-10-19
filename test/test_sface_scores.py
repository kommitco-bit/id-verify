# test/test_sface_scores.py
# Calcule toutes les paires d'un petit jeu (même personne vs différentes)
# et suggère un seuil SFace.

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import cv2

from face import compare, get_embedding

ROOT = os.path.join(os.path.dirname(__file__), "..")
SAMPLES = os.path.join(ROOT, "data", "samples")

# (personne_id, nom_de_fichier) — ADAPTER à tes vrais noms de fichiers.
ITEMS = [
    ("A", "pers_a_1.jpg"),
    ("A", "pers_a_2.jpg"),
    ("B", "pers_b_1.jpg"),
    ("B", "pers_b_2.jpg"),
    ("C", "pers_c_1.png"),
    ("C", "pers_c_2.png"),
]


def main():
    embs = []
    for pid, name in ITEMS:
        path = os.path.join(SAMPLES, name)
        img = cv2.imread(path)
        if img is None:
            print(f"[ERREUR] image introuvable : {path}")
            return
        e = get_embedding(img)
        if e is None:
            print(f"[ERREUR] aucun visage détecté : {name}")
            return
        embs.append((pid, name, e))
        print(f"OK  {pid}  {name}  shape={e.shape}")

    print("\n--- Scores (toutes paires) ---")
    rows = []
    for (pa, na, ea), (pb, nb, eb) in itertools.combinations(embs, 2):
        s = compare(ea, eb)
        same = pa == pb
        rows.append((s, same, na, nb))
        tag = "MÊME" if same else "DIFF"
        print(f"{tag:4s}  {na:20s} vs {nb:20s}  score={s:.4f}")

    scores_same = [r[0] for r in rows if r[1]]
    scores_diff = [r[0] for r in rows if not r[1]]
    print("\n--- Bilan ---")
    print(f"n_paires_meme_personne = {len(scores_same)}")
    print(f"n_paires_differentes   = {len(scores_diff)}")
    if scores_same:
        print(f"min(score même) = {min(scores_same):.4f}")
    if scores_diff:
        print(f"max(score diff) = {max(scores_diff):.4f}")

    if scores_same and scores_diff:
        lo = max(scores_diff)
        hi = min(scores_same)
        if hi > lo:
            seuil = (lo + hi) / 2.0
            print(f"SÉPARATION OK. Seuil suggéré (mi-chemin) = {seuil:.4f}")
            print(f"  marge basse (min_same - seuil) = {hi - seuil:.4f}")
            print(f"  marge haute (seuil - max_diff) = {seuil - lo:.4f}")
        else:
            print("ATTENTION : recouvrement (min_same <= max_diff).")
            print(
                "  Revoir les photos (angle, lumière, netteté) ou accepter un compromis."
            )


if __name__ == "__main__":
    main()
