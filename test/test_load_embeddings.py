# test/test_load_embeddings.py
# Mini-test J11 : lire les embeddings stockes dans SQLite et les afficher.
# Ne fait AUCUNE recherche : on verifie juste qu'on a de quoi chercher.

import sqlite3
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import database  # noqa: E402


def main() -> None:
    database.init_db()  # idempotent : ne casse rien si les tables existent

    conn = sqlite3.connect(database.DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT id, numero, nom, prenom, embedding FROM persons ORDER BY id"
        ).fetchall()
    finally:
        conn.close()

    if not rows:
        print("Aucune personne en base. Lance test/test_enroll_5.py d'abord.")
        return

    print(f"{len(rows)} personne(s) en base :")
    for row in rows:
        blob = row["embedding"]
        if blob is None:
            print(f"  id={row['id']:>2}  numero={row['numero']:<10}  (embedding NULL)")
            continue
        emb = np.frombuffer(blob, dtype=np.float32)
        norme = float(np.linalg.norm(emb))
        prenom = row["prenom"] or ""
        nom = row["nom"] or "?"
        print(
            f"  id={row['id']:>2}  numero={row['numero']:<10} "
            f"nom={nom} {prenom}  "
            f"shape={emb.shape} dtype={emb.dtype} norme={norme:.2f}"
        )


if __name__ == "__main__":
    main()
