# STATE.md — mis à jour le 26/10, jour 15, avec DeepSeek

## Terminé et testé

- **Environnement** : venv Python **3.14.4** confirmé. Contournement Qt/Wayland (`QT_QPA_PLATFORM=xcb`) toujours en place.
- **Arborescence** : `~/Documents/DevOps/Projet/id-verif/` confirmée. Dossier de tests réel : `test/` (singulier).
- **J2 à J12** : Clos et confirmés (ESP32-CAM, `capture`, `imaging`, `ocr`, `face` YuNet/SFace, base SQLite, `vector_search`, `decision.py` 8/8 OK).
- **J13 (25/10) — Pipeline et interface** ✅ confirmé :
  - `src/pipeline.py` : `verify(card_source, face_source)` conforme §6. Orchestre `capture -> imaging -> ocr -> face -> database -> decision -> log`. Testé en CLI : `ANOMALIE` (numéro absent), puis `VALIDE` après enrôlement (score 0.7905).
  - `test/test_enroll_from_card.py` : enrôlement idempotent (insertion `B8078673`).
  - `src/ui.py` : customtkinter complet, thread + `self.after`, statuts colorés. Testé par capture d'écran (cas « carte illisible » → `ANOMALIE` sans crash).
- **J14 — volontairement sauté** (décision du 26/10, voir §Décisions). Reprise ultérieure non planifiée.
- **J15 (26/10) — Documentation (partie 1)** ✅ rédigée et **relue/confirmée** :
  - `README.md` **à la racine** (pour rendu natif GitHub). Contenu : pitch, limites assumées, prérequis (Tesseract `fra`), installation (venv + modèles ONNX + init DB), utilisation CLI + UI, table `config.py`, arborescence, tests, limites, lien DEMO, remerciements.
  - `docs/ARCHITECTURE.md`. Contenu : schéma ASCII du pipeline, tableau rôles/frontières par module, contrats §6 recopiés, flux `verify` (9 étapes + court-circuit R1), tableau choix techniques vs alternatives écartées, modèle SQLite, sécurité/vie privée, pistes d'évolution.
  - **Note d'honnêteté** : ce sont des fichiers Markdown, **pas du code exécuté**. « Confirmé » = « relecture validée par l'utilisateur », pas « testé par exécution ».

## En cours ou bloqué

- **J15 — Documentation (partie 2) : NON commencée**
  - `docs/DEMO.md` (diapositives Markdown type Marp) **pas encore produit**.
  - Mise à jour finale de `docs/STATE.md` = **ce fichier** (fait à cette session).
- **Vérification des prop. 2 et 4** (rappel, non bloquant) :
  - **Prop. 2** (`(int(v) for v in face[:4])` dans `_detect_faces`) : sorties des tests toujours **non collées**.
  - **Prop. 4** (migration `DB_PATH` et `VALID_STATUSES` vers `src/config.py`) : code de `config.py` / `database.py` toujours **non collé**.
- **`FICT-004` absent de la base** : toujours absent (contourné à J13 par `B8078673` id=5).
- **Calibration `SEUIL_SFACE` fragile** : marge observée 0.7905, à consolider sur jeu large.
- **`src/ui.py`** : `ESP32_URL` codée en dur (PROP. 6 toujours en attente).
- **IP ESP32** : DHCP `10.135.250.228`, réservation à envisager.
- **Jeux de données** : J7 incomplet (4 cartes), J9 insuffisant (4 photos / 6 paires).

## Décisions prises (et pourquoi)

- **18/10 au 24/10 (J7 à J12)** : _(Voir historique, inchangé : Tesseract PSM 6, YuNet seuils 0.6/0.3, SFace L2 + clamp, SQLite UNIQUE numero/BLOB, force brute numpy, agrégation par le pire statut, R1 court-circuit, SCORE_FACE_REJECT=0.20)._
- **25/10 (J13)** : séparation stricte Pipeline / UI ; sauvegarde temporaire des captures UI via `tempfile.mkstemp` ; threading + `self.after(0, …)` (thread-safety Tkinter) ; anti double-clic (`state="disabled"`) ; enrôlement idempotent (test avant `add_person`).
- **26/10 (J15) — J14 sauté volontairement** : l'utilisateur préfère finaliser la **présentation (J15)** maintenant et revenir à J14 (consolidation/finitions techniques) plus tard. Aucun module J14 n'est entamé.
- **26/10 (J15) — `README.md` à la racine**, pas dans `docs/` : GitHub n'affiche en page d'accueil que le `README.md` racine. C'est l'objectif explicite « présentable sur GitHub ». Les autres docs (`ARCHITECTURE`, `DEMO`, `STATE`, `PROJECT_BRIEF`) restent dans `docs/`.
- **26/10 (J15) — Dépassement de la règle « 80 lignes »** autorisé **une seule fois** pour `README.md`, sur demande explicite de l'utilisateur (exhaustivité + esthétique GitHub). `ARCHITECTURE.md` reste compact.
- **26/10 (J15) — Schéma d'architecture dans un doc séparé** (`docs/ARCHITECTURE.md`), le README pointe dessus et résume en 5 lignes. Évite un README obèse et sépare « vitrine » (README) et « référence technique » (ARCHITECTURE).
- **26/10 (J15) — Format démo = diapos Markdown (type Marp)** : léger, versionnable, aucun ajout de dépendance à la stack (Marp n'est qu'un outil de rendu externe, le fichier source reste `.md`).

## Signatures réelles des fonctions écrites (si elles diffèrent du contrat)

