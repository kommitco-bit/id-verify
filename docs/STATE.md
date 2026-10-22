# STATE.md — mis à jour le 24/10, jour 12, avec DeepSeek

> **Note** : J12 confirmé le 24/10 avec sortie collée (8/8 OK sur `test/test_decision.py`). Statut « ✅ confirmé » = écrit **et** exécuté avec succès rapporté par l'étudiant avec sortie collée. Prop. 2 et 4 rapportées OK verbalement le 24/10 (« je teste cela et search n'est pas bloquant ») mais **code non collé** → statut « rapporté OK, à re-confirmer par collage code + sortie ».

---

## Terminé et testé

- **Environnement** : venv Python **3.14.4** confirmé. Contournement Qt/Wayland (`QT_QPA_PLATFORM=xcb`) toujours en place.
- **Arborescence** : `~/Documents/DevOps/Projet/id-verif/` confirmée. **Note J12** : le dossier de tests réel est `test/` (singulier), pas `tests/` comme écrit §5 — on suit la réalité.
- **J2, J3, J4** : ESP32-CAM (`/` et `/capture`) fonctionnel, `src/capture.py` (3 sources) fonctionnel.
- **J5** : `imaging.py` (flou, resize, seuil, Otsu, Canny) fonctionnel.
- **J6 (17/10)** : `prepare_card(img) -> np.ndarray | None` fonctionnel.
- **J7 (18/10) — OCR** : Tesseract **5.5.0** + pack `fra` ; `src/ocr.py` conforme §6 ; 20/20 champs sur 4 cartes fictives.
- **J8 (19/10) — Détection YuNet** : `src/face.py` V1 ; `test_face_detect.py` et `test_face_detect_10.py` confirmés (10/10 frames).
- **J9 (19/10) — Empreintes SFace** : `get_embedding` (128 float32), `compare` (cosinus clampé, garde-fous `None`). `test_sface_scores.py` sur 6 paires confirmé (`min MÊME = 0.3414`, `max DIFF = 0.0352`).
- **J10 (22/10) — Base SQLite** ✅ confirmé : `init_db`, `add_person`, `get_person_by_number`, `log_verification` ; `test/test_enroll_5.py` et `test/test_log_verification.py` exécutés.
- **J11 (23/10) — Recherche vectorielle** ✅ confirmé : `test/test_load_embeddings.py` (4 personnes lues) ; `src/vector_search.py` (`find_nearest`, force brute numpy) ; auto-test `__main__` → `id=1 (1.0000)`, `id=2 (0.0762)`, `id=3 (0.0307)`.
- **J12 (24/10) — Moteur de décision** ✅ confirmé :
  - **`src/decision.py`** : `decide(fields, card_emb, live_emb, person) -> dict {status, reasons, scores}` **conforme §6**. 10 règles (R1–R10), agrégation par le pire statut, court-circuit R1. Auto-test `__main__` exécuté → `{'status': 'VALIDE', ...}` collé.
  - **`test/test_decision.py`** : 8 scénarios (cas normal, mauvais visage, numéro inconnu, photo floue, champ illisible, visage absent carte, visage absent porteur, date invalide). **Sortie collée : 8/8 OK.**

## En cours ou bloqué

- **Vérification des prop. 2 et 4 (rapportées OK verbalement le 24/10, à re-confirmer par collage)** :
  - **Prop. 2** (`(int(v) for v in face[:4])` dans `_detect_faces`) : l'étudiant a dit « je teste cela et search n'est pas bloquant » mais **code et sortie non collés** → tests `test_face_detect.py`, `test_face_detect_10.py`, `test_sface_scores.py` **non re-passés avec sortie affichée**.
  - **Prop. 4** (migration `DB_PATH` et `VALID_STATUSES` vers `src/config.py`) : rapportée OK verbalement, `vector_search.py` non bloqué selon l'étudiant, mais **code de `config.py` / `database.py` non collé** → impossible de confirmer si `from database import DB_PATH` est un ré-export ou un vrai import depuis `config`.
