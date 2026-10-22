# test/test_enroll_from_card.py
"""Enrole la personne de la carte fictive dans la base locale.
Idempotent : si le numero existe deja, ne fait rien.
"""

import sys

sys.path.insert(0, "src")  # import depuis src/, comme les autres tests

import capture
import database
import face
import imaging
import ocr

CARD = "data/samples/carte_fictive_01.jpg"

# 1) Capture + preparation de la carte
img = capture.get_frame(f"file:{CARD}")
if img is None:
    print("ERREUR: carte introuvable:", CARD)
    sys.exit(1)

card = imaging.prepare_card(img)
if card is None:
    print("ERREUR: prepare_card a echoue")
    sys.exit(1)

# 2) OCR -> champs
fields = ocr.extract_fields(card)
print("Champs OCR :", fields)

if fields is None or not fields.get("numero"):
    print("ERREUR: numero introuvable, impossible d'enroller")
    sys.exit(1)

numero = fields["numero"]

# 3) Idempotence : deja en base ?
existing = database.get_person_by_number(numero)
if existing:
    print(f"Deja en base : id={existing['id']}, numero={numero}")
    sys.exit(0)

# 4) Empreinte faciale de la photo de la carte
emb = face.get_embedding(card)
if emb is None:
    print("ERREUR: aucun visage detectable sur la carte")
    sys.exit(1)

# 5) Avertissement si un champ est manquant (sera NULL en base)
missing = [
    k for k in ("nom", "postnom", "prenom", "date_naissance") if not fields.get(k)
]
if missing:
    print("ATTENTION: champs manquants (NULL en base):", missing)

# 6) INSERT
database.init_db()
pid = database.add_person(fields, emb)
print(f"Enrolle OK : id={pid}, numero={numero}, emb.shape={emb.shape}")
