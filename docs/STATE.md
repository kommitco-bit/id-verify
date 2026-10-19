# STATE.md — mis à jour le 19/10, jour 9, avec DeepSeek

## Terminé et testé

- **Environnement** : venv Python **3.14.4** confirmé. Contournement Qt/Wayland toujours en place (`QT_QPA_PLATFORM=xcb`).
- **Arborescence** : `~/Documents/DevOps/Projet/id-verif/` confirmée.
- **J2, J3, J4** : ESP32-CAM (`/` et `/capture`) fonctionnel, `src/capture.py` (3 sources) fonctionnel.
- **J5** : `imaging.py` (flou, resize, seuil, Otsu, Canny) fonctionnel.
- **J6 (17/10)** : `prepare_card(img) -> np.ndarray | None` fonctionnel (détection V2 + transformation de perspective + resize direct si déjà au bon format). Testé et confirmé par l'étudiant.
- **J7 (18/10) — OCR** :
  - **Tesseract 5.5.0** installé et vérifié ; pack **`fra`** présent.
  - **`pytesseract` + `Pillow`** installés dans le venv (`get_tesseract_version() == 5.5.0`).
  - **`src/ocr.py` V1 + V2** conformes au contrat §6 (`extract_fields`, `extract_raw_text`, `_preprocess`).
  - **Bug `_RE_NUM` corrigé** (`[I.L]` → `\.?[IL1]\.?`).
  - **Résultat confirmé** : **20/20 champs lus sur les 4 cartes fictives disponibles** (`carte_fictive_01..04.jpg`).
- **J8 (19/10) — Détection de visage (YuNet)** :
  - **Modèles ONNX téléchargés dans `models/`** :
    - `face_detection_yunet_2023mar.onnx` (YuNet, détection) — utilisé et fonctionnel.
    - `face_recognition_sface_2021dec.onnx` (SFace, reconnaissance) — utilisé en J9.
  - **`src/face.py` V1 créé** :
    - `_get_detector()` : charge YuNet une seule fois (singleton paresseux).
    - `_detect_faces(img) -> list[dict]` : retourne `[{bbox, landmarks, score}, ...]`.
    - `_crop_face(img, bbox, margin=0.2) -> np.ndarray | None` : recadre avec 20 % de marge.
  - **Test isolé `test/test_face_detect.py`** confirmé : 1 visage détecté sur `carte_fictive_01.jpg`, **score 0.935**.
  - **Test live `test/test_face_detect_10.py`** confirmé : **10/10 frames** avec 1 visage, scores 0.868–0.910. **Livrable J8 rempli**.
  - **WARN OpenCV bénin** : `setPreferableTarget Targets are not supported by the new graph engine for now` — avertissement OpenCV 4.9+, ignoré, inférence en **CPU**, aucun impact.
- **J9 (19/10) — Empreintes faciales (SFace)** :
  - **`src/face.py` étendu** :
    - `_get_recognizer()` : charge SFace une seule fois (singleton paresseux, symétrique à `_get_detector`).
    - **`get_embedding(img) -> np.ndarray float32 (128,) | None`** implémentée — conformité **confirmée** : `shape=(128,)`, `dtype=float32`, `is_none=False` sur `carte_fictive_01.jpg`.
    - **`compare(a, b) -> float | None`** implémentée — conformité **confirmée** : `compare(e, e) = 0.99999988` (précision float32), `None` sur `None`, `zeros`, tailles différentes.
    - Méthode : `_detect_faces` (réutilisé J8) → plus grand visage → reconstruction ligne 15 valeurs → `recognizer.alignCrop` (112×112) → `recognizer.feature` → `flatten()`.
  - **Calibration — `test/test_sface_scores.py` créé et exécuté** :
    - **6 paires** calculées (4 photos, 2 personnes A/B, angles différents).
    - **`min(score MÊME) = 0.3414`** (A1↔A2), **`0.4319`** (B1↔B2).
    - **`max(score DIFF) = 0.0352`** ; les autres DIFF : −0.0110, −0.1167, −0.0157.
    - **Séparation nette** : min(MÊME) ≫ max(DIFF) par un facteur ~10.
    - **Classification 6/6 correcte** avec `SEUIL_SFACE = 0.30` (2 VALIDE, 4 REJET).
  - **Seuil écrit dans `src/config.py`** : `SEUIL_SFACE = 0.30` + `SEUIL_SFACE_REFERENCE = 0.363`. Import et comparaison confirmés par l'étudiant (`SEUIL_SFACE = 0.3` affiché).

