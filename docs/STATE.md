# STATE.md — mis à jour le 17/10, jour 4/15, avec DeepSeek

## Terminé et testé

- Arborescence `id-verif/` créée (`docs/`, `models/`, `data/samples/`, `data/db/`, `firmware/esp32cam/`, `src/`, `tests/`).
- `docs/PROJECT_BRIEF.md` rédigé et relu (stack, arborescence, contrat, vocabulaire figés).
- `docs/STATE.md` initial rédigé, puis mis à jour en fin de J3 et en fin de J4.
- Environnement virtuel `env/` créé : `python3 -m venv env` exécuté, `source env/bin/activate` fonctionne, prompt affiche `(env)`.
- `requirements.txt` créé et installé : `pip install -r requirements.txt` terminé avec succès (opencv-python, numpy, pytesseract, requests, customtkinter).
- Tesseract installé avec la langue française : `sudo apt install tesseract-ocr tesseract-ocr-fra` OK, `tesseract --list-langs` affiche `fra` et `eng`.
- **`src/config.py` testé et fonctionnel** : `python src/config.py` s'exécute, affiche `PROJECT_ROOT`, `SAMPLES_DIR`, `DB_PATH`, et crée les dossiers `data/samples/`, `data/db/`, `models/`.
- **`src/imaging.py` testé et fonctionnel** : chargement d'une image fictive depuis `data/samples/`, affichage de la taille, conversion en niveaux de gris, sauvegarde `*_gray.jpg` vérifiée visuellement.
- **J2 terminé (16/10)** : support ESP32 installé dans l'Arduino IDE, port série `/dev/ttyUSB0` détecté.
- Sketch `firmware/esp32cam/wifi_test/wifi_test.ino` uploadé et fonctionnel.
- ESP32 connectée au Wi-Fi `Klayenet` (2.4 GHz), IP attribuée : `10.135.250.228`, RSSI -32 dBm.
- `ping 10.135.250.228` depuis le PC : réponses OK.
- Fichier `firmware/esp32cam/wifi_test/secrets.h` créé localement (SSID + mot de passe), **non partagé**.
- **J3 terminé (16/10) — ESP32-CAM flux vidéo** :
  - Sketch `firmware/esp32cam/camera_web_server/camera_web_server.ino` rédigé (modèle AI-Thinker, `esp_camera` + `esp_http_server`, `FRAMESIZE_VGA`, qualité JPEG 12, baud 115200, identifiants lus depuis `secrets.h`).
  - **Confirmé par l'étudiant** : moniteur série affiche `Camera OK`, l'IP `10.135.250.228` et `Serveur HTTP demarre`.
  - **Confirmé par l'étudiant** : `http://10.135.250.228/` s'affiche dans le navigateur (page HTML minimale avec lien `/capture`).
  - **Confirmé par l'étudiant** : `http://10.135.250.228/capture` renvoie bien une image JPEG dans le navigateur.
- **`src/capture.py` testé et fonctionnel sur les 3 sources (J4, 17/10)** :
  - **Confirmé par l'étudiant** en fin de J4 : test des trois sources depuis `src/` renvoie, pour chacune :
    - `webcam:0` → `OK : image 640x480, 3 canaux, dtype=uint8`
    - `http://10.135.250.228/capture` (ESP32) → `OK : image 640x480, 3 canaux, dtype=uint8`
    - `file:capture_test.jpg` → `OK : image 640x480, 3 canaux, dtype=uint8`
  - Le contrat §6 (`get_frame(source) -> np.ndarray | None`) est respecté sur les trois cas.
- **J4 terminé (17/10) — cartes fictives style « carte officielle »** :
  - **`src/make_fake_cards.py`** rédigé (outil de test, hors contrat §6) : génère 10 cartes fictives style « carte d'électeur RDC-like », avec bandeau titre, sous-bandeau, mention `DUPLICATA`, zone photo gauche, QR factice droite, champs étendus, bas de carte filiation + délivrance.
  - **Confirmé par l'étudiant** : `python make_fake_cards.py` depuis `src/` affiche `10 visage(s) trouve(s)` puis `OK : carte_fictive_01.jpg` … `OK : carte_fictive_10.jpg`.
  - **Confirmé par l'étudiant** : le rendu visuel est bon, tout fonctionne. Les 10 cartes sont dans `data/samples/`, chacune associée à un visage différent de `data/samples/faces/`.
  - Données 100 % inventées, visages fournis par l'étudiant (fictifs ou consentants). Aucune donnée réelle utilisée.