- **`src/config.py`** : _(Inchangé)_ `TESSERACT_LANG="fra"`, `TESSERACT_PSM=6`, `OCR_MIN_WIDTH=1500`, `SEUIL_SFACE=0.30`, `SEUIL_SFACE_REFERENCE=0.363`, `SCORE_FACE_REJECT=0.20`, `DB_PATH`, `VALID_STATUSES`.
- **`src/imaging.py`** : `prepare_card(img) -> np.ndarray | None` (conforme).
- **`src/capture.py`** : `get_frame(source: str) -> np.ndarray | None` (conforme).
- **`src/ocr.py`** : `extract_fields(card_img) -> dict` (conforme).
- **`src/face.py`** : `get_embedding(img)`, `compare(emb_a, emb_b)` (conformes).
- **`src/database.py`** : 4/4 fonctions §6 (conforme).
- **`src/vector_search.py`** : `find_nearest(embedding, k=3)` (conforme).
- **`src/decision.py`** : `decide(fields, card_emb, live_emb, person)` (conforme).
- **`src/pipeline.py`** : `verify(card_source, face_source) -> dict` (conforme §6). Helpers privés `_safe_card`, `_safe_live`.
- **`src/ui.py`** : classe `App(ctk.CTk)` ; méthodes `_capture(attr)`, `on_verify()`, `_run_verify()`, `_show(res)` ; constantes module `ESP32_URL`, `COLORS`.
- **Aucun nouveau fichier Python cette session** — J15 = documentation uniquement.

## Valeurs importantes (seuils, IP de l'ESP32, chemins)

- Racine projet : `~/Documents/DevOps/Projet/id-verif/`
- Python : 3.14.4 (dans `env/`)
- ESP32-CAM : IP `10.135.250.228` (DHCP) — toujours codée en dur dans `ui.py`.
- Taille cible carte : 1000 × 630 px
- Seuils `prepare_card` : tolérance 10 %, taille min 600×375, epsilon 0.01–0.08, rect ≥ 0.55.
- Seuils OCR : `fra`, PSM 6, `OCR_MIN_WIDTH = 1500`.
- Seuils YuNet : `0.6 / 0.3 / 5000`, `margin=0.2`.
- Seuils SFace : `SEUIL_SFACE = 0.30`, `SCORE_FACE_REJECT = 0.20`.
- Modèles : `models/face_detection_yunet_2023mar.onnx`, `models/face_recognition_sface_2021dec.onnx`.
- Variable Qt : `QT_QPA_PLATFORM=xcb`.
- Base SQLite : `data/db/id_verif.db`.
- **Personnes actuellement en base** : 5 lignes — `id=1 FICT-001`, `id=2 FICT-002`, `id=3 FICT-003`, `id=4 SYNTH-005`, `id=5 B8078673`.
- **Format `scores`** : `{score_face: float|None, numero_trouve: bool, ocr_ok: bool, champs_manquants: list[str], date_valide: bool}`.
- **Nouveaux docs J15** : `README.md` (racine), `docs/ARCHITECTURE.md`, `docs/STATE.md` (ce fichier). À venir : `docs/DEMO.md`.

## Notions apprises (pour me réinterroger plus tard)

_(J6 à J12 : inchangés)_

**J13 — Pipeline et Interface** : **Pipeline** = chaîne de montage (sortie d'un module = entrée du suivant) ; **Événement GUI** = action utilisateur déclenchant une callback ; **Thread** = fil d'exécution séparé pour ne pas geler l'UI ; **Thread-safety Tkinter** = passer par `self.after()` pour repasser sur le thread principal ; **`daemon=True`** = thread tué à la fermeture de la fenêtre ; **fichier temporaire** (`tempfile`) = fichier éphémère pour respecter un contrat `str` sans modifier la signature.

**J15 — Documentation de projet** : **README** = vitrine GitHub (seul fichier rendu automatiquement à la racine) ; **doc d'architecture** = plan avant travaux (modules, flux, contrats, choix + alternatives écartées) ; **frontière d'un module** = ce qu'il ne fait PAS, garantit la responsabilité unique ; **lien relatif** = chemin depuis le fichier courant (`../` remonte d'un dossier) ; **diagramme ASCII** = schéma en monospace, lisible partout (terminal, GitHub, éditeur) ; **Marp** = moteur de rendu qui transforme un `.md` en diapositives, sans changer la stack.

## Prochaine étape

- **J1 à J13 + J15 (partie 1) clos** ; **J14 volontairement sauté** (à reprendre plus tard).
- **J15 — reste à faire** :
  1. Produire **`docs/DEMO.md`** (diapos Markdown type Marp) : titre, problème, architecture résumée, scénario de démo 3 cartes (VALIDE / ANOMALIE / VÉRIFICATION_COMPLEMENTAIRE), limites assumées, Q&R jury.
  2. (Optionnel) vérifier les liens relatifs du README et d'ARCHITECTURE une fois DEMO créé.
- **Propositions toujours en attente (aucune appliquée)** :
  - **PROP. 1** — déplacer seuils YuNet vers `config.py`.
  - **PROP. 2** — diff de `_detect_faces` à coller (rappel).
  - **PROP. 3** — `src/` en package Python (`__init__.py` + imports relatifs).
  - **PROP. 4** — code de `config.py` / `database.py` à coller (rappel).
  - **PROP. 5** — `CHROMA_DIR` dans `config.py` quand bonus C réalisé.
  - **PROP. 6** — déplacer `ESP32_URL` de `ui.py` vers `config.py`.
- **Bonus C — différé** : ChromaDB non installé.
