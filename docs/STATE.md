# STATE.md — mis à jour le 17/10, jour 5/15, avec DeepSeek

## Terminé et testé

- Arborescence `id-verif/` créée (`docs/`, `models/`, `data/samples/`, `data/db/`, `firmware/esp32cam/`, `src/`, `tests/`).
- `docs/PROJECT_BRIEF.md` rédigé et relu (stack, arborescence, contrat, vocabulaire figés).
- `docs/STATE.md` initial rédigé, puis mis à jour en fin de J3, J4 et J5.
- Environnement virtuel `env/` créé et fonctionnel. **ATTENTION** : le venv tourne actuellement sur Python 3.14, ce qui a causé des problèmes d'affichage OpenCV (Qt/wayland) en fin de J5. Contourné par `QT_QPA_PLATFORM=xcb` puis résolu après recréation avec une version Python plus stable. **Préciser la version retenue dans la prochaine session.**
- `requirements.txt` créé et installé : `pip install -r requirements.txt` terminé avec succès (opencv-python, numpy, pytesseract, requests, customtkinter).
- Tesseract installé avec la langue française : `sudo apt install tesseract-ocr tesseract-ocr-fra` OK, `tesseract --list-langs` affiche `fra` et `eng`.
- **`src/config.py` testé et fonctionnel** : affiche `PROJECT_ROOT`, `SAMPLES_DIR`, `DB_PATH`, crée les dossiers `data/samples/`, `data/db/`, `models/`.
- **`src/imaging.py` testé et fonctionnel** sur les opérations de base J1 + J5 :
  - `load_image`, `describe_image`, `to_grayscale`, `save_image`, `demo_gray` (J1).
  - **J5** : `apply_blur`, `resize_image`, `apply_threshold`, `apply_otsu`, `detect_edges` + démos `demo_blur`, `demo_resize`, `demo_threshold`, `demo_canny`.
  - **Confirmé par l'étudiant** : chaque opération s'exécute, produit le fichier attendu, et l'effet visuel est cohérent (flou progressif, resize non déformé, seuil fixe vs Otsu, contours Canny).
  - Le contrat §6 (`prepare_card`) **n'est toujours PAS écrit** — prévu plus tard selon feuille de route.
- **J2 terminé (16/10)** : support ESP32 installé dans l'Arduino IDE, port `/dev/ttyUSB0` détecté. Sketch `wifi_test.ino` uploadé et fonctionnel. ESP32 connectée au Wi-Fi `Klayenet`, IP `10.135.250.228`, RSSI -32 dBm. `ping` OK. `secrets.h` créé localement, non partagé.
- **J3 terminé (16/10)** : `camera_web_server.ino` opérationnel (`Camera OK`, `Serveur HTTP demarre`), page `/` visible, `/capture` renvoie une JPEG. `FRAMESIZE_VGA`, qualité 12, baud 115200.
- **`src/capture.py` testé et fonctionnel (J4)** sur les 3 sources : `webcam:0`, `http://10.135.250.228/capture`, `file:...`. Contrat §6 respecté (`get_frame(source) -> np.ndarray | None`).
- **J4 terminé (17/10)** : `src/make_fake_cards.py` rédigé, 10 cartes fictives style « carte officielle » générées dans `data/samples/`, chacune avec un visage différent de `data/samples/faces/`. Validé visuellement.
- **J5 terminé (17/10) — traitement d'images (1/2)** :
  - Notions vues : redimensionnement, niveaux de gris, flou gaussien, seuillage (fixe + Otsu), détection de contours (Canny avec hystérésis), luminosité (mentionnée, pas encore codée).
  - **`src/imaging.py` complété** avec `apply_blur`, `resize_image`, `apply_threshold`, `apply_otsu`, `detect_edges` + démos dédiées. **Confirmé par l'étudiant** : tout s'exécute et le rendu visuel est compris.
  - **`src/demo_steps.py`** (nouveau, outil hors contrat §6) : affiche en une fenêtre une grille 2×3 (Original | Gris | Flou / Seuil 127 | Otsu | Canny). **Confirmé par l'étudiant** : la fenêtre s'ouvre et reste jusqu'à une touche pressée. Note : le nom réel du fichier côté étudiant est `demo_step.py` (singulier) — à harmoniser plus tard, sans urgence.
  - **`tests/test_imaging_all_cards.py`** (nouveau, hors contrat §6) : non-régression des fonctions `imaging.py` sur toutes les cartes de `data/samples/`. **Confirmé par l'étudiant** : `Bilan : 13/13 cartes OK` (le glob a attrapé aussi les variantes `_gray`, `_blur`, `_canny_*`, `_otsu`, `_resize_*`, `_thr_*` générées pendant les démos — c'est acceptable, aucun échec).
  - **Livrable J5 validé** : l'étudiant sait expliquer avec ses mots ce que fait chaque étape.

