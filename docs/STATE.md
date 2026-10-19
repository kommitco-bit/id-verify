# STATE.md — mis à jour le 19/10, jour 8, avec DeepSeek

<!-- Si tu es encore le 18/10, ajuste la date en tête -->

## Terminé et testé

- **Environnement** : venv Python **3.14.4** confirmé. Contournement Qt/Wayland toujours en place (`QT_QPA_PLATFORM=xcb`).
- **Arborescence** : `~/Documents/DevOps/Projet/id-verif/` confirmée.
- **J2, J3, J4** : ESP32-CAM (`/` et `/capture`) fonctionnel, `src/capture.py` (3 sources) fonctionnel.
- **J5** : `imaging.py` (flou, resize, seuil, Otsu, Canny) fonctionnel.
- **J6 (17/10)** : `prepare_card(img) -> np.ndarray | None` fonctionnel (détection V2 + transformation de perspective + resize direct si déjà au bon format). Testé et confirmé par l’étudiant.
- **J7 (18/10) — OCR** :
  - **Tesseract 5.5.0** installé et vérifié ; pack **`fra`** présent.
  - **`pytesseract` + `Pillow`** installés dans le venv (`get_tesseract_version() == 5.5.0`).
  - **`src/ocr.py` V1 + V2** conformes au contrat §6 (`extract_fields`, `extract_raw_text`, `_preprocess`).
  - **Bug `_RE_NUM` corrigé** (`[I.L]` → `\.?[IL1]\.?`).
  - **Résultat confirmé** : **20/20 champs lus sur les 4 cartes fictives disponibles** (`carte_fictive_01..04.jpg`).
- **J8 (19/10) — Détection de visage (YuNet)** :
  - **Modèles ONNX téléchargés dans `models/`** :
    - `face_detection_yunet_2023mar.onnx` (YuNet, détection) — utilisé et fonctionnel.
    - `face_recognition_sface_2021dec.onnx` (SFace, réservé J9) — téléchargé, **non utilisé encore**.
  - **`src/face.py` V1 créé** :
    - `_get_detector()` : charge YuNet une seule fois (singleton paresseux).
    - `_detect_faces(img) -> list[dict]` : retourne `[{bbox, landmarks, score}, ...]`.
    - `_crop_face(img, bbox, margin=0.2) -> np.ndarray | None` : recadre avec 20 % de marge.
  - **Test isolé `test/test_face_detect.py`** confirmé par l’étudiant : 1 visage détecté sur `carte_fictive_01.jpg`, **score 0.935**, recadrage sauvegardé.
  - **Test live `test/test_face_detect_10.py`** confirmé par l’étudiant : **10/10 frames** avec 1 visage, scores 0.868–0.910. **Livrable J8 rempli**.
  - **WARN OpenCV bénin** : `setPreferableTarget Targets are not supported by the new graph engine for now` — avertissement OpenCV 4.9+, ignoré, inférence en **CPU**, aucun impact.

## En cours ou bloqué

- **`get_embedding` et `compare` (SFace)** : **non implémentées**, prévues J9. Ne pas anticiper sans la section J9 de la feuille de route.
- **`config.py`** : toujours inchangé pour J8. Seuils YuNet (`SCORE_THRESHOLD = 0.6`, `NMS_THRESHOLD = 0.3`, `TOP_K = 5000`) vivent encore **dans `src/face.py`**, pas dans `config.py` (écart à la convention §6 → PROPOSITION en attente ci-dessous).
- **Jeu de données J7 incomplet** : seulement **4 cartes** (`carte_fictive_01..04.jpg`) dans `data/samples/`. Cartes `05..10` absentes. Le tableau J7 (20/20 sur 4 cartes) est **honnête mais sur échantillon réduit** → à régénérer quand pertinent.
- **`src/imaging.py`** : V1 du cadre-guide (`prepare_card` interactif) toujours **non câblée**. Prévue pour l’étape `ui.py`.
- **Imports `src/`** : toujours gérés par `sys.path.insert` dans les tests. Solution propre (package Python) toujours en attente (PROPOSITION à venir).
- **IP de l’ESP32** : toujours en DHCP (`10.135.250.228`), réservation à envisager (PROPOSITION à venir).
- **`capture.py` en mode flux** : `get_frame` est appelé 10 fois de suite dans le test J8 ; ça fonctionne mais on n’a pas vérifié si la caméra est rouverte à chaque appel. Si lent ou instable, étudier un mode « flux continu » sans changer le contrat §6.

## Décisions prises (et pourquoi)

