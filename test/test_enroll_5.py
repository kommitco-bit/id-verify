"""Test J10 : enrôler 5 personnes (4 cartes + 1 synthétique) et vérifier la ronde-trip BLOB."""

import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import database
import face
import ocr
from capture import get_frame

SAMPLES = PROJECT_ROOT / "data" / "samples"
CARDS = sorted(SAMPLES.glob("carte_fictive_0*.jpg"))


def enroll_card(numero: str, card_path: Path) -> tuple[int, np.ndarray] | None:
    """Enrôle une carte. Renvoie (id, embedding_original) ou None si KO."""
    img = get_frame(f"file:{card_path}")
    if img is None:
        print(f"  [KO] image illisible : {card_path.name}")
        return None
    fields = ocr.extract_fields(img)
    emb = face.get_embedding(img)
    if emb is None:
        print(f"  [KO] aucun visage : {card_path.name}")
        return None
    fields["numero"] = numero  # on force un numéro unique et fictif
    pid = database.add_person(fields, emb)
    if pid is None:
        print(f"  [KO] échec de l'enregistrement en base : {card_path.name}")
        return None

    print(f"  [OK] id={pid} numero={numero} nom={fields.get('nom')}")
    return int(pid), emb


def main() -> None:
    database.init_db()
    enrolled: list[tuple[str, np.ndarray]] = []

    print("=== Enrôlement 4 cartes fictives ===")
    for i, card in enumerate(CARDS, start=1):
        numero = f"FICT-{i:03d}"
        result = enroll_card(numero, card)
        if result is not None:
            enrolled.append((numero, result[1]))

    print("=== Enrôlement 5e personne synthétique ===")
    rng = np.random.default_rng(seed=42)
    synth = rng.standard_normal(128).astype(np.float32)
    fields_synth = {
        "nom": "SYNTH",
        "postnom": "TEST",
        "prenom": "Cinq",
        "date_naissance": "2000-01-01",
        "numero": "SYNTH-005",
    }
    pid = database.add_person(fields_synth, synth)
    print(f"  [OK] id={pid} numero=SYNTH-005")
    enrolled.append(("SYNTH-005", synth))

    print("=== Vérification ronde-trip BLOB ===")
    for numero, emb_orig in enrolled:
        person = database.get_person_by_number(numero)
        if person is None:
            print(f"  [KO] {numero} introuvable en base")
            continue
        score = face.compare(person["embedding"], emb_orig)
        score_str = "None" if score is None else f"{score:.6f}"
        ok = score is not None and abs(score - 1.0) < 1e-4
        print(f"  [{'OK' if ok else 'KO'}] {numero} score={score_str}")


if __name__ == "__main__":
    main()
