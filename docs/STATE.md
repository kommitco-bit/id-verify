# STATE.md — mis à jour le 22/10, jour 10, avec DeepSeek

> **Note honnêteté** : la seule étape du jour dont l'exécution a été **prouvée par sortie collée** est `init_db()` (V1). Pour `add_person`, `get_person_by_number`, `log_verification` et les deux tests `test_enroll_5.py` / `test_log_verification.py`, l'étudiant a répondu « Ok »/« OK » sans coller la sortie d'exécution. Je les ai marqués **« écrit, runtime à confirmer »** — pas « terminé et testé » — conformément à ta règle.

---

## Terminé et testé

- **Environnement** : venv Python **3.14.4** confirmé. Contournement Qt/Wayland toujours en place (`QT_QPA_PLATFORM=xcb`).
- **Arborescence** : `~/Documents/DevOps/Projet/id-verif/` confirmée.
- **J2, J3, J4** : ESP32-CAM (`/` et `/capture`) fonctionnel, `src/capture.py` (3 sources) fonctionnel.
- **J5** : `imaging.py` (flou, resize, seuil, Otsu, Canny) fonctionnel.
- **J6 (17/10)** : `prepare_card(img) -> np.ndarray | None` fonctionnel (détection V2 + perspective + resize direct). Testé et confirmé.
- **J7 (18/10) — OCR** : Tesseract **5.5.0** + pack `fra` présents ; `pytesseract` + `Pillow` installés ; `src/ocr.py` V1+V2 conformes §6 (`extract_fields`, `extract_raw_text`, `_preprocess`) ; bug `_RE_NUM` corrigé ; **20/20 champs lus sur 4 cartes fictives**.
- **J8 (19/10) — Détection YuNet** : modèles `.onnx` dans `models/` ; `src/face.py` V1 (`_get_detector`, `_detect_faces`, `_crop_face`) ; `test_face_detect.py` (score 0.935) et `test_face_detect_10.py` (10/10 frames, 0.868–0.910) confirmés. WARN OpenCV `setPreferableTarget` bénin, CPU only.
- **J9 (19/10) — Empreintes SFace** : `_get_recognizer`, `get_embedding` (128 float32), `compare` (cosinus, clamp `[-1,1]`, garde-fous `None`) écrites et testées ; `test_sface_scores.py` sur 6 paires (`min MÊME = 0.3414`, `max DIFF = 0.0352`, 6/6 corrects à `SEUIL_SFACE = 0.30`). Seuil migré dans `config.py`.
- **J10 (22/10) — `init_db()` (V1)** : **exécution confirmée par sortie collée**.
  - `data/db/id_verif.db` créé.
  - Tables observées : `['persons', 'sqlite_sequence', 'verifications']`. `sqlite_sequence` est créée automatiquement par SQLite (conséquence d'`AUTOINCREMENT`), ce n'est pas un bug.

## En cours ou bloqué

- **J10 — `src/database.py` V3 (code écrit, runtime à confirmer)** :
  - `add_person` et `get_person_by_number` : écrits (V2). L'étudiant a dit « Ok » sans coller la sortie de `python -c "...; print('imports OK')"`. **À exécuter en début de J11.**
  - `log_verification` : écrit (V3). **Idem — sortie non collée.**
- **J10 — `test/test_enroll_5.py`** : écrit (enrôle 4 cartes + 1 synthétique seed=42, vérifie la ronde-trip `tobytes ↔ frombuffer` via `compare`). **Non exécuté à ce stade.**
- **J10 — `test/test_log_verification.py`** : écrit (2 passages, relecture JSON). **Non exécuté à ce stade.**
- **Jeu de données J9 insuffisant** : 4 photos / 6 paires ; suffisant pour un point de départ, insuffisant pour une calibration statistiquement solide.
- **Scores MÊME bas pour SFace** (0.34, 0.43 vs 0.5–0.8 typiques) — pas un bug, à surveiller en J11+ (domaine « live webcam » ≠ « photo imprimée »).
- **`config.py` incohérent §6** sur les seuils YuNet : `SCORE_THRESHOLD`, `NMS_THRESHOLD`, `TOP_K`, `margin` vivent toujours dans `src/face.py`. Seuls `SEUIL_SFACE` et `SEUIL_SFACE_REFERENCE` ont été migrés (J9).
- **Jeu J7 incomplet** : seulement 4 cartes (`carte_fictive_01..04.jpg`), 05..10 absentes.
- **`src/imaging.py`** : V1 du cadre-guide (`prepare_card` interactif) toujours non câblée — prévue pour `ui.py`.
- **Imports `src/`** : toujours gérés par `sys.path.insert` dans les tests (solution package en attente).
- **IP ESP32** : toujours DHCP `10.135.250.228`, réservation à envisager.
- **`capture.py` en mode flux** : réouverture caméra à chaque appel, non vérifiée sur la durée.

## Décisions prises (et pourquoi)

- **18/10 (J7)** — `TESSERACT_PSM = 6`. Bloc de texte uniforme, adapté à une carte dense.
- **18/10 (J7)** — `OCR_MIN_WIDTH = 1500`. En dessous, Tesseract confond `I/1/L`, `0/O`, `4/9`. Compromis CPU / qualité sur AMD 3020e.
- **18/10 (J7)** — Prétraitement `gris → upscale INTER_CUBIC → Otsu`. Upscale **avant** binarisation.
- **18/10 (J7)** — Regex ancrées sur les étiquettes (`Nom :`, `NI.`, etc.).
- **18/10 (J7)** — Deux groupes dans `_RE_NUM` `([A-Z])\s*(\d{6,8})` + concaténation.
- **19/10 (J8)** — Seuils YuNet `SCORE_THRESHOLD=0.6`, `NMS_THRESHOLD=0.3`, `TOP_K=5000` (défauts OpenCV, 10/10 en live). **À déplacer dans `config.py`** (proposition).
- **19/10 (J8)** — Marge de recadrage `margin=0.2` (20 % autour de la bbox).
- **19/10 (J8)** — `setInputSize((w, h))` à chaque `detect()`. Frames ESP32 ≠ cartes.
- **19/10 (J8)** — Détection ≠ reconnaissance.
- **19/10 (J9)** — `get_embedding` garde le **plus grand** visage (`max(faces, key=w*h)`).
- **19/10 (J9)** — SFace brut ne normalise pas (norme ≈ 13). **Normalisation L2 déplacée dans `compare`**.
- **19/10 (J9)** — Clamp `[-1, 1]` dans `compare` (erreurs flottantes ~10⁻⁷).
- **19/10 (J9)** — Garde-fous `None` + tailles + norme nulle dans `compare`.
- **19/10 (J9)** — `SEUIL_SFACE = 0.30` (au lieu de 0.363) : marge **0.265** au-dessus de `max(DIFF)`, marge **0.041** sous `min(MÊME)`. `SEUIL_SFACE_REFERENCE = 0.363` conservé pour documentation.
- **19/10 (J9)** — Pas de renormalisation au stockage : embeddings bruts, `compare` normalise à la volée.
- **22/10 (J10)** — Schéma `persons` avec `numero TEXT NOT NULL UNIQUE`. Raison : un matricule est unique par définition ; contrainte **au niveau base**, pas seulement applicatif.
- **22/10 (J10)** — `embedding BLOB` stocké via `.tobytes()`, relu via `np.frombuffer(..., dtype=np.float32)`. Ronde-trip sans perte (512 octets = 128 × 4).
- **22/10 (J10)** — `add_person` **lève** `TypeError` / `ValueError` sur `embedding` non-ndarray ou mauvais dtype. Raison : **bug de code**, pas donnée absente. Convention §6 « `None` au lieu de planter » ne vise que les **données manquantes**.
- **22/10 (J10)** — Paramètre lié `?` partout dans `INSERT` / `SELECT`. Neutralise l'injection SQL.
- **22/10 (J10)** — `VALID_STATUSES` fermé dans `database.py`. Refuse tout statut hors des 3 mots exacts du contrat §6.
- **22/10 (J10)** — `log_verification` accepte `person_id = None` : passage ANOMALIE avant lookup = pas de personne associée, §6 ne l'interdit pas.
- **22/10 (J10)** — `scores` stocké en `TEXT` JSON (`json.dumps(..., ensure_ascii=False, default=float)`). Raison : lisible via `sqlite3 CLI`, debug facilité. `default=float` neutralise tout `np.float32` résiduel.
- **22/10 (J10)** — `test_enroll_5.py` force `fields["numero"] = "FICT-00i"` au lieu du numero OCR. Raison : `UNIQUE` rejetterait 2 cartes de la même personne (A1/A2 partagent probablement le même numero OCR). On accepte le doublon facial pour tester J11+ (« même visage, deux cartes » = ANOMALIE).
- **22/10 (J10)** — 5ᵉ personne synthétique `rng.standard_normal(128).astype(np.float32)` avec `seed=42`. Reproductibilité, pas de nouvelle photo consentie sous la main, l'objet du test est la ronde-trip BLOB, pas la reconnaissance.
- **22/10 (J10)** — Tolérance `abs(score - 1.0) < 1e-4` dans `test_enroll_5.py`. Raison : `compare(e, e) ≈ 0.99999988` (résidu float32 J9) — `== 1.0` strict échouerait.

## Signatures réelles des fonctions écrites (si elles diffèrent du contrat)

- **`src/config.py`** :
  - `TESSERACT_LANG = "fra"`, `TESSERACT_PSM = 6`, `OCR_MIN_WIDTH = 1500`.
  - `SEUIL_SFACE = 0.30`, `SEUIL_SFACE_REFERENCE = 0.363`.
  - **Toujours absents** : `SCORE_THRESHOLD`, `NMS_THRESHOLD`, `TOP_K`, `margin`, `DB_PATH`, `VALID_STATUSES`.
- **`src/imaging.py`** : `prepare_card(img) -> np.ndarray | None` (conforme §6). Helpers `_order_corners`, `_quad_min_side`, `_detect_card_quad`.
- **`src/capture.py`** : `get_frame(source: str) -> np.ndarray | None` (conforme §6).
- **`src/ocr.py`** : `_preprocess`, `extract_raw_text`, `extract_fields` + regex `_RE_NOM`, `_RE_PP`, `_RE_DATE`, `_RE_NUM`.
- **`src/face.py`** :
  - `_get_detector()`, `_detect_faces(img)`, `_crop_face(img, bbox, margin=0.2)`, `_get_recognizer()` (privées).
  - `get_embedding(img) -> np.ndarray float32 (128,) | None` ✅
  - `compare(emb_a, emb_b) -> float | None` ✅
  - Constantes module : `YUNET_MODEL`, `SFACE_MODEL`, `SCORE_THRESHOLD`, `NMS_THRESHOLD`, `TOP_K`.
- **`src/database.py`** — **4/4 fonctions du contrat §6 écrites (V3)** :
  - `init_db() -> None` ✅ **exécuté, sortie confirmée**.
  - `add_person(fields: dict, embedding: np.ndarray) -> int` ⚠️ écrit, runtime à confirmer.
  - `get_person_by_number(numero: str) -> dict | None` ⚠️ écrit, runtime à confirmer. `person["embedding"]` est un `np.ndarray float32 (128,)` (pas BLOB).
  - `log_verification(person_id: int | None, status: str, scores: dict) -> None` ⚠️ écrit, runtime à confirmer.
  - Constantes module : `PROJECT_ROOT`, `DB_PATH`, `VALID_STATUSES`.
- **Tests** :
  - `test/test_enroll_5.py` (J10) ⚠️ écrit, non exécuté.
  - `test/test_log_verification.py` (J10) ⚠️ écrit, non exécuté.
  - `test/test_face_detect.py`, `test/test_face_detect_10.py`, `test/test_sface_scores.py`, `test/test_ocr_raw.py`, `test/demo_quad.py`, `test/demo_perspective.py`, `test/test_prepare_card.py` : inchangés.

## Valeurs importantes (seuils, IP de l'ESP32, chemins)

- Racine projet : `~/Documents/DevOps/Projet/id-verif/`
- Python : 3.14.4 (dans `env/`)
- ESP32-CAM : IP `10.135.250.228` (DHCP)
- Taille cible carte : 1000 × 630 px (ratio ≈ 1.587)
- Seuils `prepare_card` (J6) : tolérance ratio 10 %, taille min « déjà carte » 600×375, epsilon `approxPolyDP` 0.01–0.08, rectangularité ≥ 0.55, aire quad ≥ 5 %, côté min quad 150 px.
- Seuils OCR (J7) : `TESSERACT_LANG = "fra"`, `TESSERACT_PSM = 6`, `OCR_MIN_WIDTH = 1500`.
- Seuils YuNet (J8, dans `src/face.py`) : `SCORE_THRESHOLD = 0.6`, `NMS_THRESHOLD = 0.3`, `TOP_K = 5000`. Marge `margin = 0.2`.
- Seuils SFace (J9, dans `src/config.py`) : `SEUIL_SFACE = 0.30` (décision), `SEUIL_SFACE_REFERENCE = 0.363` (documentation).
- Calibration J9 (19/10) : `min(MÊME) = 0.3414` / `0.4319` ; `max(DIFF) = 0.0352` ; autres DIFF −0.0110, −0.1167, −0.0157. 6/6 corrects à 0.30.
- Modèles : `models/face_detection_yunet_2023mar.onnx`, `models/face_recognition_sface_2021dec.onnx`.
- Variable d'environnement Qt : `QT_QPA_PLATFORM=xcb`.
- Tesseract : version **5.5.0**, packs `fra` + `eng` + `osd`.
- **Base SQLite J10** : `~/Documents/DevOps/Projet/id-verif/data/db/id_verif.db`. Créée et confirmée.
- **Schéma `persons`** : `id INTEGER PK AUTOINCREMENT`, `nom TEXT`, `postnom TEXT`, `prenom TEXT`, `date_naissance TEXT`, `numero TEXT NOT NULL UNIQUE`, `embedding BLOB`.
- **Schéma `verifications`** : `id INTEGER PK AUTOINCREMENT`, `person_id INTEGER` (FK optionnelle, PRAGMA non activée), `status TEXT`, `scores TEXT`, `created_at TEXT DEFAULT CURRENT_TIMESTAMP`.
- **`VALID_STATUSES`** : `{"VALIDE", "ANOMALIE", "VERIFICATION_COMPLEMENTAIRE"}`.
- Personnes enrôlées par `test_enroll_5.py` (si exécuté) : `FICT-001..004` + `SYNTH-005`.

## Notions apprises (pour me réinterroger plus tard)

**J6 — Contours, polygones, perspective, ratio d'image** (conservées).

**J7 — OCR** : pixels → caractères. Tesseract segmente lignes → mots → caractères. Préfère noir-sur-blanc binaire.

- `pytesseract` vs Tesseract (télécommande ↔ moteur).
- PSM `6` = bloc uniforme.
- Prétraitement : `gris → upscale INTER_CUBIC → Otsu`.
- Regex : `\s*`, `[A-Za-zÀ-ÿ]`, `\.?`, walrus `:=`.
- Piège `[I.L]` = « I ou . ou L ».
- Ancrage sur étiquette vs « n'importe où ».
- `re.fullmatch` vs `glob`.
- Confusions Tesseract : `I ↔ L ↔ 1`, `0 ↔ O`, `4 ↔ 9`.

**J8 — Détection de visage (YuNet)** :

- Détection ≠ reconnaissance.
- bbox `(x, y, w, h)`.
- Landmarks = 5 points (yeux, nez, coins de bouche).
- Modèle ONNX = filtre préfabriqué exécutable par OpenCV.
- Inférence = passage d'une image dans le modèle.
- `cv2.FaceDetectorYN` → sortie `(N, 15)` par frame (4 bbox + 10 landmarks + 1 score).
- Singleton paresseux : chargé une fois, réutilisé.
- `setInputSize` avant `detect` : taille réelle requise.
- WARN OpenCV 4.9+ bénin.

**J9 — Empreintes faciales (SFace)** :

- Embedding = vecteur 128 float32 qui résume un visage.
- Entraînement vs inférence : SFace déjà entraîné, **on ne fait que de l'inférence**.
- `alignCrop` : recadre + aligne à 112×112 via 5 landmarks. **Obligatoire** pour SFace.
- `FaceRecognizerSF.create(model, "")` : config vide = défauts OpenCV.
- Similarité cosinus : `dot(a,b)/(‖a‖·‖b‖)`, mesure l'**angle**, résultat `[-1, 1]`, insensible à la norme.
- SFace brut non normalisé (norme ≈ 13) → L2 dans `compare`.
- Précision float32 : `compare(e,e) ≈ 0.99999988`.
- Seuil de décision = frontière même/différent (analogie alarme de bruit).
- Faux positif (FAR) = usurpation, **grave** ; faux négatif (FRR) = rejet légitime, **pénible**.
- Compromis de seuil : privilégier la sécurité (minimiser FAR).
- Marge de séparation : `lo = max(DIFF)`, `hi = min(MÊME)`. Si `hi > lo`, tout seuil dans `(lo, hi)` sépare parfaitement.
- `itertools.combinations` : `n(n−1)/2` paires.

**J10 — Base de données SQLite** :

- Table = classeur à colonnes fixes ; ligne = fiche dedans.
- Clé primaire (`PRIMARY KEY`) = identifiant unique. `AUTOINCREMENT` laisse SQLite attribuer.
- `UNIQUE NOT NULL` = refuse doublons **et** NULL sur la colonne.
- `IF NOT EXISTS` rend `CREATE` idempotent (relançable sans casser).
- BLOB = octets bruts. Aller/retour ndarray via `.tobytes()` / `np.frombuffer(..., dtype=...)`.
- `np.frombuffer` = **réinterprétation sans copie**, pas une conversion. `dtype` doit correspondre à l'origine.
- Paramètre lié `?` = échappement SQLite → neutralise l'injection SQL.
- `cur.lastrowid` = id attribué après `INSERT`.
- `row_factory = sqlite3.Row` = accès par nom de colonne (`row["nom"]`).
- `json.dumps` / `json.loads` : sérialisation dict ↔ texte. **Non symétrique** avec `np.float32` → `default=float` à l'écriture.
- **`with sqlite3.connect(...) as conn`** : gère la **transaction** (commit/rollback), **pas** la fermeture de la connexion (nuance).
- `sqlite_sequence` : table interne SQLite créée dès qu'on utilise `AUTOINCREMENT`.
- `FOREIGN KEY` écrite dans le schéma mais **non active** par défaut en SQLite (PRAGMA `foreign_keys` OFF).
- **Enrôlement** : pipeline `OCR → get_embedding → INSERT`, porte d'entrée de `persons`.
- **Fail-fast** : `raise` sur bug de code (mauvais dtype), `None` sur donnée absente. Convention §6 ne vise que le second cas.

## Prochaine étape

- **J1 à J9 clos** ; **J10 partiellement** : `init_db()` confirmé par sortie ; `add_person`, `get_person_by_number`, `log_verification`, `test_enroll_5.py`, `test_log_verification.py` **écrits mais non confirmés par exécution**.
- **Début de J11 — à faire avant tout nouveau code** :
  1. Exécuter et coller la sortie de :
     ```
     cd ~/Documents/DevOps/Projet/id-verif
     source env/bin/activate
     python -c "from src.database import init_db, add_person, get_person_by_number, log_verification; print('imports OK')"
     python test/test_enroll_5.py
     python test/test_log_verification.py
     ```
  2. Si tout passe → **J10 clos** ; sinon, diagnostic court + correction minimale.
  3. **Fournir la section J11** de la feuille de route avant tout code (règle §7).
- **Points à consolider après J9/J10 (aucun urgent)** :
  - Recalibrer SFace dès que paires MÊME supplémentaires disponibles.
  - Surveiller live vs carte en J11+ (domaine différent).
  - Regénérer `carte_fictive_05..10`.
  - Réservation DHCP pour l'ESP32.
  - Package Python propre pour `src/`.
  - Harmoniser `demo_step.py` / `demo_steps.py`.
  - Mode « flux continu » dans `capture.py` si nécessaire.
- **Propositions en attente (aucune appliquée)** :
  - **PROPOSITION** : déplacer `SCORE_THRESHOLD`, `NMS_THRESHOLD`, `TOP_K`, `margin` (YuNet) dans `src/config.py`.
  - **PROPOSITION** : remplacer `face[:4].astype(int)` par `(int(v) for v in face[:4])` dans `_detect_faces`.
  - **PROPOSITION** : convertir `src/` en package Python.
  - **PROPOSITION (nouvelle J10)** : migrer `DB_PATH` **et** `VALID_STATUSES` dans `src/config.py` (contrat §6 « tous les chemins et seuils vivent dans config.py »). Aucun impact fonctionnel.