## En cours ou bloqué

- Rien de bloqué.
- **`src/ocr.py` RETIRÉ DU PÉRIMÈTRE** (décision du 17/10, J4) : rédigé en fin de J3 mais jamais testé, il ne fait pas partie du jour J4. Il ne sera **pas** repris ni testé tant que la feuille de route ne prévoit pas le jour OCR. Le fichier peut être supprimé ou laissé en place sans être compté comme terminé — **il ne doit pas apparaître comme validé**.
- Point d'attention à traiter **plus tard, pas urgent** : les imports `from config import ...` obligent à lancer les scripts depuis `src/`. Une solution propre (package ou ajustement `sys.path`) reste à décider — **PROPOSITION DE CHANGEMENT à venir**, ne rien modifier sans accord.
- `prepare_card` (redressement de carte) pas encore écrit : prévu à une étape ultérieure selon la feuille de route.
- Aucun module du contrat restant (`face`, `database`, `vector_search`, `decision`, `pipeline`, `ui`) n'est commencé.
- **IP de l'ESP32 en DHCP** (`10.135.250.228`) : peut changer au prochain redémarrage ou à l'expiration du bail. Réservation DHCP à envisager le moment venu — **PROPOSITION DE CHANGEMENT à venir**, pas urgent.

## Décisions prises (et pourquoi)