- **18/10 (J7)** — `TESSERACT_PSM = 6`. Mode « bloc de texte uniforme », adapté à une carte dense.
- **18/10 (J7)** — `OCR_MIN_WIDTH = 1500`. En dessous, Tesseract confond `I/1/L`, `0/O`, `4/9`. Compromis coût CPU / qualité sur AMD 3020e.
- **18/10 (J7)** — Prétraitement `gris → upscale INTER_CUBIC → Otsu`. Upscale **avant** binarisation pour éviter les marches d’escalier.
- **18/10 (J7)** — Regex **ancrées sur les étiquettes** (`Nom :`, `NI.`, etc.) pour éliminer le bruit visuel.
- **18/10 (J7)** — Deux groupes dans `_RE_NUM` `([A-Z])\s*(\d{6,8})` + concaténation pour un numéro propre.
- **18/10 (J7)** — Filtre `re.fullmatch(r"carte_fictive_\d{2}\.jpg", ...)` dans le test, robuste aux futures variantes.
- **19/10 (J8)** — **Seuils YuNet** : `SCORE_THRESHOLD = 0.6`, `NMS_THRESHOLD = 0.3`, `TOP_K = 5000`. Valeurs par défaut OpenCV, testées sur 10 frames live → **10/10**. À déplacer dans `config.py` (proposition en attente).
- **19/10 (J8)** — **Marge de recadrage `margin = 0.2`** (20 % autour de la bbox). Raison : évite de couper menton/front, utile pour SFace en J9.
- **19/10 (J8)** — **`setInputSize((w, h))` appelé à chaque `detect()`**. Raison : YuNet attend la taille réelle de l’image (les frames ESP32 et cartes n’ont pas la même dimension).
- **19/10 (J8)** — **Détection ≠ reconnaissance** : J8 ne fait que « où est le visage ? ». La reconnaissance (empreinte + comparaison) est **strictement** J9.
- **19/10 (J8)** — **WARN OpenCV ignoré**. `setPreferableTarget … new graph engine` = avertissement OpenCV 4.9+ sans impact, l’inférence tourne en CPU comme attendu.

## Signatures réelles des fonctions écrites (si elles diffèrent du contrat)

- **`src/config.py`** : toujours inchangé (contient `TESSERACT_LANG`, `TESSERACT_PSM`, `OCR_MIN_WIDTH` si présents, sinon valeurs par défaut via `getattr`). Pas de section J8 encore.
- **`src/imaging.py`** : inchangé depuis J6.
  - `prepare_card(img) -> np.ndarray | None` (conforme contrat §6).
  - Helpers privés : `_order_corners`, `_quad_min_side`, `_detect_card_quad`.
- **`src/capture.py`** : inchangé. `get_frame(source: str) -> np.ndarray | None`.
- **`src/ocr.py`** : inchangé depuis J7 (conforme contrat §6).
  - `_preprocess`, `extract_raw_text`, `extract_fields`.
  - Regex module : `_RE_NOM`, `_RE_PP`, `_RE_DATE`, `_RE_NUM`.
- **`src/face.py`** (nouveau J8, partiel — **pas conforme au contrat complet §6**) :
  - `_get_detector() -> cv2.FaceDetectorYN` _(privée)_
  - `_detect_faces(img: np.ndarray) -> list[dict]` _(privée, pas dans le contrat §6)_
  - `_crop_face(img: np.ndarray, bbox: tuple, margin: float = 0.2) -> np.ndarray | None` _(privée, pas dans le contrat §6)_
  - Constantes module : `YUNET_MODEL`, `SFACE_MODEL`, `SCORE_THRESHOLD`, `NMS_THRESHOLD`, `TOP_K`.
  - **`get_embedding(img)` : NON écrite** (J9).
  - **`compare(emb_a, emb_b)` : NON écrite** (J9).
- **Tests** :
  - `test/test_face_detect.py` (nouveau J8) : `main()`.
  - `test/test_face_detect_10.py` (nouveau J8) : `main()`, `SOURCE`, `N_FRAMES`, `DELAY_S`.
  - `test/test_ocr_raw.py`, `test/demo_quad.py`, `test/demo_perspective.py`, `test/test_prepare_card.py` : inchangés.

## Valeurs importantes (seuils, IP de l’ESP32, chemins)

- Racine projet : `~/Documents/DevOps/Projet/id-verif/`
- Python : 3.14.4 (dans `env/`)
- ESP32-CAM : IP `10.135.250.228` (DHCP)
- Taille cible carte : 1000 × 630 px (ratio ≈ 1.587)
- **Seuils `prepare_card` (J6)** : tolérance ratio 10 %, taille min « déjà carte » 600×375, epsilon `approxPolyDP` 0.01–0.08, rectangularité ≥ 0.55, aire quad ≥ 5 %, côté min quad 150 px.
- **Seuils OCR (J7)** : `TESSERACT_LANG = "fra"`, `TESSERACT_PSM = 6`, `OCR_MIN_WIDTH = 1500`.
- **Seuils YuNet (J8, dans `src/face.py`)** : `SCORE_THRESHOLD = 0.6`, `NMS_THRESHOLD = 0.3`, `TOP_K = 5000`. Marge recadrage `margin = 0.2`.
- **Modèles** : `models/face_detection_yunet_2023mar.onnx` (YuNet, chargé J8), `models/face_recognition_sface_2021dec.onnx` (SFace, chargé J9).
- Seuil similarité SFace : `0.363` (à calibrer en J9+).
- Variable d’environnement Qt : `QT_QPA_PLATFORM=xcb`.
- **Tesseract** : version **5.5.0**, packs `fra` + `eng` + `osd` présents.