## En cours ou bloqué

- **Jeu de données J9 insuffisant** : livrable demandait **≥ 6 photos** ; on a **4 photos / 6 paires**. Suffisant pour **calibrer un point de départ**, insuffisant pour une calibration **statistiquement solide**. À consolider (nouvelles paires MÊME, autres angles, autre personne consentante).
- **Scores MÊME bas pour SFace** (0.34, 0.43 vs 0.5–0.8 typiques) — **pas un bug**, cohérent avec angles très différents. À **surveiller en J11+** : le domaine « live webcam » ≠ « photo imprimée », les scores pourraient encore baisser.
- **`config.py`** : toujours **incohérent avec §6** sur les seuils YuNet — `SCORE_THRESHOLD`, `NMS_THRESHOLD`, `TOP_K`, `margin` vivent **encore dans `src/face.py`**, pas dans `config.py`. Seuls `SEUIL_SFACE` et `SEUIL_SFACE_REFERENCE` ont été ajoutés (J9). **PROPOSITION en attente** ci-dessous.
- **Jeu de données J7 incomplet** : seulement **4 cartes** (`carte_fictive_01..04.jpg`) dans `data/samples/`. Cartes `05..10` absentes. Tableau J7 honnête mais sur échantillon réduit.
- **`src/imaging.py`** : V1 du cadre-guide (`prepare_card` interactif) toujours **non câblée**. Prévue pour l'étape `ui.py`.
- **Imports `src/`** : toujours gérés par `sys.path.insert` dans les tests. Solution propre (package Python) toujours en attente (**PROPOSITION** à venir).
- **IP de l'ESP32** : toujours en DHCP (`10.135.250.228`), réservation à envisager (**PROPOSITION** à venir).
- **`capture.py` en mode flux** : `get_frame` appelé 10× de suite en J8, fonctionne, mais réouverture caméra à chaque appel non vérifiée sur la durée.

## Décisions prises (et pourquoi)