- **16/10** — Garder le brief complet dans `docs/PROJECT_BRIEF.md`. Raison : qu'il voyage avec le code et serve de référence en cas de doute.
- **16/10** — `STATE.md` fait foi entre les sessions. Raison : éviter de tout relire et de rediscuter les choix déjà tranchés.
- **16/10** — Centraliser chemins, seuils et statuts dans `src/config.py`. Raison : un seul endroit à modifier, pas de « chiffre magique » dispersé.
- **16/10** — Convention « renvoyer `None` en cas d'échec » plutôt que laisser planter. Raison : contrat §6 du brief maître.
- **16/10** — Attendre le « ok » explicite de l'étudiant avant de coder chaque fichier. Raison : pédagogie, un pas à la fois, éviter de submerger.
- **16/10** — Identifiants Wi-Fi isolés dans `firmware/esp32cam/wifi_test/secrets.h`, jamais collés dans le chat ni versionnés publiquement. Raison : règle de sécurité du brief (§3.9, données sensibles).
- **16/10** — Ne pas figer d'IP statique dans le sketch pour l'instant. Raison : la réservation DHCP côté routeur est plus propre ; on décidera plus tard selon les contraintes réelles.
- **16/10 (J3)** — Rester en `FRAMESIZE_VGA` (640×480) plutôt que monter en UXGA. Raison : suffisant pour OCR + détection de visage, plus stable, moins de RAM utilisée sur l'ESP32, transfert plus rapide. Un passage à `FRAMESIZE_SVGA` (800×600) ne se fera que si l'OCR lit mal les cartes — **PROPOSITION DE CHANGEMENT** à ce moment-là.
- **16/10 (J3)** — `camera_web_server.ino` fournit une page `/` minimale (lien vers `/capture`) plutôt que le flux MJPEG complet de l'exemple Arduino. Raison : on a seulement besoin de `/capture` pour le pipeline Python ; le flux MJPEG n'apporte rien au prototype et alourdit le sketch. Ajout possible plus tard si besoin — **PROPOSITION DE CHANGEMENT** sinon.
- **16/10 (J3)** — Ne pas compter `src/ocr.py` comme terminé. Raison : l'étudiant ne l'a ni exécuté ni validé ; on ne marque « terminé et testé » que ce qui est confirmé fonctionnel (règle §8 du brief).
- **17/10 (J4)** — **Retirer `src/ocr.py` du périmètre actif.** Raison : l'étudiant ne le testera pas tant que la feuille de route ne prévoit pas le jour OCR. Décision explicite de l'étudiant en début de session J4. Ne pas le compter comme terminé, ne pas le proposer avant le jour prévu.
- **17/10 (J4)** — **PROPOSITION DE CHANGEMENT acceptée par l'étudiant** : refonte du générateur de cartes fictives dans un style « carte officielle » (bandeau titre, sous-bandeau, `DUPLICATA`, zone photo gauche, QR factice droite, champs étendus, bas de carte filiation + délivrance) + insertion d'images de visages depuis `data/samples/faces/`. Raison : rendre les cartes fictives visuellement réalistes pour préparer l'OCR et la détection de visage, **sans** introduire de données réelles ni de dépendance supplémentaire.
- **17/10 (J4)** — **Ne pas reproduire la vraie carte d'électeur RDC** (CENI) montrée par l'étudiant en exemple, ni copier ses champs, ni réutiliser sa photo. Raison : règle §3.9 du brief (aucune vraie donnée personnelle, aucune vraie photo). On s'inspire uniquement du **style** (disposition, bandeaux, QR, filiation).
- **17/10 (J4)** — **Aucune nouvelle dépendance** pour le QR factice : il est dessiné avec `cv2.rectangle` (grille 12×12 de petits carrés tirés au hasard). Raison : rester dans la stack figée (opencv + numpy + random) ; pas de `qrcode`, pas de `pyzbar`.
- **17/10 (J4)** — Les 10 visages de `data/samples/faces/` sont **fournis par l'étudiant**, fictifs ou consentants. Raison : règle §3.9, aucune image de personne réelle non consentante, aucun téléchargement depuis Internet.
- **17/10 (J4)** — Le script `make_fake_cards.py` est un **outil de test**, explicitement **hors contrat §6**. Raison : ce n'est pas un module du pipeline ; il ne doit pas apparaître dans les signatures contractuelles.
- **17/10 (J4)** — Garder le nom de fichier `carte_fictive_NN.jpg`. Raison : ne pas casser ce qui existe déjà et ce qui sera référencé plus tard.
- **17/10 (J4)** — Graine `SEED = 42` conservée pour la reproductibilité. Raison : retrouver les mêmes cartes à chaque exécution, utile pour reproduire un bug plus tard.

## Signatures réelles des fonctions écrites (si elles diffèrent du contrat)

- **`src/config.py`** : aucune fonction du contrat. Contient les constantes `PROJECT_ROOT`, `DATA_DIR`, `SAMPLES_DIR`, `DB_DIR`, `MODELS_DIR`, `DOCS_DIR`, `DB_PATH`, `YUNET_MODEL`, `SFACE_MODEL`, `ESP32_URL`, `HTTP_TIMEOUT_SECONDS`, `CARD_WIDTH`, `CARD_HEIGHT`, `FACE_MATCH_THRESHOLD`, `FACE_AMBIGUITY_MARGIN`, `VECTOR_SEARCH_K`, `STATUS_VALID`, `STATUS_ANOMALY`, `STATUS_NEED_MORE`, et la fonction `ensure_dirs() -> None`.

- **`src/imaging.py`** : fonctions écrites **en plus** du contrat (le contrat ne prévoyait que `prepare_card`) :
  - `load_image(path: str) -> np.ndarray | None`
  - `describe_image(img: np.ndarray) -> tuple[int, int, int]`
  - `to_grayscale(img: np.ndarray) -> np.ndarray`
  - `save_image(img: np.ndarray, path: str) -> bool`
  - `demo_gray(input_path: str) -> None`
  - **`prepare_card(img)` n'est PAS encore écrit** — prévu plus tard selon la feuille de route.