- **`FICT-004` absent de la base** : `test_load_embeddings.py` (23/10) lit 4 personnes au lieu de 5. Non bloquant. Diagnostic suggéré : `sqlite3 data/db/id_verif.db "SELECT id, numero FROM persons ORDER BY id;"`.
- **Calibration `SEUIL_SFACE` fragile** : non-match observé à 0.0762 (J11), au-dessus du `max(DIFF) = 0.0352` calibré J9 (6 paires). Marge toujours confortable sous `0.30`, mais **`decision.py` en dépend désormais (R8/R9)** → à consolider avant de mettre en prod.
- **Bonus ChromaDB reporté (option C)** : rien installé, stack §4 intacte.
- **Jeu de données J9 insuffisant** : 4 photos / 6 paires.
- **Scores MÊME bas pour SFace** (0.34, 0.43 vs 0.5–0.8 typiques) — pas un bug, à surveiller en J13+.
- **Jeu J7 incomplet** : 4 cartes, 05..10 absentes.
- **`src/imaging.py`** : V1 du cadre-guide non câblée — prévue pour `ui.py`.
- **Imports `src/`** : toujours gérés par `sys.path.insert(0, "src")` dans les tests (chemin **relatif** → cwd = racine `id-verif/` obligatoire).
- **IP ESP32** : DHCP `10.135.250.228`, réservation à envisager.
- **`capture.py` en mode flux** : réouverture caméra à chaque appel, non vérifiée sur la durée.

## Décisions prises (et pourquoi)

- **18/10 (J7)** — `TESSERACT_PSM = 6`, `OCR_MIN_WIDTH = 1500`, prétraitement `gris → upscale INTER_CUBIC → Otsu`, regex ancrées, deux groupes dans `_RE_NUM`.
- **19/10 (J8)** — Seuils YuNet `0.6 / 0.3 / 5000` + `margin=0.2` (toujours dans `face.py`). `setInputSize` à chaque `detect`.
- **19/10 (J9)** — `get_embedding` garde le plus grand visage ; SFace brut non normalisé → L2 dans `compare` ; clamp `[-1,1]` ; `SEUIL_SFACE = 0.30`, `SEUIL_SFACE_REFERENCE = 0.363` documentaire.
- **22/10 (J10)** — Schéma `persons` avec `numero UNIQUE` ; `embedding BLOB` via `.tobytes()` / `np.frombuffer` ; `?` anti-injection ; `VALID_STATUSES` fermé ; `log_verification` accepte `person_id = None` ; `scores` en JSON TEXT.
- **23/10 (J11)** — Force brute numpy retenue ; tri + slice `[:k]` ; bonus ChromaDB différé.
- **24/10 (J12) — Choix de l'étudiant sur les cas ambigus** :
  - **Numéro inconnu → `ANOMALIE`** (choix **plus strict** que ma proposition par défaut de `VERIFICATION_COMPLEMENTAIRE`). Raison opérateur : une carte dont le numéro n'est pas en base locale est un signal fort au guichet.
  - **Nom/prénom manquant → `VERIFICATION_COMPLEMENTAIRE`**. Raison : un champ OCR raté n'est pas un document faux, on demande une reprise manuelle.
- **24/10 (J12) — Agrégation par le pire statut** (`_RANK` + `max(..., key=...)`) : `ANOMALIE` > `VERIFICATION_COMPLEMENTAIRE` > `VALIDE`. On collecte **toutes** les raisons, pas seulement la première.
- **24/10 (J12) — Court-circuit R1** : `fields is None` ou `raw_text` vide → retour immédiat `ANOMALIE`, aucun autre calcul.
- **24/10 (J12) — Comparaison faciale conditionnelle** : `compare(card_emb, live_emb)` seulement si **les deux** empreintes existent ; sinon `scores["score_face"] = None` et R2/R3 tranchent avant.
- **24/10 (J12) — Nouveau seuil `SCORE_FACE_REJECT = 0.20`** dans `config.py` (borne basse sous `SEUIL_SFACE = 0.30`). Dette documentée dans `decision.py` (commentaire) : calibration J9 fragile (6 paires), à consolider.