## En cours ou bloqué

- Rien de bloqué à la fin de J5.
- **`src/ocr.py` reste RETIRÉ DU PÉRIMÈTRE ACTIF** (décision du 17/10, J4) : ne pas le compter comme terminé, ne pas le tester, ne pas le proposer avant le jour OCR prévu par la feuille de route.
- Point d'attention à traiter **plus tard, pas urgent** : les imports `from config import ...` obligent à lancer les scripts depuis `src/` (ou à ajuster `sys.path`, comme dans le test J5). Une solution propre (package) reste à décider — **PROPOSITION DE CHANGEMENT à venir**, ne rien modifier sans accord.
- **Version Python du venv à clarifier** : problèmes Qt/wayland rencontrés avec Python 3.14 en fin de J5. Le contournement `QT_QPA_PLATFORM=xcb` a fonctionné, puis une recréation du venv a été faite. **Noter la version effectivement retenue** au début de J6 pour ne pas perdre de temps.
- **Nettoyage de `data/samples/`** : les variantes `_gray`, `_blur`, `_canny_*`, `_otsu`, `_resize_*`, `_thr_*` générées pendant les démos polluent le dossier. Le test les ramasse comme cartes. À nettoyer **plus tard** (ou à filtrer dans le glob) — **pas urgent**, mais à traiter avant que d'autres modules n'itèrent sur `data/samples/`.
- `prepare_card` (redressement de carte) toujours pas écrit.
- Modules du contrat restants non commencés : `face`, `database`, `vector_search`, `decision`, `pipeline`, `ui`.
- **IP de l'ESP32 en DHCP** (`10.135.250.228`) : peut changer. Réservation DHCP à envisager — **PROPOSITION DE CHANGEMENT à venir**, pas urgent.

## Décisions prises (et pourquoi)

