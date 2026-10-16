# STATE.md — mis à jour le 16/10, jour 1/15, avec DeepSeek

## Terminé et testé

- Arborescence `id-verif/` créée (`docs/`, `models/`, `data/samples/`, `data/db/`, `firmware/esp32cam/`, `src/`, `tests/`).
- `docs/PROJECT_BRIEF.md` rédigé et relu (stack, arborescence, contrat, vocabulaire figés).
- `docs/STATE.md` initial rédigé.
- Environnement virtuel `env/` créé : `python3 -m venv env` exécuté, `source env/bin/activate` fonctionne, prompt affiche `(env)`.
- `requirements.txt` créé et installé : `pip install -r requirements.txt` terminé avec succès (opencv-python, numpy, pytesseract, requests, customtkinter).
- Tesseract installé avec la langue française : `sudo apt install tesseract-ocr tesseract-ocr-fra` OK, `tesseract --list-langs` affiche `fra` et `eng`.
- **`src/config.py` testé et fonctionnel** : `python src/config.py` s'exécute, affiche `PROJECT_ROOT`, `SAMPLES_DIR`, `DB_PATH`, et crée les dossiers `data/samples/`, `data/db/`, `models/`.
- **`src/imaging.py` testé et fonctionnel** : chargement d'une image fictive depuis `data/samples/`, affichage de la taille, conversion en niveaux de gris, sauvegarde `*_gray.jpg` vérifiée visuellement (image bien en noir et blanc).

## En cours ou bloqué

- Rien de bloqué.
- Point d'attention à traiter **plus tard, pas urgent** : les imports `from config import ...` obligent à lancer les scripts depuis `src/`. Une solution propre (package ou ajustement `sys.path`) reste à décider — **PROPOSITION DE CHANGEMENT à venir**, ne rien modifier sans accord.
- `prepare_card` (redressement de carte) pas encore écrit : prévu à une étape ultérieure selon la feuille de route.
- Aucun module du contrat (`capture`, `ocr`, `face`, `database`, `vector_search`, `decision`, `pipeline`, `ui`) n'est encore commencé.

## Décisions prises (et pourquoi)

- **16/10** — Garder le brief complet dans `docs/PROJECT_BRIEF.md`. Raison : qu'il voyage avec le code et serve de référence en cas de doute.
- **16/10** — `STATE.md` fait foi entre les sessions. Raison : éviter de tout relire et de rediscuter les choix déjà tranchés.
- **16/10** — Centraliser chemins, seuils et statuts dans `src/config.py`. Raison : un seul endroit à modifier, pas de « chiffre magique » dispersé.
- **16/10** — Convention « renvoyer `None` en cas d'échec » plutôt que laisser planter. Raison : contrat §6 du brief maître.
- **16/10** — Attendre le « ok » explicite de l'étudiant avant de coder chaque fichier. Raison : pédagogie, un pas à la fois, éviter de submerger.

## Signatures réelles des fonctions écrites (si elles diffèrent du contrat)

- **`src/config.py`** : aucune fonction du contrat. Contient les constantes `PROJECT_ROOT`, `DATA_DIR`, `SAMPLES_DIR`, `DB_DIR`, `MODELS_DIR`, `DOCS_DIR`, `DB_PATH`, `YUNET_MODEL`, `SFACE_MODEL`, `ESP32_URL`, `HTTP_TIMEOUT_SECONDS`, `CARD_WIDTH`, `CARD_HEIGHT`, `FACE_MATCH_THRESHOLD`, `FACE_AMBIGUITY_MARGIN`, `VECTOR_SEARCH_K`, `STATUS_VALID`, `STATUS_ANOMALY`, `STATUS_NEED_MORE`, et la fonction `ensure_dirs() -> None`.

- **`src/imaging.py`** : fonctions écrites **en plus** du contrat (le contrat ne prévoyait que `prepare_card`) :
  - `load_image(path: str) -> np.ndarray | None`
  - `describe_image(img: np.ndarray) -> tuple[int, int, int]`
  - `to_grayscale(img: np.ndarray) -> np.ndarray`
  - `save_image(img: np.ndarray, path: str) -> bool`
  - `demo_gray(input_path: str) -> None`
  - **`prepare_card(img)` n'est PAS encore écrit** — prévu plus tard selon la feuille de route.

## Valeurs importantes (seuils, IP de l'ESP32, chemins)

- Racine projet : `~/id-verif/`
- Base SQLite (prévue) : `~/id-verif/data/db/id_verif.db`
- Images de test : `~/id-verif/data/samples/`
- Modèles ONNX (à télécharger plus tard) :
  - `~/id-verif/models/face_detection_yunet_2023mar.onnx`
  - `~/id-verif/models/face_recognition_sface_2021dec.onnx`
- ESP32-CAM (valeur par défaut, à ajuster quand l'IP réelle sera connue) : `http://192.168.1.50/capture`
- Délai HTTP : 5 secondes
- Taille cible carte : 1000 × 630 px
- Seuil similarité faciale 1:1 (SFace) : `0.363` — **à calibrer** sur nos propres tests
- Marge d'ambiguïté 1:N : `0.05`
- Voisins en recherche 1:N : `k = 3`
- Statuts (mots exacts) : `VALIDE`, `ANOMALIE`, `VERIFICATION_COMPLEMENTAIRE`
- Langue Tesseract : `fra`

## Notions apprises (pour me réinterroger plus tard)

- **Image = matrice numpy** de forme `(hauteur, largeur, canaux)`. Couleur = 3 canaux **BGR** (OpenCV), gris = 1 canal.
- **BGR vs RGB** : OpenCV lit en BGR, à ne pas oublier.
- **Niveaux de gris** : `cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)` remplace 3 valeurs par 1 (luminosité).
- **Tableau numpy** : grille de nombres sur laquelle on fait des calculs vectorisés.
- **Environnement virtuel (venv)** : trousse isolée par projet. `python3 -m venv env` crée, `source env/bin/activate` active (visible au `(env)` dans le prompt), `deactivate` quitte. Vérification : `which python` doit pointer vers `env/bin/python`.
- **`pip`** : installe les paquets dans le venv actif.
- **`requirements.txt`** : liste des dépendances avec versions minimales (`>=`).
- **`pytesseract` vs `tesseract`** : `pytesseract` est un pont Python, `tesseract-ocr` est le binaire, `tesseract-ocr-fra` est le pack de langue française.
- **`Path` (pathlib)** : manipulation moderne des chemins. `__file__` = chemin du fichier courant, `.resolve()` = absolu, `.parent` = dossier parent.
- **`config.py`** : centraliser les valeurs pour ne pas avoir de « chiffre magique ».
- **`if __name__ == "__main__":`** : bloc exécuté seulement quand on lance le fichier directement.
- **Convention `None`** : une fonction qui peut échouer signale l'échec par une valeur, pas par un crash.
- **`cv2.imread` / `cv2.imwrite`** : lecture/écriture d'image. `imread` renvoie `None` si échec, `imwrite` renvoie `True`/`False`.
- **`mkdir(parents=True, exist_ok=True)`** : crée un dossier et ses parents sans erreur s'il existe déjà.

## Prochaine étape

- J1 est **clos** : environnement installé, arborescence créée, `config.py` et `imaging.py` testés et fonctionnels.
- **Passer à J2** : fournir la section J2 de la feuille de route avant tout code (règle : ne pas coder les modules des jours suivants sans instruction explicite).
- Point à intégrer le moment venu : décider comment gérer proprement les imports depuis `src/` (package vs `sys.path`) — **PROPOSITION DE CHANGEMENT à venir**, à valider par l'étudiant avant modification.
