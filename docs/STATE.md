# STATE.md — mis à jour le 23/10, jour 11, avec DeepSeek

> **Note** : J10 confirmé le 22/10. J11 (recherche vectorielle) réalisé le 23/10. Statuts « ✅ confirmé » = écrit **et** exécuté avec succès rapporté par l'étudiant, avec sortie collée. Les propositions 2 et 4 sont marquées « fait » par l'étudiant le 23/10 mais **sans code ni sortie de test collés** → statut « rapporté fait, à re-confirmer ».

---

## Terminé et testé

- **Environnement** : venv Python **3.14.4** confirmé. Contournement Qt/Wayland toujours en place (`QT_QPA_PLATFORM=xcb`).
- **Arborescence** : `~/Documents/DevOps/Projet/id-verif/` confirmée.
- **J2, J3, J4** : ESP32-CAM (`/` et `/capture`) fonctionnel, `src/capture.py` (3 sources) fonctionnel.
- **J5** : `imaging.py` (flou, resize, seuil, Otsu, Canny) fonctionnel.
- **J6 (17/10)** : `prepare_card(img) -> np.ndarray | None` fonctionnel (détection V2 + perspective + resize direct).
- **J7 (18/10) — OCR** : Tesseract **5.5.0** + pack `fra` ; `src/ocr.py` conforme §6 ; **20/20 champs lus sur 4 cartes fictives**.
- **J8 (19/10) — Détection YuNet** : `src/face.py` V1 (détection) ; `test_face_detect.py` et `test_face_detect_10.py` confirmés (10/10 frames). WARN OpenCV bénin, CPU only.
- **J9 (19/10) — Empreintes SFace** : `get_embedding` (128 float32), `compare` (cosinus clampé, garde-fous `None`). `test_sface_scores.py` sur 6 paires confirmé (`min MÊME = 0.3414`, `max DIFF = 0.0352`).
- **J10 (22/10) — Base SQLite** ✅ confirmé : `init_db`, `add_person`, `get_person_by_number`, `log_verification` ; `test/test_enroll_5.py` et `test/test_log_verification.py` exécutés.
- **J11 (23/10) — Recherche vectorielle** ✅ confirmé :
  - **`test/test_load_embeddings.py`** : lit les embeddings en base, affiche `id`, `numero`, `nom`, `shape`, `dtype`, `norme`. **4 personnes lues** (voir « En cours » pour `FICT-004`).
  - **`src/vector_search.py`** : `find_nearest(embedding, k=3) -> list[(person_id, score)]` en force brute numpy. Auto-test `__main__` exécuté : requête `FICT-001` → `id=1 (1.0000)`, `id=2 (0.0762)`, `id=3 (0.0307)`. **La bonne personne est 1ʳᵉ.**

## En cours ou bloqué

