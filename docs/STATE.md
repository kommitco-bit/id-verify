# STATE.md — mis à jour le 25/10, jour 13, avec DeepSeek

## Terminé et testé

- **Environnement** : venv Python **3.14.4** confirmé. Contournement Qt/Wayland (`QT_QPA_PLATFORM=xcb`) toujours en place.
- **Arborescence** : `~/Documents/DevOps/Projet/id-verif/` confirmée. Dossier de tests réel : `test/` (singulier).
- **J2 à J12** : Clos et confirmés (ESP32-CAM, `capture`, `imaging`, `ocr`, `face` YuNet/SFace, base SQLite, `vector_search`, `decision.py` 8/8 OK).
- **J13 (25/10) — Pipeline et interface** ✅ confirmé :
  - **`src/pipeline.py`** : `verify(card_source, face_source)` conforme §6. Orchestre `capture -> imaging -> ocr -> face -> database -> decision -> log`. Testé en CLI : renvoie d'abord `ANOMALIE` (numéro absent), puis `VALIDE` après enrôlement (score 0.7905).
  - **`test/test_enroll_from_card.py`** : Script d'enrôlement créé et exécuté avec succès (idempotent, insertion de `B8078673`).
  - **`src/ui.py`** : Interface customtkinter complète. Boutons de capture, affichage coloré du statut (Rouge/Orange/Vert), zone de log pour les raisons. Utilisation d'un **thread** + `self.after` pour ne pas figer l'UI. Testé et validé par capture d'écran (cas "carte illisible" → `ANOMALIE` gérée sans crash).

## En cours ou bloqué

- **Vérification des prop. 2 et 4 (rapportées OK verbalement le 24/10, à re-confirmer par collage)** :
  - **Prop. 2** (`(int(v) for v in face[:4])` dans `_detect_faces`) : code et sortie des tests `test_face_detect*.py` et `test_sface_scores.py` toujours **non collés**.
  - **Prop. 4** (migration `DB_PATH` et `VALID_STATUSES` vers `src/config.py`) : code de `config.py` / `database.py` toujours **non collé**.
- **`FICT-004` absent de la base** : Toujours absent. Contourné pour J13 par l'enrôlement du numéro `B8078673` (id=5) issu de `carte_fictive_01.jpg`.
- **Calibration `SEUIL_SFACE` fragile** : Marge observée sur le visage du jour (0.7905), ce qui est rassurant, mais à consolider sur un jeu de données plus large.
- **`src/ui.py`** : L'URL de l'ESP32 (`ESP32_URL = "http://10.135.250.228/capture"`) y est codée en dur (à déplacer dans `config.py` via PROP. 6).
- **IP ESP32** : DHCP `10.135.250.228`, réservation à envisager.
- **Jeux de données** : J7 incomplet (4 cartes), J9 insuffisant (4 photos / 6 paires).

## Décisions prises (et pourquoi)

- **18/10 au 24/10 (J7 à J12)** : _(Voir historique, inchangé : Tesseract PSM 6, YuNet seuils 0.6/0.3, SFace L2 + clamp, SQLite UNIQUE numero/BLOB, force brute numpy, agrégation par le pire statut, R1 court-circuit, SCORE_FACE_REJECT=0.20)._
- **25/10 (J13) — Séparation stricte Pipeline / UI** : `pipeline.py` gère la logique métier (aucune dépendance à tkinter), `ui.py` gère l'affichage. Permet de tester en CLI sans ouvrir de fenêtre.
- **25/10 (J13) — Sauvegarde temporaire des captures UI** : L'UI utilise `tempfile.mkstemp(suffix=".jpg", dir="data/samples")` et `cv2.imwrite` pour passer une chaîne `file:...` au pipeline (qui respecte le contrat §6), plutôt que de modifier le contrat pour accepter des `np.ndarray`.
- **25/10 (J13) — Threading et rafraîchissement GUI** : Appel de `pipeline.verify` dans un `threading.Thread(daemon=True)`. Le retour UI se fait obligatoirement via `self.after(0, self._show, res)` pour respecter le thread principal (thread-safety de Tkinter).
- **25/10 (J13) — Anti double-clic** : Désactivation du bouton "Vérifier" (`state="disabled"`) pendant l'exécution du thread, réactivé dans `_show` à la fin.
- **25/10 (J13) — Enrôlement idempotent** : `test_enroll_from_card.py` vérifie `get_person_by_number` avant `add_person` pour éviter les `IntegrityError` et permettre de relancer le script à volonté.

## Signatures réelles des fonctions écrites (si elles diffèrent du contrat)