- **16/10** — Garder le brief complet dans `docs/PROJECT_BRIEF.md`. Raison : référence en cas de doute.
- **16/10** — `STATE.md` fait foi entre les sessions.
- **16/10** — Centraliser chemins, seuils et statuts dans `src/config.py`. Raison : pas de « chiffre magique » dispersé.
- **16/10** — Convention « renvoyer `None` en cas d'échec » plutôt que laisser planter (contrat §6).
- **16/10** — Attendre le « ok » explicite de l'étudiant avant de coder chaque fichier. Raison : pédagogie, un pas à la fois.
- **16/10** — Identifiants Wi-Fi isolés dans `firmware/esp32cam/wifi_test/secrets.h`, jamais collés dans le chat ni versionnés. Raison : sécurité (§3.9).
- **16/10** — Ne pas figer d'IP statique dans le sketch pour l'instant. Raison : réservation DHCP côté routeur plus propre.
- **16/10 (J3)** — Rester en `FRAMESIZE_VGA` (640×480). Raison : suffisant, plus stable, moins de RAM.
- **16/10 (J3)** — Page `/` minimale plutôt que flux MJPEG complet. Raison : on n'a besoin que de `/capture`.
- **16/10 (J3)** — Ne pas compter `src/ocr.py` comme terminé (non testé par l'étudiant).
- **17/10 (J4)** — Retirer `src/ocr.py` du périmètre actif. Décision explicite de l'étudiant.
- **17/10 (J4)** — **PROPOSITION DE CHANGEMENT acceptée** : refonte du générateur de cartes fictives dans un style « carte officielle ». Raison : préparer OCR + détection de visage sans donnée réelle.
- **17/10 (J4)** — Ne pas reproduire la vraie carte CENI. Raison : §3.9, aucune vraie donnée.
- **17/10 (J4)** — Aucune nouvelle dépendance pour le QR factice (`cv2.rectangle` uniquement).
- **17/10 (J4)** — Visages fournis par l'étudiant, fictifs ou consentants.
- **17/10 (J4)** — `make_fake_cards.py` = outil de test, hors contrat §6.
- **17/10 (J4)** — Garder le nom `carte_fictive_NN.jpg`.
- **17/10 (J4)** — Graine `SEED = 42` conservée pour reproductibilité.
- **17/10 (J5)** — Ajouter `resize_image`, `apply_blur`, `apply_threshold`, `apply_otsu`, `detect_edges` à `imaging.py` plutôt que créer un second fichier image. Raison : `imaging.py` est **le** module d'image du contrat ; on le complète sans le casser.
- **17/10 (J5)** — `apply_threshold` et `apply_otsu` convertissent automatiquement en gris si on leur passe une image couleur. Raison : éviter un piège `cv2.error: scn == 1` côté étudiant.
- **17/10 (J5)** — `detect_edges` floute **automatiquement** (kernel 5×5) avant Canny. Raison : sans flou, Canny ramasse tout le bruit JPEG ; ce n'est pas pédagogique de laisser l'étudiant se piéger.
- **17/10 (J5)** — `resize_image` choisit `INTER_AREA` pour réduire, `INTER_LINEAR` pour agrandir. Raison : c'est la pratique recommandée, et ça évite à l'étudiant de mémoriser des règles sans comprendre.
- **17/10 (J5)** — `demo_steps.py` et `tests/test_imaging_all_cards.py` sont **hors contrat §6**. Raison : ce sont des outils de démo/test, pas des modules du pipeline.
- **17/10 (J5)** — Grille 2×3 dans `demo_steps.py`, images réduites à 500×315 pour tenir à l'écran sur un 8 Go RAM. Raison : lisibilité et stabilité d'affichage.
- **17/10 (J5)** — Ajout de `QT_QPA_PLATFORM=xcb` (et recréation du venv) pour résoudre le blocage `imshow` sous Wayland/GNOME. Raison : sans ça, `cv2.imshow` n'affiche rien malgré un programme correct.

## Signatures réelles des fonctions écrites (si elles diffèrent du contrat)

- **`src/config.py`** : aucune fonction du contrat. Constantes : `PROJECT_ROOT`, `DATA_DIR`, `SAMPLES_DIR`, `DB_DIR`, `MODELS_DIR`, `DOCS_DIR`, `DB_PATH`, `YUNET_MODEL`, `SFACE_MODEL`, `ESP32_URL`, `HTTP_TIMEOUT_SECONDS`, `CARD_WIDTH`, `CARD_HEIGHT`, `FACE_MATCH_THRESHOLD`, `FACE_AMBIGUITY_MARGIN`, `VECTOR_SEARCH_K`, `STATUS_VALID`, `STATUS_ANOMALY`, `STATUS_NEED_MORE`, fonction `ensure_dirs() -> None`.

- **`src/imaging.py`** :
  - J1 : `load_image(path: str) -> np.ndarray | None`, `describe_image(img) -> tuple[int, int, int]`, `to_grayscale(img) -> np.ndarray`, `save_image(img, path) -> bool`, `demo_gray(input_path: str) -> None`.
  - **J5** : `apply_blur(img, kernel_size: int = 5) -> np.ndarray | None`, `resize_image(img, width: int, height: int) -> np.ndarray | None`, `apply_threshold(gray, threshold: int = 127) -> np.ndarray | None`, `apply_otsu(gray) -> np.ndarray | None`, `detect_edges(img, low: int = 50, high: int = 150) -> np.ndarray | None`, + démos `demo_blur`, `demo_resize`, `demo_threshold`, `demo_canny`.
  - **`prepare_card` toujours PAS écrit** — prévu plus tard.

- **`src/capture.py`** : conforme au contrat §6. `get_frame(source: str) -> np.ndarray | None`. Helpers privés `_frame_from_http`, `_frame_from_webcam`, `_frame_from_file`.

- **`src/ocr.py`** : **RETIRÉ DU PÉRIMÈTRE ACTIF (17/10)**.

- **`src/make_fake_cards.py`** : outil de test, hors contrat §6. `_rand_date`, `_rand_number`, `_rand_code`, `_draw_fake_qr`, `_paste_face`, `make_one_card`, `main`. Constante `SEED = 42`, `FACES_DIR = SAMPLES_DIR / "faces"`.

- **`src/demo_steps.py`** : outil pédagogique, hors contrat §6. `to_bgr3(img) -> np.ndarray`, `label(img, text) -> np.ndarray`, `make_grid(input_path: str) -> np.ndarray | None`, `main() -> None`. Note : le fichier s'appelle `demo_step.py` (singulier) chez l'étudiant — à harmoniser plus tard.

- **`tests/test_imaging_all_cards.py`** : outil de test, hors contrat §6. `run_on_one(path: Path) -> bool`, `main() -> None`. Utilise `sys.path.insert` pour importer `imaging` et `config` depuis `src/`.

- **`firmware/esp32cam/wifi_test/wifi_test.ino`** : sketch Arduino, hors contrat Python. `setup()`, `loop()`, `WiFi.h`, `secrets.h`.

- **`firmware/esp32cam/camera_web_server/camera_web_server.ino`** : sketch Arduino, hors contrat Python. `setup()`, `loop()`, `start_server()`, `capture_handler()`, `index_handler()`, `esp_camera.h`, `WiFi.h`, `esp_http_server.h`, `secrets.h`.

## Valeurs importantes (seuils, IP de l'ESP32, chemins)

- Racine projet : `~/id-verif/` (ou `~/Documents/DevOps/Projet/id-verif/` selon l'emplacement réel).
- Base SQLite (prévue) : `data/db/id_verif.db`
- Cartes fictives : `data/samples/carte_fictive_01.jpg` … `carte_fictive_10.jpg`
- Visages : `data/samples/faces/` (10 fichiers fournis par l'étudiant)
- Modèles ONNX (à télécharger plus tard) :
  - `models/face_detection_yunet_2023mar.onnx`
  - `models/face_recognition_sface_2021dec.onnx`
- ESP32-CAM (valeur actuelle) : SSID `Klayenet`, IP `10.135.250.228` (DHCP — peut changer), RSSI -32 dBm
- Endpoints ESP32-CAM confirmés : `http://10.135.250.228/` (HTML) et `http://10.135.250.228/capture` (JPEG)
- Réglages caméra : `FRAMESIZE_VGA` (640×480), `jpeg_quality = 12`, `fb_count = 1`, `xclk_freq_hz = 20000000`
- Délai HTTP : 5 secondes
- Taille cible carte : 1000 × 630 px
- Seuil similarité faciale 1:1 (SFace) : `0.363` — à calibrer
- Marge d'ambiguïté 1:N : `0.05`
- Voisins en recherche 1:N : `k = 3`
- Statuts : `VALIDE`, `ANOMALIE`, `VERIFICATION_COMPLEMENTAIRE`
- Langue Tesseract : `fra`
- Baud rate ESP32 : `115200`
- Fichier de test capture : `src/capture_test.jpg`
- Graine générateur cartes : `SEED = 42` (dans `src/make_fake_cards.py`)
- Zone photo carte : `(zx, zy, zw, zh) = (40, 190, 260, 320)` — ne pas modifier sans maîtriser `_paste_face`
- Flou gaussien : `kernel_size` impair, défaut 5
- Canny : `low = 50`, `high = 150` (défaut), flou 5×5 préalable systématique
- Seuil fixe : 127 (défaut démo)
- Resize démo : 500×315 (moitié de 1000×630, ratio préservé)
- Variable d'environnement Qt : `QT_QPA_PLATFORM=xcb` (si `imshow` bloqué sous Wayland)

## Notions apprises (pour me réinterroger plus tard)

- **Image = matrice numpy** de forme `(hauteur, largeur, canaux)`. BGR (OpenCV), gris = 1 canal.
- **BGR vs RGB**, `cv2.cvtColor`, `cv2.COLOR_BGR2GRAY`.
- **Tableau numpy** : grille de nombres, calculs vectorisés.
- **venv**, **pip**, **requirements.txt**, **pytesseract vs tesseract**, **`Path` (pathlib)**, **`if __name__ == "__main__"`**, **convention `None`**, **`cv2.imread`/`cv2.imwrite`**, **`mkdir(parents=True, exist_ok=True)`**.
- **Microcontrôleur**, **Arduino IDE**, **moniteur série**, **baud rate**, **`WIFI_STA` vs `WIFI_AP`**, **DHCP**, **RSSI**, **GPIO0/GND**, **SSID**, **`ping`**, **serveur HTTP embarqué**, **endpoints `/` vs `/capture`**, **flux MJPEG**, **`esp_camera_fb_get`/`esp_camera_fb_return`**, **`FRAMESIZE_VGA/SVGA/UXGA`**, **`jpeg_quality`**, **brownout**, **`requests.get(...).content`**, **`np.frombuffer` + `cv2.imdecode`**, **`cap.release()`**, **`raise_for_status()`**.
- **OCR (notion seulement, code non testé)**.
- **Abstraction de source** : `get_frame(source)` unique pour 3 sources.
- **`cv2.rectangle`**, **`cv2.putText`**, **`np.full`**, **rognage avant resize**, **écriture par tranche numpy**, **graine (SEED)**, **QR factice**.
- **J5 — flou gaussien** : chaque pixel devient une moyenne pondérée de ses voisins (courbe en cloche). Noyau impair obligatoire (pixel central). Plus `kernel_size` est grand, plus c'est flou. Utile avant Canny/OCR pour supprimer le bruit.
- **J5 — redimensionnement** : changer le nombre de pixels. `cv2.resize` attend `(largeur, hauteur)`, alors que `img.shape[:2]` renvoie `(hauteur, largeur)`. `INTER_AREA` pour réduire (moyenne de blocs), `INTER_LINEAR` pour agrandir (interpolation). **Respecter le ratio** (ex. 1000×630 → 500×315) sinon image écrasée.
- **J5 — seuillage** : pixel < seuil → 0 (noir), ≥ seuil → 255 (blanc). Image **binaire** 1 canal. Seuil fixe (127) = arbitraire ; **Otsu** = calcule le meilleur seuil pour l'image en séparant l'histogramme en deux groupes. Il faut **convertir en gris avant** de seuiller (threshold exige 1 valeur par pixel).
- **J5 — Canny** : détection de contours. Enchaîne flou → gradient → non-maxima → **hystérésis** (`low`, `high`). Pixel ≥ `high` = bord fort gardé toujours ; < `low` = bruit jeté ; entre `low` et `high` = bord faible gardé **seulement s'il est relié** à un bord fort. Règle empirique : `high ≈ 2× à 3× low` (défaut 50/150). Toujours `gray → blur → Canny`. Canny renvoie une image **binaire 1 canal** (contours blancs sur fond noir).
- **J5 — grille d'affichage** : `np.hstack` (colonne) et `np.vstack` (ligne) exigent des formes compatibles. Pour empiler du gris avec du couleur : `cv2.COLOR_GRAY2BGR` (astuce d'affichage, pas un vrai retour en couleur).
- **J5 — `cv2.waitKey(0)`** : attend indéfiniment une touche. `cv2.waitKey(1000)` = 1 seconde. Sans `waitKey`, la fenêtre ne s'affiche pas / se ferme immédiatement.
- **J5 — `QT_QPA_PLATFORM=xcb`** : force Qt à utiliser X11 plutôt que Wayland. Contourne les blocages `imshow` sous GNOME/Wayland. Complément : `sudo apt install libxcb-cursor0`.
- **J5 — version Python** : Python 3.14 (trop récent) peut casser les wheels OpenCV (Qt/affichage). Python 3.12/3.13 = plus sûr pour OpenCV à ce jour.

## Prochaine étape

- **J1 à J5 sont clos** :
  - J1 : environnement, arborescence, `config.py`, `imaging.py` de base testés.
  - J2 : ESP32 Wi-Fi, `wifi_test` fonctionnel.
  - J3 : ESP32-CAM joignable, `/` et `/capture` OK.
  - J4 : `capture.py` sur 3 sources, 10 cartes fictives générées et validées.
  - J5 : `imaging.py` complété (flou, resize, seuil, Otsu, Canny), `demo_steps.py` (grille 2×3) fonctionnel, `tests/test_imaging_all_cards.py` passe `13/13`.
- **À faire en tout début de prochaine session** :
  - Fournir la **section J6** de la feuille de route **avant tout nouveau code**.
  - Ne **pas** proposer `src/ocr.py` (retiré du périmètre actif).
  - Confirmer la **version Python du venv** effectivement retenue.
- **Points à intégrer le moment venu (aucun urgent)** :
  - décider comment gérer proprement les imports depuis `src/` (package vs `sys.path`) — **PROPOSITION DE CHANGEMENT à venir** ;
  - figer l'IP de l'ESP32 via réservation DHCP — **PROPOSITION DE CHANGEMENT à venir** ;
  - nettoyer `data/samples/` des variantes `_gray`, `_blur`, `_canny_*`, `_otsu`, `_resize_*`, `_thr_*` générées par les démos, ou filtrer le glob du test pour ne cibler que `carte_fictive_NN.jpg` — **à faire avant que d'autres modules n'itèrent sur ce dossier** ;
  - harmoniser le nom `demo_step.py` vs `demo_steps.py` — **sans urgence** ;
  - éventuellement ajouter un flux MJPEG sur `/` — **PROPOSITION DE CHANGEMENT** si besoin ;
  - conserver `data/samples/faces/` (10 visages stables) pour la reproductibilité de `make_fake_cards.py` avec `SEED = 42`.