## Signatures réelles des fonctions écrites (si elles diffèrent du contrat)

- **`src/config.py`** :
  - `TESSERACT_LANG = "fra"`, `TESSERACT_PSM = 6`, `OCR_MIN_WIDTH = 1500`.
  - `SEUIL_SFACE = 0.30`, `SEUIL_SFACE_REFERENCE = 0.363`.
  - **`SCORE_FACE_REJECT = 0.20` ajouté le 24/10 (J12)** ✅ — borne basse de décision.
  - `DB_PATH` et `VALID_STATUSES` déplacés ici le 23/10 (prop. 4 rapportée OK, code non collé).
  - **Toujours absents** : `SCORE_THRESHOLD`, `NMS_THRESHOLD`, `TOP_K`, `margin` (YuNet), `CHROMA_DIR`, `SCORE_FACE_ACCEPT` (on utilise `SEUIL_SFACE` directement dans `decision.py`).
- **`src/imaging.py`** : `prepare_card(img) -> np.ndarray | None` (conforme §6).
- **`src/capture.py`** : `get_frame(source: str) -> np.ndarray | None` (conforme §6).
- **`src/ocr.py`** : `_preprocess`, `extract_raw_text`, `extract_fields` + regex.
- **`src/face.py`** : `_get_detector`, `_detect_faces`, `_crop_face`, `_get_recognizer`, `get_embedding`, `compare`. Constantes module `YUNET_MODEL`, `SFACE_MODEL`, `SCORE_THRESHOLD`, `NMS_THRESHOLD`, `TOP_K`. `_detect_faces` modifié 23/10 (prop. 2 rapportée OK, code non collé).
- **`src/database.py`** — 4/4 fonctions §6 ✅ : `init_db`, `add_person`, `get_person_by_number`, `log_verification`. `DB_PATH` et `VALID_STATUSES` migrés vers `config.py` (prop. 4 rapportée OK, à re-confirmer).
- **`src/vector_search.py`** (J11) ✅ : `find_nearest(embedding: np.ndarray, k: int = 3) -> list[tuple[int, float]]` **conforme §6**.
- **`src/decision.py`** (nouveau J12) ✅ :
  - `decide(fields, card_emb, live_emb, person) -> dict` **conforme §6**.
  - Helpers module : `_worst(statuses)`, `_out(status, reasons, scores)`.
  - Constantes module : `RE_DATE = re.compile(r"^\d{2}/\d{2}/\d{4}$")`, `_RANK = {"VALIDE": 0, "VERIFICATION_COMPLEMENTAIRE": 1, "ANOMALIE": 2}`.
  - Importe `SEUIL_SFACE`, `SCORE_FACE_REJECT` depuis `config`, et `compare` depuis `face`.
- **Tests** :
  - `test/test_decision.py` (nouveau J12) ✅ — 8 scénarios, sortie collée 8/8 OK.
  - `test/test_load_embeddings.py` (J11) ✅ exécuté avant prop. 2/4.
  - `test/test_enroll_5.py`, `test/test_log_verification.py` (J10) ✅ exécutés avant prop. 4 — **à re-passer**.
  - `test/test_face_detect.py`, `test/test_face_detect_10.py`, `test/test_sface_scores.py` — **à re-passer** post-prop. 2.
  - `test/test_ocr_raw.py`, `test/demo_quad.py`, `test/demo_perspective.py`, `test/test_prepare_card.py` : inchangés.

## Valeurs importantes (seuils, IP de l'ESP32, chemins)

