# src/pipeline.py
"""Pipeline de vérification d'identité.

Orchestration : capture -> imaging -> ocr -> face -> database -> decision -> log.
Conforme au contrat §6 : verify(card_source, face_source) -> dict de decision.decide.
"""

import capture
import database
import decision
import face
import imaging
import ocr


def _safe_card(card_source):
    """Capture + prépare la carte. Renvoie (fields, card_emb) ou (None, None)."""
    img = capture.get_frame(card_source)
    if img is None:
        return None, None
    prepared = imaging.prepare_card(img)
    if prepared is None:
        return None, None
    fields = ocr.extract_fields(prepared)  # dict avec clés ou None
    emb = face.get_embedding(prepared)  # np.float32(128) ou None
    return fields, emb


def _safe_live(face_source):
    """Capture le porteur. Renvoie son empreinte ou None."""
    img = capture.get_frame(face_source)
    if img is None:
        return None
    return face.get_embedding(img)


def verify(card_source, face_source):
    """Enchaîne tous les modules et renvoie le dict de decision.decide."""
    fields, card_emb = _safe_card(card_source)
    live_emb = _safe_live(face_source)

    # Recherche 1:1 : on ne la tente que si un numéro a été lu.
    person = None
    if fields is not None:
        numero = fields.get("numero")
        if numero:
            person = database.get_person_by_number(numero)

    # decision.decide sait gérer fields/embeddings/person à None (règles R1-R10).
    result = decision.decide(fields, card_emb, live_emb, person)

    # Journalisation : person_id peut être None (porteur inconnu de la base).
    person_id = person["id"] if person else None
    database.log_verification(person_id, result["status"], result["scores"])
    return result


if __name__ == "__main__":
    # Ajuste ces deux chemins vers des images réelles de data/samples/.
    res = verify(
        "file:data/samples/carte_fictive_01.jpg", "file:data/samples/porteur_02.png"
    )
    print(res)