- **`src/capture.py`** : conforme au contrat §6.
  - `get_frame(source: str) -> np.ndarray | None`
  - Helpers privés : `_frame_from_http(url)`, `_frame_from_webcam(index)`, `_frame_from_file(path)`.
  - Sources reconnues : `webcam:N`, `http://...` ou `https://...`, `file:/chemin`.
  - **Testé et confirmé** sur les trois sources (J4, 17/10).

- **`src/ocr.py`** : **RETIRÉ DU PÉRIMÈTRE ACTIF (17/10)**. Ne pas le compter comme terminé, ne pas le tester, ne pas le proposer tant que la feuille de route ne prévoit pas le jour OCR.

- **`src/make_fake_cards.py`** : **outil de test**, hors contrat §6. Écrit et testé le 17/10.
  - `_rand_date(rng, y_min, y_max) -> str`
  - `_rand_number(rng) -> str`
  - `_rand_code(rng) -> str`
  - `_draw_fake_qr(img, x, y, size, rng) -> None`
  - `_paste_face(card, face_path: Path) -> None`
  - `make_one_card(index: int, rng, face_path: Path) -> Path`
  - `main() -> None`
  - Constante `FACES_DIR = SAMPLES_DIR / "faces"`, `SEED = 42`.

- **`firmware/esp32cam/wifi_test/wifi_test.ino`** : sketch Arduino, hors contrat Python. Contient `setup()` et `loop()`. Utilise `WiFi.h` et `secrets.h`.

- **`firmware/esp32cam/camera_web_server/camera_web_server.ino`** : sketch Arduino, hors contrat Python. Contient `setup()`, `loop()`, `start_server()`, `capture_handler()`, `index_handler()`. Utilise `esp_camera.h`, `WiFi.h`, `esp_http_server.h`, `secrets.h`.

## Valeurs importantes (seuils, IP de l'ESP32, chemins)

