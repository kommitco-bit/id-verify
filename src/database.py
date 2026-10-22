"""Base de données SQLite — id-verif. J10 V3 : 4 fonctions du contrat §6."""

import json
import sqlite3
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "db" / "id_verif.db"

VALID_STATUSES = {"VALIDE", "ANOMALIE", "VERIFICATION_COMPLEMENTAIRE"}


def init_db() -> None:
    """Crée le fichier et les tables persons / verifications si absentes."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS persons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT, postnom TEXT, prenom TEXT, date_naissance TEXT,
            numero TEXT NOT NULL UNIQUE, embedding BLOB)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS verifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT, person_id INTEGER,
            status TEXT, scores TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (person_id) REFERENCES persons(id))""")
        conn.commit()


def add_person(fields: dict, embedding: np.ndarray) -> int | None:
    """Insère une personne, renvoie son id. embedding : float32 (128,)."""
    if not isinstance(embedding, np.ndarray):
        raise TypeError("embedding doit être un np.ndarray")
    if embedding.dtype != np.float32:
        raise ValueError(f"dtype attendu float32, reçu {embedding.dtype}")
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "INSERT INTO persons (nom, postnom, prenom, date_naissance, numero, embedding)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (
                fields.get("nom"),
                fields.get("postnom"),
                fields.get("prenom"),
                fields.get("date_naissance"),
                fields.get("numero"),
                embedding.tobytes(),
            ),
        )
        conn.commit()
        return cur.lastrowid


def get_person_by_number(numero: str) -> dict | None:
    """Renvoie dict complet ou None. embedding redevient np.ndarray float32."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM persons WHERE numero = ?", (numero,)
        ).fetchone()
    if row is None:
        return None
    person = dict(row)
    if person["embedding"] is not None:
        person["embedding"] = np.frombuffer(person["embedding"], dtype=np.float32)
    return person


def log_verification(person_id: int | None, status: str, scores: dict) -> None:
    """Logue un passage. status ∈ {VALIDE, ANOMALIE, VERIFICATION_COMPLEMENTAIRE}."""
    if status not in VALID_STATUSES:
        raise ValueError(f"status invalide : {status!r}")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO verifications (person_id, status, scores) VALUES (?, ?, ?)",
            (person_id, status, json.dumps(scores, ensure_ascii=False, default=float)),
        )
        conn.commit()


if __name__ == "__main__":
    init_db()
    print(f"Base initialisée : {DB_PATH}")