- Racine projet : `~/Documents/DevOps/Projet/id-verif/`
- Python : 3.14.4 (dans `env/`)
- ESP32-CAM : IP `10.135.250.228` (DHCP)
- Taille cible carte : 1000 × 630 px
- Seuils `prepare_card` (J6) : tolérance ratio 10 %, taille min 600×375, epsilon 0.01–0.08, rectangularité ≥ 0.55, aire quad ≥ 5 %, côté min 150 px.
- Seuils OCR (J7) : `fra`, PSM 6, `OCR_MIN_WIDTH = 1500`.
- Seuils YuNet (J8, toujours dans `face.py`) : `SCORE_THRESHOLD = 0.6`, `NMS_THRESHOLD = 0.3`, `TOP_K = 5000`, `margin = 0.2`.
- Seuils SFace (J9, `config.py`) : `SEUIL_SFACE = 0.30`, `SEUIL_SFACE_REFERENCE = 0.363`.
- **Seuils décision (J12, `config.py`)** : `SCORE_FACE_REJECT = 0.20` (borne basse), `SEUIL_SFACE = 0.30` (borne haute acceptée).
- **Zones de décision (J12)** : `score_face < 0.20` → ANOMALIE ; `0.20 ≤ score_face < 0.30` → VÉRIF_COMPL ; `score_face ≥ 0.30` → OK côté visage.
- **Calibration J9** : `min(MÊME) = 0.3414` / `0.4319` ; `max(DIFF) = 0.0352`.
- **Observation J11** : self `1.0000`, non-match `0.0762` (id=2), `0.0307` (id=3). Marge toujours sous `0.20`.
- Modèles : `models/face_detection_yunet_2023mar.onnx`, `models/face_recognition_sface_2021dec.onnx`.
- Variable Qt : `QT_QPA_PLATFORM=xcb`.
- Tesseract : **5.5.0**, packs `fra` + `eng` + `osd`.
- Base SQLite : `data/db/id_verif.db`.
- **Schéma `persons`** : `id INTEGER PK AUTOINCREMENT`, `nom`, `postnom`, `prenom`, `date_naissance` TEXT, `numero TEXT NOT NULL UNIQUE`, `embedding BLOB`.
- **Schéma `verifications`** : `id PK AUTOINCREMENT`, `person_id INTEGER`, `status TEXT`, `scores TEXT`, `created_at DEFAULT CURRENT_TIMESTAMP`.
- **`VALID_STATUSES`** : `{"VALIDE", "ANOMALIE", "VERIFICATION_COMPLEMENTAIRE"}` — localisation à confirmer (avant `database.py`, après prop. 4 `config.py`).
- **Personnes actuellement en base (23/10)** : 4 lignes — `id=1 FICT-001`, `id=2 FICT-002`, `id=3 FICT-003`, `id=4 SYNTH-005`. **`FICT-004` absent.**
- **Format `scores` renvoyé par `decide` (J12)** : `{score_face: float|None, numero_trouve: bool, ocr_ok: bool, champs_manquants: list[str], date_valide: bool}`.

## Notions apprises (pour me réinterroger plus tard)

**J6 — Contours, polygones, perspective, ratio d'image.**

**J7 — OCR** : pixels → caractères ; Tesseract segmente lignes → mots → caractères ; `pytesseract` = télécommande, Tesseract = moteur ; PSM 6 = bloc uniforme ; `gris → upscale → Otsu` ; regex ancrées ; confusions `I/L/1`, `0/O`, `4/9`.

**J8 — YuNet** : détection ≠ reconnaissance ; bbox ; landmarks ; modèle ONNX = filtre préfabriqué ; `(N, 15)` par frame ; singleton paresseux ; `setInputSize` avant `detect`.

**J9 — SFace** : embedding = vecteur 128 float32 ; inférence seule ; `alignCrop` 112×112 ; cosinus = angle ; SFace brut non normalisé (norme ≈ 13) → L2 dans `compare` ; `compare(e,e) ≈ 0.99999988` ; FAR grave / FRR pénible ; marge `(max(DIFF), min(MÊME))`.