- **18/10 (J7)** — `TESSERACT_PSM = 6`. Mode « bloc de texte uniforme », adapté à une carte dense.
- **18/10 (J7)** — `OCR_MIN_WIDTH = 1500`. En dessous, Tesseract confond `I/1/L`, `0/O`, `4/9`. Compromis coût CPU / qualité sur AMD 3020e.
- **18/10 (J7)** — Prétraitement `gris → upscale INTER_CUBIC → Otsu`. Upscale **avant** binarisation pour éviter les marches d'escalier.
- **18/10 (J7)** — Regex **ancrées sur les étiquettes** (`Nom :`, `NI.`, etc.) pour éliminer le bruit visuel.
- **18/10 (J7)** — Deux groupes dans `_RE_NUM` `([A-Z])\s*(\d{6,8})` + concaténation pour un numéro propre.
- **19/10 (J8)** — **Seuils YuNet** : `SCORE_THRESHOLD = 0.6`, `NMS_THRESHOLD = 0.3`, `TOP_K = 5000`. Valeurs par défaut OpenCV, testées 10/10 en live. **À déplacer dans `config.py`** (proposition en attente).
- **19/10 (J8)** — **Marge de recadrage `margin = 0.2`** (20 % autour de la bbox). Évite de couper menton/front, utile pour SFace.
- **19/10 (J8)** — **`setInputSize((w, h))` à chaque `detect()`** : YuNet attend la taille réelle (frames ESP32 ≠ cartes).
- **19/10 (J8)** — **Détection ≠ reconnaissance** : J8 = « où est le visage ? » ; J9 = « à qui ressemble-t-il ? ».
- **19/10 (J9)** — **`get_embedding` garde le plus grand visage** (`max(faces, key=w*h)`). Raison : sur une carte, YuNet peut détecter la photo **et** des reflets/bruit ; le vrai visage est la plus grande zone.
- **19/10 (J9)** — **SFace brut ne normalise pas** (`norm ≈ 13` observée). **Normalisation L2 déplacée dans `compare`**, pas dans `get_embedding`. Raison : garder `get_embedding` « brut conforme SFace », et rendre `compare` mathématiquement autonome (cosinus). Conséquence : `compare(e, e) = 0.99999988` (précision float32), suffisant pour un seuil à 0.30.
- **19/10 (J9)** — **Clamp `[-1, 1]`** dans `compare`. Raison : erreurs flottantes (~10⁻⁷) peuvent dépasser 1.0 ; on borne pour un seuil fiable.
- **19/10 (J9)** — **Garde-fous `None` + tailles + norme nulle** dans `compare`. Raison : convention §6 « renvoyer `None` au lieu de planter ».
- **19/10 (J9)** — **`SEUIL_SFACE = 0.30`** (au lieu du défaut SFace `0.363`). Justification mesurée :
  - marge **0.265** au-dessus de `max(DIFF) = 0.0352` → risque de faux positif quasi nul sur nos données.
  - marge **0.041** sous `min(MÊME) = 0.3414` → la personne A passe (**0.363 l'aurait rejetée** = faux négatif certain).
  - **0.30 ≈ 0.83 × 0.363** → compromis **côté sécurité**, pas réglage sauvage.
- **19/10 (J9)** — **`SEUIL_SFACE_REFERENCE = 0.363` conservé** dans `config.py`. Raison : documenter la valeur officielle OpenCV sans l'utiliser en décision (traçabilité / pédagogie).
- **19/10 (J9)** — **Pas de renormalisation au stockage** (J9). Les embeddings seront stockés **bruts** ; c'est `compare` qui normalise à la volée. Décision cohérente avec `get_embedding` « brut conforme SFace ».

## Signatures réelles des fonctions écrites (si elles diffèrent du contrat)

- **`src/config.py`** :
  - Section J7 : `TESSERACT_LANG = "fra"`, `TESSERACT_PSM = 6`, `OCR_MIN_WIDTH = 1500` (si présents, sinon `getattr` par défaut).
  - **Nouveau J9** : `SEUIL_SFACE = 0.30`, `SEUIL_SFACE_REFERENCE = 0.363`.
  - Pas encore : `SCORE_THRESHOLD`, `NMS_THRESHOLD`, `TOP_K`, `margin` (toujours dans `face.py`).
- **`src/imaging.py`** : inchangé depuis J6. `prepare_card(img) -> np.ndarray | None` (conforme §6). Helpers privés `_order_corners`, `_quad_min_side`, `_detect_card_quad`.
- **`src/capture.py`** : inchangé. `get_frame(source: str) -> np.ndarray | None` (conforme §6).
- **`src/ocr.py`** : inchangé depuis J7. `_preprocess`, `extract_raw_text`, `extract_fields` + regex `_RE_NOM`, `_RE_PP`, `_RE_DATE`, `_RE_NUM`.
- **`src/face.py`** — **conforme au contrat §6 sur les 2 fonctions publiques** :
  - `_get_detector() -> cv2.FaceDetectorYN` _(privée)_.
  - `_detect_faces(img) -> list[dict]` _(privée)_.
  - `_crop_face(img, bbox, margin=0.2) -> np.ndarray | None` _(privée)_.
  - **`_get_recognizer() -> cv2.FaceRecognizerSF | None`** _(privée, nouveau J9)_.
  - **`get_embedding(img) -> np.ndarray float32 (128,) | None`** ✅ **écrite et testée**.
  - **`compare(emb_a, emb_b) -> float | None`** ✅ **écrite et testée**.
  - Constantes module : `YUNET_MODEL`, `SFACE_MODEL`, `SCORE_THRESHOLD`, `NMS_THRESHOLD`, `TOP_K`.
- **Tests** :
  - `test/test_face_detect.py`, `test/test_face_detect_10.py` (J8), inchangés.
  - **`test/test_sface_scores.py`** (nouveau J9) : `main()`, `ITEMS`, `SAMPLES`. Calcule embeddings + 6 paires + stats + suggestion de seuil.
  - `test/test_ocr_raw.py`, `test/demo_quad.py`, `test/demo_perspective.py`, `test/test_prepare_card.py` : inchangés.

## Valeurs importantes (seuils, IP de l'ESP32, chemins)

- Racine projet : `~/Documents/DevOps/Projet/id-verif/`
- Python : 3.14.4 (dans `env/`)
- ESP32-CAM : IP `10.135.250.228` (DHCP)
- Taille cible carte : 1000 × 630 px (ratio ≈ 1.587)
- **Seuils `prepare_card` (J6)** : tolérance ratio 10 %, taille min « déjà carte » 600×375, epsilon `approxPolyDP` 0.01–0.08, rectangularité ≥ 0.55, aire quad ≥ 5 %, côté min quad 150 px.
- **Seuils OCR (J7)** : `TESSERACT_LANG = "fra"`, `TESSERACT_PSM = 6`, `OCR_MIN_WIDTH = 1500`.
- **Seuils YuNet (J8, dans `src/face.py`)** : `SCORE_THRESHOLD = 0.6`, `NMS_THRESHOLD = 0.3`, `TOP_K = 5000`. Marge `margin = 0.2`.
- **Seuils SFace (J9, dans `src/config.py`)** :
  - **`SEUIL_SFACE = 0.30`** (décision).
  - `SEUIL_SFACE_REFERENCE = 0.363` (documentation).
- **Calibration J9 (19/10)** : `min(MÊME) = 0.3414`, `0.4319` ; `max(DIFF) = 0.0352` ; autres DIFF −0.0110, −0.1167, −0.0157. **6/6 corrects à 0.30**.
- **Modèles** : `models/face_detection_yunet_2023mar.onnx` (chargé J8), `models/face_recognition_sface_2021dec.onnx` (chargé J9).
- Variable d'environnement Qt : `QT_QPA_PLATFORM=xcb`.
- **Tesseract** : version **5.5.0**, packs `fra` + `eng` + `osd` présents.

## Notions apprises (pour me réinterroger plus tard)

- **J6 — Contours, polygones, perspective, ratio d'image** (conservées).
- **J7 — OCR** : pixels → caractères. Tesseract segmente en lignes → mots → caractères. Préfère le noir-sur-blanc binaire.
- **J7 — `pytesseract` vs `Tesseract`** : télécommande Python ↔ moteur système séparé.
- **J7 — PSM** : `6` = bloc uniforme (adapté aux cartes).
- **J7 — Prétraitement OCR** : `gris → upscale INTER_CUBIC → Otsu`.
- **J7 — Regex** : `\s*`, `[A-Za-zÀ-ÿ]`, `\.?`, walrus `:=`.
- **J7 — Piège classe de caractères** : `[I.L]` = « I ou . ou L ».
- **J7 — Ancrage sur étiquette** vs recherche « n'importe où ».
- **J7 — `re.fullmatch` vs `glob`**.
- **J7 — Confusions Tesseract** : `I ↔ L ↔ 1`, `0 ↔ O`, `4 ↔ 9`.
- **J8 — Détection ≠ reconnaissance** : détection = « où ? » ; reconnaissance = « qui ? ». Notion clé.
- **J8 — Boîte englobante (bbox)** : `(x, y, w, h)`.
- **J8 — Points de repère (landmarks)** : 5 points (yeux, nez, coins de bouche).
- **J8 — Modèle ONNX** : « filtre préfabriqué » exécutable par OpenCV sans réentraîner.
- **J8 — Inférence** : passage d'une image dans le modèle pour obtenir un résultat.
- **J8 — `cv2.FaceDetectorYN`** : sortie `(N, 15)` par frame (4 bbox + 10 landmarks + 1 score).
- **J8 — Singleton paresseux** : chargé une fois, réutilisé ensuite.
- **J8 — `setInputSize` avant `detect`** : taille réelle requise.
- **J8 — WARN OpenCV 4.9+** : bénin.
- **J9 — Embedding (empreinte faciale)** : vecteur de 128 float32 qui résume un visage. Deux photos de la même personne → vecteurs proches.
- **J9 — Entraînement vs inférence** : SFace est déjà entraîné ; on fait **uniquement de l'inférence** (aucun réentraînement).
- **J9 — `alignCrop`** : recadre et **aligne** le visage à 112×112 selon les 5 landmarks. **Obligatoire** pour SFace.
- **J9 — `FaceRecognizerSF.create(model, "")`** : instance SFace. Config vide = valeurs par défaut OpenCV.
- **J9 — Similarité cosinus** : `dot(a,b)/(‖a‖·‖b‖)`. Mesure l'**angle**, pas la longueur. Résultat `[-1, 1]`. Insensible à la norme (d'où norme 13 neutralisée).
- **J9 — SFace brut n'est pas normalisé** (norme ~13). La normalisation L2 se fait dans `compare`.
- **J9 — Précision float32** : `compare(e, e) ≈ 0.99999988` (résidu ~10⁻⁷). N'affecte **pas** la décision à un seuil de 0.30.
- **J9 — Seuil de décision** : frontière « même personne » vs « différentes ». Analogie alarme de bruit.
- **J9 — Faux positif (FAR)** : deux personnes différentes acceptées comme identiques → **grave** (usurpation).
- **J9 — Faux négatif (FRR)** : même personne rejetée → **pénible** (utilisateur doit recommencer).
- **J9 — Compromis de seuil** : privilégier la **sécurité** (minimiser FAR) tout en gardant de la marge sous le signal.
- **J9 — Marge de séparation** : `lo = max(DIFF)`, `hi = min(MÊME)`. Si `hi > lo`, tout seuil dans `(lo, hi)` sépare **parfaitement** l'échantillon.
- **J9 — `itertools.combinations`** : `n` photos → `n(n−1)/2` paires (4 photos → 6 paires).

