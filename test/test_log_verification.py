"""Test J10 : log_verification écrit 2 passages et on les relit (JSON rond)."""

import json
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import database


def read_all_verifications() -> list[dict]:
    """Relit toutes les lignes de verifications, scores désérialisés."""
    with sqlite3.connect(database.DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, person_id, status, scores, created_at "
            "FROM verifications ORDER BY id"
        ).fetchall()
    result = []
    for row in rows:
        d = dict(row)
        d["scores"] = json.loads(d["scores"]) if d["scores"] else None
        result.append(d)
    return result


def main() -> None:
    database.init_db()

    # Personne factice minimale pour garantir la FK (si PRAGMA activé).
    if database.get_person_by_number("FICT-001") is None:
        import numpy as np

        emb = np.zeros(128, dtype=np.float32)
        database.add_person(
            {
                "nom": "DUPONT",
                "postnom": "X",
                "prenom": "Jean",
                "date_naissance": "1990-01-01",
                "numero": "FICT-001",
            },
            emb,
        )

    print("=== Insertion 2 passages ===")
    database.log_verification(1, "VALIDE", {"face": 0.62, "ocr": 1.0})
    print("  [OK] passage 1 : VALIDE")
    database.log_verification(None, "ANOMALIE", {"ocr": 0.0})
    print("  [OK] passage 2 : ANOMALIE")

    print("=== Relecture ===")
    rows = read_all_verifications()
    for r in rows:
        print(
            f"  id={r['id']} person_id={r['person_id']} "
            f"status={r['status']} scores={r['scores']} "
            f"created_at={r['created_at']}"
        )

    print("=== Contrôle d'intégrité ===")
    expected = [
        {"face": 0.62, "ocr": 1.0},
        {"ocr": 0.0},
    ]
    ok = (
        len(rows) >= 2
        and rows[-2]["scores"] == expected[0]
        and rows[-1]["scores"] == expected[1]
        and rows[-2]["status"] == "VALIDE"
        and rows[-1]["status"] == "ANOMALIE"
        and rows[-1]["person_id"] is None
    )
    print(f"  [{'OK' if ok else 'KO'}] scores == origine, statuts corrects")


if __name__ == "__main__":
    main()
