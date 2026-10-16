# PROJECT_BRIEF — Vérification d'identité (prototype 15 jours)

Dernière mise à jour : 2026-10-16

## 1. Objectif
Prototype de vérification d'identité en 3 contrôles :
1. La carte est lisible et cohérente (OCR + contrôles simples).
2. Ses données existent dans une base de référence locale (SQLite).
3. Le visage du porteur correspond à la photo de la carte (comparaison 1:1).

Résultat affiché : VALIDE, ANOMALIE ou VERIFICATION_COMPLEMENTAIRE.

## 2. Limite assumée
Sans accès à la base de l'organisme émetteur, on vérifie la cohérence
avec une base locale, pas l'authenticité absolue du document.

## 3. Matériel
- ESP32-CAM (AI-Thinker) : capture et envoi d'images via Wi-Fi (HTTP /capture).
- PC Ubuntu (8 Go RAM, CPU AMD 3020e, sans GPU) : tout le traitement lourd en Python.

## 4. Stack figée
| Besoin              | Choix                                                              |
|---------------------|--------------------------------------------------------------------|
| Langage             | Python 3.10+ dans un venv                                          |
| Images              | opencv-python >= 4.8 + numpy                                       |
| OCR                 | Tesseract via pytesseract, langue fra                              |
| Détection visage    | YuNet (ONNX face_detection_yunet_2023mar.onnx)                     |
| Empreinte faciale   | SFace (ONNX face_recognition_sface_2021dec.onnx), cosinus, seuil 0.363 |
| Base de données     | SQLite (module sqlite3)                                            |
| Recherche vect.     | numpy (force brute). ChromaDB en option seulement                  |
| Interface           | customtkinter                                                     |
| Capture             | ESP32-CAM via HTTP /capture. Plan B : webcam ou photo téléphone    |
| Réseau              | requests                                                           |

Interdit sans accord : TensorFlow, PyTorch, dlib, Docker, frameworks web,
services cloud, tout ce qui exige un GPU.

## 5. Arborescence (fixe)
id-verif/
  main.py
  docs/          (PROJECT_BRIEF.md, STATE.md)
  models/        (fichiers .onnx)
  data/
    samples/     (photos de test fictives)
    db/          (fichier SQLite)
  firmware/esp32cam/   (code Arduino)
  src/
    config.py    (seuils, chemins, IP de l'ESP32)
    capture.py
    imaging.py
    ocr.py
    face.py
    database.py
    vector_search.py
    decision.py
    pipeline.py
    ui.py
  tests/

## 6. Contrat d'interfaces (figé)
| Module           | Fonction                              | Entrée → Sortie |
|------------------|---------------------------------------|-----------------|
| capture.py       | get_frame(source: str)                | 'webcam:0' / 'http://IP/capture' / 'file:chemin.jpg' → BGR np.ndarray ou None |
| imaging.py       | prepare_card(img)                     | image brute → carte redressée 1000×630 ou None |
| ocr.py           | extract_fields(card_img)              | → dict {nom, postnom, prenom, date_naissance, numero, raw_text} (None si non lu) |
| face.py          | get_embedding(img)                    | image avec visage → np.ndarray float32 (128) ou None |
| face.py          | compare(emb_a, emb_b)                 | → float (similarité cosinus) |
| database.py      | init_db()                             | crée persons + verifications |
| database.py      | add_person(fields, embedding)         | → id (int) |
| database.py      | get_person_by_number(numero)          | → dict ou None |
| database.py      | log_verification(person_id, status, scores) | → None |
| vector_search.py | find_nearest(embedding, k=3)          | → [(person_id, score), ...] du meilleur au pire |
| decision.py      | decide(fields, card_emb, live_emb, person) | → {status, reasons, scores} |
| pipeline.py      | verify(card_source, face_source)      | → dict de decision.decide |

Conventions :
- Images = np.ndarray BGR (OpenCV).
- Empreintes = np.ndarray float32.
- En cas d'échec : renvoyer None (ne pas planter).
- Seuils et chemins : uniquement dans config.py.
- status ∈ {VALIDE, ANOMALIE, VERIFICATION_COMPLEMENTAIRE}.

## 7. Vocabulaire
- Carte : le document. Titulaire : personne sur la photo. Porteur : personne devant la caméra.
- Frame : une image capturée.
- Empreinte faciale (embedding) : liste de nombres qui résume un visage.
- Score : mesure de ressemblance. Seuil : valeur d'acceptation.
- Base de référence : SQLite des personnes enrôlées. Enrôlement : ajouter une personne.
- Vérification 1:1 : comparer à UNE photo. 1:N : chercher parmi N personnes.

## 8. Règles de collaboration
- Un seul fichier par réponse, 80 lignes max.
- Explication avant code, explication bloc par bloc après.
- Ne jamais changer stack / arborescence / contrat sans accord explicite.
- Travail uniquement avec cartes fictives et personnes consentantes.
- STATE.md fait foi entre les sessions.
