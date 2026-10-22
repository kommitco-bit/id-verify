"""Tests J12 : 8 scénarios pour decision.decide()."""

import sys

sys.path.insert(0, "src")
import numpy as np

from decision import decide

# Empreintes factices : identiques → cosinus ≈ 1.0 ; orthogonales → cosinus ≈ 0.09.
EMB_A = np.ones(128, dtype=np.float32)
EMB_B = np.zeros(128, dtype=np.float32)
EMB_B[0] = 1.0

FIELDS_OK = {
    "raw_text": "x",
    "numero": "FICT-001",
    "nom": "KABILA",
    "prenom": "Jean",
    "date_naissance": "01/01/1990",
}
PERSON_OK = {"numero": "FICT-001", "nom": "KABILA"}


def run(name, fields, card, live, person, expected):
    """Exécute un scénario et vérifie le statut retourné."""
    r = decide(fields, card, live, person)
    ok = r["status"] == expected
    print(f"[{'OK' if ok else 'FAIL'}] {name}: {r['status']} (attendu {expected})")
    if not ok:
        print(f"      reasons={r['reasons']}")
    return ok


if __name__ == "__main__":
    results = [
        run("1 cas normal", FIELDS_OK, EMB_A, EMB_A, PERSON_OK, "VALIDE"),
        run("2 mauvais visage", FIELDS_OK, EMB_A, EMB_B, PERSON_OK, "ANOMALIE"),
        run("3 numero inconnu", FIELDS_OK, EMB_A, EMB_A, None, "ANOMALIE"),
        run(
            "4 photo floue (OCR vide)",
            {**FIELDS_OK, "raw_text": ""},
            EMB_A,
            EMB_A,
            PERSON_OK,
            "ANOMALIE",
        ),
        run(
            "5 champ illisible (nom)",
            {**FIELDS_OK, "nom": None},
            EMB_A,
            EMB_A,
            PERSON_OK,
            "VERIFICATION_COMPLEMENTAIRE",
        ),
        run("6 visage absent carte", FIELDS_OK, None, EMB_A, PERSON_OK, "ANOMALIE"),
        run(
            "7 visage absent porteur",
            FIELDS_OK,
            EMB_A,
            None,
            PERSON_OK,
            "VERIFICATION_COMPLEMENTAIRE",
        ),
        run(
            "8 date invalide",
            {**FIELDS_OK, "date_naissance": "1990-01-01"},
            EMB_A,
            EMB_A,
            PERSON_OK,
            "ANOMALIE",
        ),
    ]
    print(f"\n{sum(results)}/8 OK")