- **Vérification post-modifications du 23/10** (propositions 2 et 4 « fait » par l'étudiant, code non collé) :
  - **Prop. 2** (`(int(v) for v in face[:4])` dans `_detect_faces`) : risque faible, mais `test_face_detect.py`, `test_face_detect_10.py` et `test_sface_scores.py` **non re-passés** → à re-exécuter pour confirmer.
  - **Prop. 4** (migration `DB_PATH` et `VALID_STATUSES` vers `src/config.py`) : **impacte `src/vector_search.py`** (J11) qui fait `from database import DB_PATH`. Soit un ré-export subsiste dans `database.py` (OK), soit `vector_search.py` doit être adapté. **À vérifier avant J12.** Tests de J10 et J11 (`test_enroll_5.py`, `test_log_verification.py`, `test_load_embeddings.py`, `__main__` de `vector_search.py`) **non re-passés** → à re-exécuter.
- **`FICT-004` absent de la base** : `test_load_embeddings.py` (23/10) lit **4 personnes** au lieu de 5. Cause non diagnostiquée. **Non bloquant**. Diagnostic suggéré : `sqlite3 data/db/id_verif.db "SELECT id, numero FROM persons ORDER BY id;"`.
- **Calibration `SEUIL_SFACE` fragile** : score `0.0762` observé sur un non-match (id=2), au-dessus du `max(DIFF) = 0.0352` calibré J9 (6 paires). Marge toujours confortable sous `0.30` (0.22), mais à consolider avant `decision.py`.
- **Bonus ChromaDB reporté (option C)** : rien installé, stack §4 intacte. Reprise quand une vraie question de scaling se posera.
- **Jeu de données J9 insuffisant** : 4 photos / 6 paires.
- **Scores MÊME bas pour SFace** (0.34, 0.43 vs 0.5–0.8 typiques) — pas un bug, à surveiller en J12+.
- **Jeu J7 incomplet** : 4 cartes, 05..10 absentes.
- **`src/imaging.py`** : V1 du cadre-guide non câblée — prévue pour `ui.py`.
- **Imports `src/`** : toujours gérés par `sys.path.insert` dans les tests.
- **IP ESP32** : DHCP `10.135.250.228`, réservation à envisager.
- **`capture.py` en mode flux** : réouverture caméra à chaque appel, non vérifiée sur la durée.

## Décisions prises (et pourquoi)

- **18/10 (J7)** — `TESSERACT_PSM = 6`, `OCR_MIN_WIDTH = 1500`, prétraitement `gris → upscale INTER_CUBIC → Otsu`, regex ancrées sur étiquettes, deux groupes dans `_RE_NUM`.
- **19/10 (J8)** — Seuils YuNet `0.6 / 0.3 / 5000` + `margin=0.2`. `setInputSize` à chaque `detect`.
- **19/10 (J9)** — `get_embedding` garde le plus grand visage ; SFace brut non normalisé (norme ≈ 13) → L2 dans `compare` ; clamp `[-1,1]` ; `SEUIL_SFACE = 0.30`, `SEUIL_SFACE_REFERENCE = 0.363` documentaire.
- **22/10 (J10)** — Schéma `persons` avec `numero UNIQUE` ; `embedding BLOB` via `.tobytes()` / `np.frombuffer` ; `add_person` lève sur mauvais dtype ; paramètre lié `?` ; `VALID_STATUSES` fermé ; `log_verification` accepte `person_id = None` ; `scores` en JSON TEXT.
- **23/10 (J11)** — Force brute numpy retenue (simple, transparente, réutilise `face.compare` et `DB_PATH`) ; garde-fous symétriques J10 ; tri + slice `[:k]` (pas de `heapq`) ; bonus ChromaDB différé (option C).
- **23/10 (post-J11) — Proposition 2 « rapportée faite »** : `(int(v) for v in face[:4])` dans `_detect_faces`. Raison J8 : logs propres (évite `numpy.int64` dans les `print`). Code non collé, tests **non re-passés** → à re-confirmer.
- **23/10 (post-J11) — Proposition 4 « rapportée faite »** : migration `DB_PATH` + `VALID_STATUSES` vers `src/config.py` pour respecter §6 (« tous les chemins et seuils vivent dans `config.py` »). Code non collé, tests **non re-passés**, `vector_search.py` **potentiellement impacté** → à re-confirmer avant J12.

## Signatures réelles des fonctions écrites (si elles diffèrent du contrat)

- **`src/config.py`** :
  - `TESSERACT_LANG = "fra"`, `TESSERACT_PSM = 6`, `OCR_MIN_WIDTH = 1500`.
  - `SEUIL_SFACE = 0.30`, `SEUIL_SFACE_REFERENCE = 0.363`.
  - **`DB_PATH` et `VALID_STATUSES` déplacés ici le 23/10** (prop. 4 rapportée faite, **à confirmer**) — donc `database.py` doit les importer depuis `config`, et `vector_search.py` doit soit continuer à faire `from database import DB_PATH` (si ré-export), soit passer à `from config import DB_PATH`.
  - **Toujours absents** : `SCORE_THRESHOLD`, `NMS_THRESHOLD`, `TOP_K`, `margin` (YuNet), `CHROMA_DIR`.
- **`src/imaging.py`** : `prepare_card(img) -> np.ndarray | None` (conforme §6).
- **`src/capture.py`** : `get_frame(source: str) -> np.ndarray | None` (conforme §6).
- **`src/ocr.py`** : `_preprocess`, `extract_raw_text`, `extract_fields` + regex.
- **`src/face.py`** :
  - `_get_detector()`, `_detect_faces(img)`, `_crop_face(img, bbox, margin=0.2)`, `_get_recognizer()`.
  - **`_detect_faces` modifié le 23/10** : `(int(v) for v in face[:4])` au lieu de `face[:4].astype(int)` (prop. 2 rapportée faite, **à confirmer**).
  - `get_embedding(img) -> np.ndarray float32 (128,) | None` ✅ ; `compare(emb_a, emb_b) -> float | None` ✅.
  - Constantes module : `YUNET_MODEL`, `SFACE_MODEL`, `SCORE_THRESHOLD`, `NMS_THRESHOLD`, `TOP_K`.
- **`src/database.py`** — 4/4 fonctions §6 ✅ :
  - `init_db()`, `add_person(fields, embedding)`, `get_person_by_number(numero)`, `log_verification(person_id, status, scores)`.
  - **Modifié le 23/10** : `DB_PATH` et `VALID_STATUSES` déplacés vers `config.py` (prop. 4 rapportée faite, **à confirmer**). Si non ré-exportés, tout code faisant `from database import DB_PATH` casse — **`vector_search.py` est le premier concerné**.
- **`src/vector_search.py`** (nouveau J11) ✅ :
  - `find_nearest(embedding: np.ndarray, k: int = 3) -> list[tuple[int, float]]` **conforme §6**.
  - **Point de vigilance post-prop. 4** : `from database import DB_PATH` à valider — si `DB_PATH` a migré vers `config.py` sans ré-export dans `database.py`, **cette ligne casse silencieusement au prochain run** (ModuleNotFoundError / ImportError).
- **Tests** :
  - `test/test_load_embeddings.py` (nouveau J11) ✅ exécuté **avant** les modifications de prop. 2 et 4.
  - `test/test_enroll_5.py`, `test/test_log_verification.py` (J10) ✅ exécutés **avant** prop. 4 — **à re-passer**.
  - `test/test_face_detect.py`, `test/test_face_detect_10.py`, `test/test_sface_scores.py` — **à re-passer** post-prop. 2.
  - `test/test_ocr_raw.py`, `test/demo_quad.py`, `test/demo_perspective.py`, `test/test_prepare_card.py` : inchangés.

## Valeurs importantes (seuils, IP de l'ESP32, chemins)

- Racine projet : `~/Documents/DevOps/Projet/id-verif/`
- Python : 3.14.4 (dans `env/`)
- ESP32-CAM : IP `10.135.250.228` (DHCP)
- Taille cible carte : 1000 × 630 px
- Seuils `prepare_card` (J6) : tolérance ratio 10 %, taille min 600×375, epsilon 0.01–0.08, rectangularité ≥ 0.55, aire quad ≥ 5 %, côté min 150 px.
- Seuils OCR (J7) : `fra`, PSM 6, `OCR_MIN_WIDTH = 1500`.
- Seuils YuNet (J8, **toujours dans `face.py`** — prop. 1 non faite) : `SCORE_THRESHOLD = 0.6`, `NMS_THRESHOLD = 0.3`, `TOP_K = 5000`, `margin = 0.2`.
- Seuils SFace (J9, `config.py`) : `SEUIL_SFACE = 0.30`, `SEUIL_SFACE_REFERENCE = 0.363`.
- **Calibration J9 (19/10)** : `min(MÊME) = 0.3414` / `0.4319` ; `max(DIFF) = 0.0352`.
- **Observation J11 (23/10)** : self `1.0000`, non-match `0.0762` (id=2), `0.0307` (id=3). Calibration J9 à consolider.
- Modèles : `models/face_detection_yunet_2023mar.onnx`, `models/face_recognition_sface_2021dec.onnx`.
- Variable Qt : `QT_QPA_PLATFORM=xcb`.
- Tesseract : **5.5.0**, packs `fra` + `eng` + `osd`.
- Base SQLite : `data/db/id_verif.db`.
- **Schéma `persons`** : `id INTEGER PK AUTOINCREMENT`, `nom`, `postnom`, `prenom`, `date_naissance` TEXT, `numero TEXT NOT NULL UNIQUE`, `embedding BLOB`.
- **Schéma `verifications`** : `id PK AUTOINCREMENT`, `person_id INTEGER` (FK non activée), `status TEXT`, `scores TEXT`, `created_at DEFAULT CURRENT_TIMESTAMP`.
- **`VALID_STATUSES`** : `{"VALIDE", "ANOMALIE", "VERIFICATION_COMPLEMENTAIRE"}` — **localisation à confirmer** (avant : `database.py` ; après prop. 4 : `config.py`).
- **Personnes actuellement en base (23/10)** : **4 lignes** — `id=1 FICT-001`, `id=2 FICT-002`, `id=3 FICT-003`, `id=4 SYNTH-005`. **`FICT-004` absent.**
- **Normes observées (23/10)** : `13.03`, `9.62`, `10.54`, `9.01`.

## Notions apprises (pour me réinterroger plus tard)

**J6 — Contours, polygones, perspective, ratio d'image** (conservées).

**J7 — OCR** : pixels → caractères ; Tesseract segmente lignes → mots → caractères ; `pytesseract` = télécommande, Tesseract = moteur ; PSM 6 = bloc uniforme ; `gris → upscale → Otsu` ; regex ancrées ; confusions `I/L/1`, `0/O`, `4/9`.

**J8 — YuNet** : détection ≠ reconnaissance ; bbox ; landmarks ; modèle ONNX = filtre préfabriqué ; `(N, 15)` par frame ; singleton paresseux ; `setInputSize` avant `detect`.

**J9 — SFace** : embedding = vecteur 128 float32 ; inférence seule ; `alignCrop` 112×112 ; cosinus = angle ; SFace brut non normalisé (norme ≈ 13) → L2 dans `compare` ; `compare(e,e) ≈ 0.99999988` ; FAR grave / FRR pénible ; marge `(max(DIFF), min(MÊME))`.

**J10 — SQLite** : table ↔ classeur ; `PRIMARY KEY` ; `UNIQUE NOT NULL` ; `IF NOT EXISTS` idempotent ; BLOB ↔ `np.frombuffer` sans copie ; `?` anti-injection ; `cur.lastrowid` ; `row_factory` ; `json.dumps/loads` non symétrique avec `np.float32` → `default=float` ; `with sqlite3.connect(...)` gère la transaction, pas la fermeture ; `sqlite_sequence` = interne `AUTOINCREMENT` ; FK écrite mais non active ; enrôlement = `OCR → get_embedding → INSERT` ; fail-fast sur bug code, `None` sur donnée absente.

**J11 — Recherche vectorielle** : vecteur = flèche à N dimensions ; 1:N = « qui me ressemble parmi N », 1:1 = « est-ce X » ; force brute = O(N) par requête ; tri décroissant + `[:k]` = k plus proches voisins ; ChromaDB renvoie `distance = 1 − similarité` (reconvertir pour rester aligné sur `face.compare`) ; index vectoriel (HNSW/IVF) = accélère à grande échelle au prix d'approximation + mémoire ; pièges ChromaDB (`ids` en `str`, `embedding_function=None`, `n_results ≤ count()`, `hnsw:space = "cosine"`) ; garde-fous à trois niveaux (None → `[]`, bug → `raise`, ligne corrompue → `continue`).

**Nouveau (23/10, post-J11) — Impact d'une migration de constantes** : déplacer `DB_PATH` de `database.py` vers `config.py` **casse tout import `from database import DB_PATH`** sauf si `database.py` fait un **ré-export** (`from config import DB_PATH`). C'est un exemple classique de **couplage implicite par import** : un module peut devenir « boîte aux lettres » d'une constante qui vit ailleurs. Leçon : après ce type de migration, **re-passer tous les tests qui touchent l'import concerné**, même si le code « a l'air » inchangé.

## Prochaine étape

- **J1 à J11 clos** (J11 confirmé fonctionnel le 23/10).
- **Avant J12 — 3 vérifications à faire (ordre suggéré) :**
  1. **Coller le contenu actuel de `src/config.py` et `src/database.py`** (pour que je vérifie où vivent `DB_PATH` et `VALID_STATUSES` et si un ré-export existe). Sans ça, je ne peux pas garantir que `vector_search.py` fonctionne encore.
  2. **Coller le diff (ou le contenu) de `_detect_faces` dans `src/face.py`** (prop. 2).
  3. **Re-passer les tests impactés** :
     - `test_face_detect.py`, `test_face_detect_10.py`, `test_sface_scores.py` (post-prop. 2).
     - `test_enroll_5.py`, `test_log_verification.py`, `test_load_embeddings.py`, `python src/vector_search.py` (post-prop. 4).
- **Début de J12 — à faire avant tout code** : fournir la **section J12** de la feuille de route (§7). Attendu probable : `src/decision.py` (`decide(fields, card_emb, live_emb, person)`). **À confirmer par la feuille.**
- **Points à consolider (aucun urgent)** : diagnostic `FICT-004` ; recalibration `SEUIL_SFACE` ; surveillance live vs carte ; cartes 05..10 ; DHCP ESP32 ; package Python `src/` ; harmonisation `demo_step.py`/`demo_steps.py`.
- **Propositions restant en attente (aucune appliquée)** :
  - **PROP. 1** — déplacer seuils YuNet (`SCORE_THRESHOLD`, `NMS_THRESHOLD`, `TOP_K`, `margin`) vers `config.py`. **Non faite le 23/10.**
  - **PROP. 3** — convertir `src/` en package Python (`__init__.py` + imports relatifs). **Non faite le 23/10.**
  - **PROP. 5** — ajouter `CHROMA_DIR` à `config.py` quand le bonus C sera réalisé. **Non faite le 23/10 (normal, bonus C différé).**
- **Bonus C — différé** : ChromaDB non installé, reprise quand une vraie question de scaling se posera.

---

**Rappel de prochaine étape immédiate** : colle-moi `src/config.py` + `src/database.py` actuels (et idéalement le diff de `_detect_faces`). Je te confirmerai en 2 lignes si `vector_search.py` fonctionne toujours tel quel, ou s'il faut une correction minimale.