- Racine projet : `~/id-verif/`
- Base SQLite (prévue) : `~/id-verif/data/db/id_verif.db`
- Images de test (cartes fictives) : `~/id-verif/data/samples/carte_fictive_01.jpg` … `carte_fictive_10.jpg`
- Visages pour les cartes fictives : `~/id-verif/data/samples/faces/` (10 fichiers fournis par l'étudiant)
- Modèles ONNX (à télécharger plus tard) :
  - `~/id-verif/models/face_detection_yunet_2023mar.onnx`
  - `~/id-verif/models/face_recognition_sface_2021dec.onnx`
- ESP32-CAM (valeur actuelle) : SSID `Klayenet`, IP `10.135.250.228` (DHCP — peut changer, à figer plus tard), RSSI -32 dBm
- Endpoints ESP32-CAM confirmés fonctionnels :
  - `http://10.135.250.228/` → page HTML minimale (lien vers `/capture`)
  - `http://10.135.250.228/capture` → une image JPEG
- Réglages caméra (J3) : `FRAMESIZE_VGA` (640×480), `jpeg_quality = 12`, `fb_count = 1`, `xclk_freq_hz = 20000000`
- Délai HTTP : 5 secondes
- Taille cible carte : 1000 × 630 px
- Seuil similarité faciale 1:1 (SFace) : `0.363` — **à calibrer** sur nos propres tests
- Marge d'ambiguïté 1:N : `0.05`
- Voisins en recherche 1:N : `k = 3`
- Statuts (mots exacts) : `VALIDE`, `ANOMALIE`, `VERIFICATION_COMPLEMENTAIRE`
- Langue Tesseract : `fra`
- Baud rate moniteur série ESP32 : `115200`
- Fichier de test capture : `src/capture_test.jpg`
- Graine du générateur de cartes : `SEED = 42` (dans `src/make_fake_cards.py`)
- Zone photo sur la carte fictive : `(zx, zy, zw, zh) = (40, 190, 260, 320)` — **ne pas modifier sans maîtriser `_paste_face`**

## Notions apprises (pour me réinterroger plus tard)

- **Image = matrice numpy** de forme `(hauteur, largeur, canaux)`. Couleur = 3 canaux **BGR** (OpenCV), gris = 1 canal.
- **BGR vs RGB** : OpenCV lit en BGR, à ne pas oublier.
- **Niveaux de gris** : `cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)` remplace 3 valeurs par 1 (luminosité).
- **Tableau numpy** : grille de nombres sur laquelle on fait des calculs vectorisés.
- **Environnement virtuel (venv)** : trousse isolée par projet. `python3 -m venv env` crée, `source env/bin/activate` active (visible au `(env)` dans le prompt), `deactivate` quitte. Vérification : `which python` doit pointer vers `env/bin/python`.
- **`pip`** : installe les paquets dans le venv actif.
- **`requirements.txt`** : liste des dépendances avec versions minimales (`>=`).
- **`pytesseract` vs `tesseract`** : `pytesseract` est un pont Python, `tesseract-ocr` est le binaire, `tesseract-ocr-fra` est le pack de langue française.
- **`Path` (pathlib)** : manipulation moderne des chemins. `__file__` = chemin du fichier courant, `.resolve()` = absolu, `.parent` = dossier parent, `/` = jointure.
- **`config.py`** : centraliser les valeurs pour ne pas avoir de « chiffre magique ».
- **`if __name__ == "__main__":`** : bloc exécuté seulement quand on lance le fichier directement.
- **Convention `None`** : une fonction qui peut échouer signale l'échec par une valeur, pas par un crash.
- **`cv2.imread` / `cv2.imwrite`** : lecture/écriture d'image. `imread` renvoie `None` si échec, `imwrite` renvoie `True`/`False`.
- **`mkdir(parents=True, exist_ok=True)`** : crée un dossier et ses parents sans erreur s'il existe déjà.
- **Microcontrôleur** : petit ordinateur spécialisé, un seul programme en boucle, pas d'OS.
- **Arduino IDE** : environnement qui compile et envoie le code sur la carte via USB.
- **Gestionnaire de cartes** : permet à l'IDE de connaître les cartes ESP32 (sinon il ne les voit pas).
- **Moniteur série** : fenêtre de l'IDE qui affiche les `Serial.print()` de la carte. Le **baud rate** doit être identique des deux côtés (ici 115200). C'est une vitesse de **liaison série**, pas une vitesse de calcul.
- **Station (`WIFI_STA`) vs AP (`WIFI_AP`)** : station = client du réseau ; AP = l'ESP32 crée son propre réseau.
- **DHCP** : le routeur attribue automatiquement une IP ; elle peut changer.
- **RSSI** : force du signal en dBm ; proche de 0 = fort, proche de -90 = faible.
- **GPIO0 à GND** : mode « flash » obligatoire pour uploader sur ESP32-CAM AI-Thinker (à retirer après).
- **SSID** : nom du réseau Wi-Fi. Ici `Klayenet`.
- **`ping`** : envoie un petit paquet à une IP pour vérifier qu'elle répond.
- **Serveur HTTP embarqué** : petit « guichet » dans la puce. On frappe une URL, il regarde le chemin et renvoie la bonne chose.
- **Endpoint `/` vs `/capture`** : `/` renvoie du HTML (page avec lien), `/capture` renvoie **une seule image JPEG brute**.
- **Flux MJPEG** : enchaînement continu d'images JPEG, utilisé par une page de streaming. Non utilisé dans notre version minimale.
- **`esp_camera_fb_get()` / `esp_camera_fb_return()`** : emprunter un buffer d'image à la caméra, puis le rendre. Oublier le `return` épuise la mémoire après quelques requêtes.
- **`FRAMESIZE_VGA`** : 640×480 px. `FRAMESIZE_SVGA` = 800×600, `FRAMESIZE_UXGA` = 1600×1200. Plus grand = plus lourd, plus long à transférer, plus de RAM.
- **`jpeg_quality`** : 0 = meilleure qualité (fichier plus gros), 63 = pire qualité.
- **`Brownout detector was triggered`** : la tension d'alimentation s'est écroulée (pic de courant de la caméra ou du Wi-Fi). Cause n°1 : câble USB trop fin, port USB faible, alim 5 V insuffisante.
- **`requests.get(...).content`** : renvoie les octets bruts de la réponse HTTP. HTTP ne connaît pas la notion d'image ; le `Content-Type` n'est qu'une étiquette.
- **`np.frombuffer` + `cv2.imdecode`** : transformer des octets JPEG en matrice BGR utilisable par OpenCV. Le transport (HTTP) et le décodage (JPEG) sont deux étapes séparées.
- **`cap.release()`** : libérer la webcam. Ressource exclusive : sans `release`, la caméra reste verrouillée pour les autres applications ou pour la prochaine frame.
- **`raise_for_status()`** : transforme un code HTTP 4xx/5xx en exception Python, qu'on attrape pour renvoyer `None` au lieu de planter.
- **OCR (Optical Character Recognition)** : programme qui lit du texte dans une image. Tesseract = moteur, `pytesseract` = pont Python, `fra` = pack de langue française. (Notion présentée mais **code non testé** — retiré du périmètre actif.)
- **Abstraction de source (J4)** : une seule fonction `get_frame(source)` sert trois sources différentes (`webcam:N`, `http://...`, `file:...`). Raison : un seul point d'entrée pour le pipeline, pas trois codes dispersés.
- **`cv2.rectangle`** : trace un rectangle. Dernier paramètre `-1` = rempli, `>0` = épaisseur du trait en pixels.
- **`cv2.putText`** : écrit du texte. `FONT_HERSHEY_SIMPLEX` = police standard OpenCV. `cv2.LINE_AA` = anti-alias (bords lisses, meilleur pour l'OCR).
- **`np.full((h, w, 3), 240, dtype=np.uint8)`** : crée une image BGR uniforme (ici presque blanche). `uint8` = entier 0-255, format standard d'image.
- **Rognage avant resize (J4)** : pour coller une photo dans une zone de ratio fixe sans la déformer, on **rogne** d'abord au bon ratio (centré), puis on redimensionne. Redimensionner directement étire l'image.
- **Écriture par tranche numpy** : `card[zy:zy+zh, zx:zx+zw] = face` remplace un bloc de pixels sans boucle. C'est la force du calcul vectorisé.
- **Graine (`SEED`)** : fige le hasard. Même graine + même code = mêmes cartes à chaque exécution. Change la graine pour obtenir de nouvelles cartes.
- **QR factice** : motif dessiné avec `cv2.rectangle`, non scannable volontairement. Sert uniquement à la ressemblance visuelle. Ne pas confondre avec un vrai QR qui encoderait une donnée.

## Prochaine étape

- **J1, J2, J3 et J4 sont clos** :
  - J1 : environnement, arborescence, `config.py`, `imaging.py` testés.
  - J2 : ESP32 connectée au Wi-Fi, sketch `wifi_test` fonctionnel.
  - J3 : ESP32-CAM joignable, page `/` visible, `/capture` renvoie une JPEG.
  - J4 : `capture.py` testé sur les 3 sources (`webcam:0`, `http://...`, `file:...`) ; 10 cartes fictives style « carte officielle » générées avec visages, validées visuellement.
- **À faire en tout début de prochaine session** :
  - Fournir la **section J5** de la feuille de route **avant tout nouveau code** (règle : ne pas coder les modules des jours suivants sans instruction explicite).
  - Ne **pas** proposer `src/ocr.py` : il est retiré du périmètre actif jusqu'au jour prévu par la feuille de route.
- **Points à intégrer le moment venu (aucun n'est urgent)** :
  - décider comment gérer proprement les imports depuis `src/` (package vs `sys.path`) — **PROPOSITION DE CHANGEMENT à venir**, à valider avant modification ;
  - figer l'IP de l'ESP32 via réservation DHCP côté routeur — **PROPOSITION DE CHANGEMENT à venir** si nécessaire ;
  - éventuellement ajouter un flux MJPEG à la page `/` si un besoin de debug visuel apparaît — **PROPOSITION DE CHANGEMENT** à ce moment-là ;
  - vérifier que `data/samples/faces/` contient bien 10 visages stables (ne pas les supprimer/déplacer) pour que `make_fake_cards.py` reste reproductible avec `SEED = 42`.