**J10 — SQLite** : table ↔ classeur ; `PRIMARY KEY` ; `UNIQUE NOT NULL` ; `IF NOT EXISTS` idempotent ; BLOB ↔ `np.frombuffer` sans copie ; `?` anti-injection ; `cur.lastrowid` ; `row_factory` ; `json.dumps/loads` non symétrique avec `np.float32` → `default=float` ; `with sqlite3.connect(...)` gère la transaction, pas la fermeture ; `sqlite_sequence` = interne `AUTOINCREMENT` ; FK écrite mais non active ; enrôlement = `OCR → get_embedding → INSERT` ; fail-fast sur bug code, `None` sur donnée absente.

**J11 — Recherche vectorielle** : vecteur = flèche à N dimensions ; 1:N = « qui me ressemble parmi N », 1:1 = « est-ce X » ; force brute = O(N) par requête ; tri décroissant + `[:k]` = k plus proches voisins ; ChromaDB renvoie `distance = 1 − similarité` ; index vectoriel (HNSW/IVF) = accélère à grande échelle au prix d'approximation ; garde-fous à trois niveaux (None → `[]`, bug → `raise`, ligne corrompue → `continue`).

**J12 — Moteur de décision** : « cohérent avec la base locale » ≠ « authentique » (limite assumée du brief) ; **agrégation par le pire statut** (`ANOMALIE` > `VÉRIF_COMPL` > `VALIDE`) — un médecin croise plusieurs symptômes, un seul suffit à alerter ; **collecte de toutes les raisons** (pas seulement la première) pour l'opérateur ; **court-circuit** quand l'entrée est inexploitable (R1) ; **comparaison conditionnelle** — on ne `compare` que si les deux empreintes existent, sinon score `None` ; **empreintes factices pour tester la logique** — `[1,1,...,1]` vs `[1,0,...,0]` donnent cosinus ≈ 0.09, indépendant de SFace (isole la règle) ; **`{**dict, "k": v}`** = copie + override, un scénario = un champ modifié ; **pyramide de règles\*\* : R1 (court-circuit) → R2-R7 (structurantes) → R8/R9 (nuancées) → R10 (défaut VALIDE).

## Prochaine étape

- **J1 à J12 clos** (J12 confirmé le 24/10 avec sortie collée 8/8 OK).
- **Avant J13 — vérifications à faire (ordre suggéré)** :
  1. **Coller le contenu actuel de `src/config.py` et `src/database.py`** (vérifier localisation `DB_PATH`, `VALID_STATUSES`, `SCORE_FACE_REJECT`, et présence d'un ré-export).
  2. **Coller le diff (ou contenu) de `_detect_faces` dans `src/face.py`** (prop. 2).
  3. **Re-passer les tests impactés** avec sortie collée :
     - `test_face_detect.py`, `test_face_detect_10.py`, `test_sface_scores.py` (post-prop. 2).
     - `test_enroll_5.py`, `test_log_verification.py`, `test_load_embeddings.py`, `python src/vector_search.py` (post-prop. 4).
- **Début de J13 — à faire avant tout code** : fournir la **section J13** de la feuille de route (§7). Attendu probable : `src/pipeline.py` — `verify(card_source, face_source) -> dict` qui orchestre `capture → prepare_card → extract_fields → get_embedding → get_person_by_number → decide → log_verification`. **À confirmer par la feuille.**
- **Points à consolider (aucun urgent)** : diagnostic `FICT-004` ; recalibration `SEUIL_SFACE` ; cartes 05..10 ; DHCP ESP32 ; package Python `src/` ; harmonisation `demo_step.py`/`demo_steps.py`.
- **Propositions restant en attente (aucune appliquée)** :
  - **PROP. 1** — déplacer seuils YuNet vers `config.py`. **Non faite.**
  - **PROP. 3** — convertir `src/` en package Python (`__init__.py` + imports relatifs). **Non faite.**
  - **PROP. 5** — ajouter `CHROMA_DIR` à `config.py` quand bonus C réalisé. **Non faite.**
- **Bonus C — différé** : ChromaDB non installé.
