# src/vector_search.py
# J11 : recherche vectorielle par force brute numpy.
# find_nearest(embedding, k=3) compare l'embedding a tous ceux en base
# et renvoie les k plus proches, du meilleur au pire.
# Contrat section 6 : entree = np.ndarray float32 (128,), sortie = list[(id, score)].

import sqlite3

import numpy as np

from database import DB_PATH
from face import compare


def find_nearest(embedding: np.ndarray, k: int = 3) -> list[tuple[int, float]]:
    # Garde-fous : bug de code = lever, donnee absente = liste vide.
    if embedding is None:
        return []
    if not isinstance(embedding, np.ndarray):
        raise TypeError("embedding doit etre un np.ndarray")
    if embedding.dtype != np.float32:
        raise ValueError(f"dtype attendu float32, recu {embedding.dtype}")
    if embedding.shape != (128,):
        raise ValueError(f"shape attendu (128,), recu {embedding.shape}")
    if k <= 0:
        return []

    # Lecture de tous les embeddings (force brute : pas d'index).
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute("SELECT id, embedding FROM persons").fetchall()
    finally:
        conn.close()

    # Comparaison un-a-un avec compare() (cosinus, teste J9).
    scored: list[tuple[int, float]] = []
    for person_id, blob in rows:
        if blob is None:
            continue
        stored = np.frombuffer(blob, dtype=np.float32)
        if stored.shape != (128,):
            continue  # ligne corrompue : ignorer plutot que planter
        score = compare(embedding, stored)
        if score is None:
            continue
        scored.append((person_id, score))

    # Tri du meilleur au pire, on ne garde que les k premiers.
    scored.sort(key=lambda t: t[1], reverse=True)
    return scored[:k]


if __name__ == "__main__":
    # Auto-test rapide : on se cherche soi-meme, on doit se retrouver 1er.
    import database

    person = database.get_person_by_number("FICT-001")
    if person is None:
        print("FICT-001 absent : lance test/test_enroll_5.py d'abord.")
    else:
        print(f"Requete : {person['numero']} {person['nom']} {person['prenom']}")
        for pid, score in find_nearest(person["embedding"], k=3):
            print(f"  id={pid}  score={score:.4f}")