## Prochaine étape

- **J1 à J9 clos** (avec **réserve documentée** sur l'échantillon J9).
- **À faire en début de prochaine session** :
  - **Fournir la section J10** de la feuille de route avant tout code (règle §7).
  - Attendu J10 (à confirmer par la feuille) : selon le brief, `database.py` (`init_db`, `add_person`, `get_person_by_number`, `log_verification`) et/ou `vector_search.py` (`find_nearest(embedding, k=3) -> list[(person_id, score)]`, force brute numpy).
- **Points à consolider après J9 (aucun urgent)** :
  - **Recalibrer SFace** dès que **paires MÊME supplémentaires** disponibles (angles variés, autres personnes consentantes). Recalculer `min(MÊME)` et `max(DIFF)`, ajuster `SEUIL_SFACE` dans `config.py`.
  - **Surveiller live vs carte** en J11+ : les scores pourraient baisser (domaine différent). Si `min(MÊME_live)` < 0.30 → ajuster.
  - Regénérer `carte_fictive_05..10` pour solidifier le tableau J7 (échantillon 10/10).
  - Réservation DHCP pour l'ESP32.
  - Gestion propre des imports `src/` (package vs `sys.path`).
  - Harmoniser `demo_step.py` / `demo_steps.py`.
  - Étudier un mode « flux continu » dans `capture.py` si la réouverture caméra pose problème.
- **Propositions en attente (aucune appliquée)** :
  - **PROPOSITION DE CHANGEMENT** : déplacer `SCORE_THRESHOLD`, `NMS_THRESHOLD`, `TOP_K`, `margin` dans `src/config.py` (cohérence §6 « tous les seuils vivent dans `config.py` »). Raison : centralisation, cohérence avec `SEUIL_SFACE` déjà migré. À appliquer en même temps qu'un éventuel futur déplacement, pas isolément.
  - **PROPOSITION DE CHANGEMENT** : remplacer `face[:4].astype(int)` par `(int(v) for v in face[:4])` dans `_detect_faces`. Raison : logs propres (`np.int64(...)` actuellement dans la sortie), aucun impact fonctionnel.
  - **PROPOSITION DE CHANGEMENT** : convertir `src/` en **package Python** (`__init__.py` + imports relatifs) pour supprimer les `sys.path.insert` dans les tests. Raison : propreté, éviter les collisions de noms avec des modules standard. À discuter avant de toucher aux imports (impacte tous les tests).