## Notions apprises (pour me réinterroger plus tard)

- **J6 — Contours, polygones, perspective, ratio d’image** (conservées).
- **J7 — OCR** : pixels → caractères. Tesseract segmente en lignes → mots → caractères. Préfère le noir-sur-blanc binaire.
- **J7 — `pytesseract` vs `Tesseract`** : télécommande Python ↔ moteur système séparé.
- **J7 — PSM** : `6` = bloc uniforme (adapté aux cartes).
- **J7 — Prétraitement OCR** : `gris → upscale INTER_CUBIC → Otsu`.
- **J7 — Regex** : `\s*`, `[A-Za-zÀ-ÿ]`, `\.?`, walrus `:=`.
- **J7 — Piège classe de caractères** : `[I.L]` = « I ou . ou L ».
- **J7 — Ancrage sur étiquette** vs recherche de valeur « n’importe où ».
- **J7 — `re.fullmatch` vs `glob`** : robuste aux variantes de noms de fichiers.
- **J7 — Confusions Tesseract** : `I ↔ L ↔ 1`, `0 ↔ O`, `4 ↔ 9`, accents perdus sur flou.
- **J7 — Deux causes d’erreur OCR** : (1) confusion de caractères, (2) bruit visuel (armoiries, bordures).
- **J8 — Détection ≠ reconnaissance** : détection = « où est le visage ? » (bbox + 5 points) ; reconnaissance = « à qui ressemble-t-il ? » (empreinte + comparaison). Notion clé.
- **J8 — Boîte englobante (bbox)** : rectangle `(x, y, w, h)` qui entoure le visage détecté.
- **J8 — Points de repère (landmarks)** : 5 points (yeux, nez, coins de bouche) pour orienter/aligner un visage.
- **J8 — Modèle ONNX** : fichier « filtre préfabriqué » exécutable par OpenCV sans réentraîner.
- **J8 — Inférence** : passage d’une image dans le modèle pour obtenir un résultat (ici : visages détectés).
- **J8 — `cv2.FaceDetectorYN`** : classe OpenCV dédiée à YuNet ; renvoie un tableau `(N, 15)` par frame (4 bbox + 10 landmarks + 1 score).
- **J8 — Singleton paresseux** : `_detector` chargé une fois, réutilisé ensuite. Évite de recharger le modèle à chaque frame (coûteux).
- **J8 — `setInputSize` avant `detect`** : YuNet attend la taille réelle de l’image, qui varie (ESP32 vs cartes).
- **J8 — WARN OpenCV 4.9+** : `setPreferableTarget … new graph engine` = avertissement bénin, inférence en CPU.

## Prochaine étape

- **J1 à J8 clos.**
- **À faire en début de prochaine session** :
  - **Fournir la section J9** de la feuille de route avant tout code (règle §7).
  - Attendu J9 : `get_embedding(img) -> np.ndarray float32 (128)` + `compare(a, b) -> float` (similarité cosinus, seuil 0.363 à calibrer), toujours sur CPU avec SFace.
- **Propositions en attente (aucune appliquée)** :
  - **PROPOSITION DE CHANGEMENT** : déplacer `SCORE_THRESHOLD`, `NMS_THRESHOLD`, `TOP_K`, et `margin` dans `config.py` (cohérence §6 « tous les seuils vivent dans config.py »). Raison : centralisation et évite de fouiller `face.py`.
  - **PROPOSITION DE CHANGEMENT** : remplacer `face[:4].astype(int)` par `(int(v) for v in face[:4])` dans `_detect_faces`. Raison : logs propres (`np.int64(...)` actuellement dans la sortie), aucun impact fonctionnel.
- **Points à intégrer le moment venu (aucun urgent)** :
  - Regénérer `carte_fictive_05..10` pour solidifier le tableau J7 (échantillon 10/10).
  - Réservation DHCP pour l’ESP32.
  - Gestion propre des imports `src/` (package vs `sys.path`).
  - Harmoniser `demo_step.py` / `demo_steps.py`.
  - Calibrer le seuil SFace (0.363 par défaut) en J9+.
  - Étudier un mode « flux continu » dans `capture.py` si la réouverture caméra pose problème (test J8 10/10 OK mais non vérifié sur la durée).
