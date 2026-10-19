"""Module base de données SQLite — id-verif.

J10 V1 : init_db() uniquement (création du fichier + 2 tables).
"""

import sqlite3
from pathlib import Path

# Racine du projet = dossier parent de src/
# NOTE : à déplacer dans config.py (cf. PROPOSITION DE CHANGEMENT en bas).
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "db" / "id_verif.db"


def init_db() -> None:
    """Crée le fichier SQLite et les tables persons / verifications si absentes.

    Idempotent : appelable plusieurs fois sans erreur ni perte de données.
    """
    # 1) S'assurer que data/db/ existe (parents=True crée data/ aussi).
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # 2) Le "with" ferme la connexion automatiquement en cas d'erreur.
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        # Table persons : une ligne = une personne enrôlée.
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS persons (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                nom             TEXT,
                postnom         TEXT,
                prenom          TEXT,
                date_naissance  TEXT,
                numero          TEXT NOT NULL UNIQUE,
                embedding       BLOB
            )
            """
        )

        # Table verifications : une ligne = un passage dans le pipeline.
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS verifications (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id  INTEGER,
                status     TEXT,
                scores     TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (person_id) REFERENCES persons(id)
            )
            """
        )

        conn.commit()


if __name__ == "__main__":
    init_db()
    print(f"Base initialisée : {DB_PATH}")
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
    print("Tables :", [r[0] for r in rows])