- **`src/config.py`** : _(Inchangé)_ `TESSERACT_LANG="fra"`, `TESSERACT_PSM=6`, `OCR_MIN_WIDTH=1500`, `SEUIL_SFACE=0.30`, `SEUIL_SFACE_REFERENCE=0.363`, `SCORE_FACE_REJECT=0.20`, `DB_PATH`, `VALID_STATUSES`.
- **`src/imaging.py`** : `prepare_card(img) -> np.ndarray | None` (conforme).
- **`src/capture.py`** : `get_frame(source: str) -> np.ndarray | None` (conforme).
- **`src/ocr.py`** : `extract_fields(card_img) -> dict` (conforme).
- **`src/face.py`** : `get_embedding(img)`, `compare(emb_a, emb_b)` (conformes).
- **`src/database.py`** : 4/4 fonctions §6 (conforme).
- **`src/vector_search.py`** : `find_nearest(embedding, k=3)` (conforme).
- **`src/decision.py`** : `decide(fields, card_emb, live_emb, person)` (conforme).
- **`src/pipeline.py`** (nouveau J13) ✅ :
  - `verify(card_source, face_source) -> dict` **conforme §6**.
  - Helpers privés : `_safe_card(card_source)`, `_safe_live(face_source)`.
  - Importe `capture`, `imaging`, `ocr`, `face`, `database`, `decision`.
- **`src/ui.py`** (nouveau J13) ✅ :
  - Classe `App(ctk.CTk)`.
  - Méthodes : `_capture(attr)`, `on_verify()`, `_run_verify()`, `_show(res)`.
  - Constantes module : `ESP32_URL`, `COLORS`.

## Valeurs importantes (seuils, IP de l'ESP32, chemins)

- Racine projet : `~/Documents/DevOps/Projet/id-verif/`
- Python : 3.14.4 (dans `env/`)
- ESP32-CAM : IP `10.135.250.228` (DHCP) — Utilisée dans `ui.py`.
- Taille cible carte : 1000 × 630 px
- Seuils `prepare_card` : tolérance 10%, taille min 600×375, epsilon 0.01-0.08, rect ≥ 0.55.
- Seuils OCR : `fra`, PSM 6, `OCR_MIN_WIDTH = 1500`.
- Seuils YuNet : `0.6 / 0.3 / 5000`, `margin=0.2`.
- Seuils SFace : `SEUIL_SFACE = 0.30`, `SCORE_FACE_REJECT = 0.20`.
- Modèles : `models/face_detection_yunet_2023mar.onnx`, `models/face_recognition_sface_2021dec.onnx`.
- Variable Qt : `QT_QPA_PLATFORM=xcb`.
- Base SQLite : `data/db/id_verif.db`.
- **Personnes actuellement en base** : 5 lignes — `id=1 FICT-001`, `id=2 FICT-002`, `id=3 FICT-003`, `id=4 SYNTH-005`, `id=5 B8078673`.
- **Format `scores`** : `{score_face: float|None, numero_trouve: bool, ocr_ok: bool, champs_manquants: list[str], date_valide: bool}`.

## Notions apprises (pour me réinterroger plus tard)

_(J6 à J12 : inchangés)_

**J13 — Pipeline et Interface** : **Pipeline** = chaîne de montage (sortie d'un module = entrée du suivant) ; **Événement GUI** = action utilisateur (clic) déclenchant une fonction (callback) ; **Thread** = fil d'exécution séparé pour ne pas geler l'UI ; **Thread-safety Tkinter** = on ne touche pas aux widgets depuis un thread secondaire, on utilise `self.after()` pour repasser sur le thread principal ; **`daemon=True`** = le thread meurt si la fenêtre principale se ferme ; **fichier temporaire** (`tempfile`) = fichier éphémère pour respecter un contrat de type `str` (source) sans modifier la signature.

## Prochaine étape

- **J1 à J13 clos** (J13 confirmé le 25/10 avec capture d'écran de l'UI et validation orale "tout est bon").
- **Avant J14 — vérifications à faire (rappel, non bloquant)** :
  1. **Coller le contenu de `src/config.py` et `src/database.py`** (prop. 4).
  2. **Coller le diff de `_detect_faces` dans `src/face.py`** (prop. 2).
  3. **Re-passer les tests** impactés par les prop. 2 et 4.
- **Début de J14 — à faire avant tout code** : fournir la **section J14** de la feuille de route.
- **Propositions restant en attente (aucune appliquée)** :
  - **PROP. 1** — déplacer seuils YuNet vers `config.py`.
  - **PROP. 3** — convertir `src/` en package Python (`__init__.py` + imports relatifs).
  - **PROP. 5** — ajouter `CHROMA_DIR` à `config.py` quand bonus C réalisé.
  - **PROP. 6** — déplacer `ESP32_URL` de `ui.py` vers `config.py`. (Nouveau J13).
- **Bonus C — différé** : ChromaDB non installé.
