"""Moteur de décision J12 : combine OCR + base + visage en un verdict unique."""

import re

import numpy as np

from config import SCORE_FACE_REJECT, SEUIL_SFACE
from face import compare

RE_DATE = re.compile(r"^\d{2}/\d{2}/\d{4}$")
_RANK = {"VALIDE": 0, "VERIFICATION_COMPLEMENTAIRE": 1, "ANOMALIE": 2}


def _worst(statuses):
    """Retourne le statut le plus grave de la liste."""
    return max(statuses, key=lambda s: _RANK[s])


def _out(status, reasons, scores):
    return {"status": status, "reasons": reasons, "scores": scores}


def decide(fields, card_emb, live_emb, person):
    """Combine plusieurs preuves. Cohérent ≠ authentique (pas de base officielle)."""
    scores = {
        "score_face": None,
        "numero_trouve": False,
        "ocr_ok": False,
        "champs_manquants": [],
        "date_valide": False,
    }

    # R1 — carte illisible : plus rien d'exploitable, on court-circuite.
    if not fields or not fields.get("raw_text"):
        return _out("ANOMALIE", ["carte illisible (OCR vide)"], scores)
    scores["ocr_ok"] = True

    verdicts, reasons = [], []

    # R2 — visage absent sur la carte.
    if card_emb is None:
        verdicts.append("ANOMALIE")
        reasons.append("aucun visage sur la carte")

    # R3 — visage absent sur le porteur : on peut redemander une capture.
    if live_emb is None:
        verdicts.append("VERIFICATION_COMPLEMENTAIRE")
        reasons.append("aucun visage sur le porteur (reprendre capture)")

    # R4 — numéro illisible.
    numero = fields.get("numero")
    if not numero:
        verdicts.append("ANOMALIE")
        reasons.append("numéro illisible")

    # R5 — date absente ou mauvais format.
    date_naiss = fields.get("date_naissance")
    if date_naiss and RE_DATE.match(date_naiss):
        scores["date_valide"] = True
    else:
        verdicts.append("ANOMALIE")
        reasons.append("date de naissance incohérente")

    # R6 — nom/prénom manquant = OCR raté probable → complément, pas anomalie.
    manquants = [k for k in ("nom", "prenom") if not fields.get(k)]
    if manquants:
        scores["champs_manquants"] = manquants
        verdicts.append("VERIFICATION_COMPLEMENTAIRE")
        reasons.append("champ manquant : " + ", ".join(manquants))

    # R7 — numéro absent de la base (choix étudiant J12 : ANOMALIE).
    if numero and person is None:
        verdicts.append("ANOMALIE")
        reasons.append("numéro absent de la base locale")
    elif person is not None:
        scores["numero_trouve"] = True

    # R8/R9 — comparaison faciale uniquement si les 2 empreintes existent.
    if card_emb is not None and live_emb is not None:
        s = compare(card_emb, live_emb)
        if s is not None:
            scores["score_face"] = round(float(s), 4)
            if s < SCORE_FACE_REJECT:
                verdicts.append("ANOMALIE")
                reasons.append("visages jugés différents")
            elif s < SEUIL_SFACE:
                verdicts.append("VERIFICATION_COMPLEMENTAIRE")
                reasons.append("similarité faciale intermédiaire")

    # Aucun problème détecté.
    if not verdicts:
        return _out("VALIDE", ["carte cohérente, porteur conforme"], scores)
    return _out(_worst(verdicts), reasons, scores)


if __name__ == "__main__":
    # Auto-test rapide (les vrais tests sont dans tests/test_decision.py).
    emb = np.ones(128, dtype=np.float32)
    print(
        decide(
            {
                "raw_text": "x",
                "numero": "FICT-001",
                "nom": "A",
                "prenom": "B",
                "date_naissance": "01/01/1990",
            },
            emb,
            emb,
            {"numero": "FICT-001"},
        )
    )
