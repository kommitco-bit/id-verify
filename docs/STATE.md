# STATE.md — mis à jour le 17/10, jour 6, avec DeepSeek

## Terminé et testé

- **Environnement** : venv Python **3.14.4** confirmé et retenu. Le problème Qt/Wayland est contourné avec `QT_QPA_PLATFORM=xcb`.
- **Arborescence** : `~/Documents/DevOps/Projet/id-verif/` confirmée.
- **J2, J3, J4** : ESP32-CAM (`/` et `/capture`) fonctionnel, `src/capture.py` (3 sources) fonctionnel, 10 cartes fictives générées.
- **J5** : `imaging.py` (flou, resize, seuil, Otsu, Canny) fonctionnel, testé sur 13/13 cartes.
- **J6 (17/10) — Redresser la carte (1/2)** :
  - **Notions vues** : contours (Canny), enveloppe convexe (`convexHull`), approximation de polygone (`approxPolyDP`), 4 coins, transformation de perspective (`getPerspectiveTransform`, `warpPerspective`), ratio d'image.
  - **`src/imaging.py` mis à jour** : ajout de `prepare_card(img) -> np.ndarray | None` (contrat §6 respecté).
  - **Logique de `prepare_card`** :
    1. Si l'image a déjà le bon ratio (1000/630 ± 10%) et une taille ≥ 600×375 (ex: carte scannée ou déjà recadrée), un simple `resize` est fait.
    2. Sinon, détection auto des 4 coins (V2) + transformation de perspective.
    3. Si la détection échoue, renvoie `None` (pas de recadrage "au hasard").
  - **Outils pédagogiques hors contrat §6 créés et testés** : `test/demo_quad.py` (visualisation des contours/coins), `test/demo_perspective.py` (redressement à partir d'un cadre simulé), `test/test_prepare_card.py` (validation sur plusieurs images).
  - **Confirmé par l'étudiant** : `prepare_card` fonctionne sur les cartes fictives (1000×630) et sur les cartes scannées (Belge, RDC 1000×630). Le pipeline peut passer à la suite.

## En cours ou bloqué

- **`src/ocr.py` reste RETIRÉ DU PÉRIMÈTRE ACTIF** : ne pas le compter comme terminé, ne pas le tester, ne pas le proposer avant le jour OCR prévu.
- **Version 1 de `prepare_card` (cadre-guide)** : la V1 (affichage d'un cadre à l'écran pour que l'utilisateur aligne la carte) n'est **pas encore câblée**. Elle est reportée à l'étape `ui.py` (customtkinter), car il faut un affichage réel pour que l'utilisateur interagisse.
- **Limites de la V2** : les photos téléphones très petites (ex: `test5.jpeg` en 352×567) sont rejetées par `prepare_card` car le côté minimum de la carte est < 150 px (OCR impossible). C'est une limite assumée, documentée, qui sera compensée par la V1 dans l'UI.
- **Imports `src/`** : toujours gérés par `sys.path.insert` dans les tests. Une solution propre (package) est en attente (**PROPOSITION DE CHANGEMENT à venir**).
- **Nettoyage `data/samples/`** : les variantes `_gray`, `_blur`, etc., générées en J5 polluent le dossier. À filtrer ou nettoyer avant les prochains modules.
- **IP de l'ESP32** : toujours en DHCP (`10.135.250.228`), réservation à envisager (**PROPOSITION DE CHANGEMENT à venir**).

## Décisions prises (et pourquoi)

- **17/10 (J6)** — Python 3.14.4 conservé. Raison : choisi par l'étudiant, fonctionne avec le contournement Qt.
- **17/10 (J6)** — Commencer par la V2 (détection auto) au lieu de la V1 (cadre-guide). Raison : demande de l'étudiant, plus rapide à tester en mode script.
- **17/10 (J6)** — **Stratégie `prepare_card`** : Détecter d'abord si l'image est déjà au format carte (ratio ~1.587 ±10%). Si oui, simple `resize`. Si non, détection V2 + perspective. Si échec, renvoyer `None`. Raison : les cartes scannées (1000×630) n'ont pas de bord externe à détecter, la V2 échouait sur elles. Le `resize` direct est plus rapide et sans risque.
- **17/10 (J6)** — **Pas de V1 en secours dans `prepare_card`**. Raison : la V1 suppose que l'utilisateur voit un cadre. Sans UI, recadrer une zone centrale au hasard produirait une carte fausse. La V1 sera codée dans `ui.py`.
- **17/10 (J6)** — Création de `test/demo_quad.py`, `test/demo_perspective.py` et `test/test_prepare_card.py`. Raison : pédagogie visuelle (voir les coins, voir la perspective) et validation automatisée. Hors contrat §6.

## Signatures réelles des fonctions écrites (si elles diffèrent du contrat)

- **`src/config.py`** : inchangé.
- **`src/imaging.py`** :
  - J1/J5 : `load_image`, `describe_image`, `to_grayscale`, `save_image`, `apply_blur`, `resize_image`, `apply_threshold`, `apply_otsu`, `detect_edges` + démos.
  - **J6 (nouveau)** :
    - `prepare_card(img: np.ndarray) -> np.ndarray | None` (Contrat §6 respecté).
    - Helpers privés : `_order_corners(pts) -> np.ndarray`, `_quad_min_side(corners) -> float`, `_detect_card_quad(img) -> np.ndarray | None`.
- **`src/capture.py`** : inchangé.
- **`test/demo_quad.py`** (pédagogique) : `order_corners`, `debug_edges`, `find_card_quad`, `draw_quad`, `main`.
- **`test/demo_perspective.py`** (pédagogique) : `order_corners`, `warp_card`, `central_frame`, `main`.
- **`test/test_prepare_card.py`** (test) : script de validation en boucle sur plusieurs images.

## Valeurs importantes (seuils, IP de l'ESP32, chemins)

- Racine projet : `~/Documents/DevOps/Projet/id-verif/`
- Python : 3.14.4 (dans `env/`)
- ESP32-CAM : IP `10.135.250.228` (DHCP)
- Taille cible carte : 1000 × 630 px (Ratio ≈ 1.587)
- **Seuils `prepare_card` (V2)** :
  - Tolérance ratio "déjà carte" : 10% (`abs(ratio_img - 1.587) / 1.587 < 0.10`)
  - Taille min "déjà carte" : `w >= 600` et `h >= 375`
  - Filtre bruit (contour) : `< 2%` de l'aire de l'image
  - Epsilon `approxPolyDP` : `0.01` à `0.08`
  - Seuil de rectangularité : `0.55`
  - Seuil d'aire finale du quad : `5%` de l'image
  - Côté minimum du quad : `150 px` (en dessous, l'OCR ne lira rien)
- Seuil similarité faciale (SFace) : `0.363` (à calibrer)
- Variable d'environnement Qt : `QT_QPA_PLATFORM=xcb`

## Notions apprises (pour me réinterroger plus tard)

- **J6 — Contours et Polygones** : `cv2.findContours` trouve les lignes de séparation. `cv2.convexHull` enveloppe le contour pour gommer les bosses (bruit). `cv2.approxPolyDP` réduit un contour à un polygone (un epsilon petit garde les détails, un grand simplifie).
- **J6 — Rectangularité** : Aire du quadrilatère / Aire de son rectangle englobant. Un rectangle parfait = 1.0. Sert à rejeter les faux quads (ex: un triangle très allongé).
- **J6 — Ordre des coins** : `order_corners` sert à s'assurer que les points sont dans l'ordre TL (Haut-Gauche), TR (Haut-Droite), BR (Bas-Droite), BL (Bas-Gauche). Sans ça, la transformation de perspective peut retourner l'image en miroir ou à l'envers.
- **J6 — Transformation de perspective** : `cv2.getPerspectiveTransform` calcule une matrice 3x3 pour "aplatir" une zone déformée (4 points quelconques) vers un rectangle parfait. `cv2.warpPerspective` applique ce calcul à tous les pixels de l'image.
- **J6 — Ratio d'image** : `Largeur / Hauteur`. Permet de reconnaître si une image a déjà la forme d'une carte, évitant ainsi une détection de contours inutile (et souvent vouée à l'échec sur une image sans bordure).
- **J6 — INTER_AREA vs INTER_LINEAR** : `INTER_AREA` est meilleur pour réduire une image (moyenne les pixels), évitant l'effet d'escalier. `INTER_LINEAR` est préféré pour agrandir (interpolation).

## Prochaine étape

- **J1 à J6 sont clos.**
- **À faire en tout début de prochaine session** :
  - Fournir la **section J7** de la feuille de route avant tout nouveau code.
  - Ne **pas** proposer `src/ocr.py`.
  - Choisir la suite : soit attaquer **`database.py`** (création des tables, `add_person`, `get_person_by_number`), soit commencer **`ui.py`** pour câbler la V1 (`prepare_card` avec cadre-guide interactif).
- **Points à intégrer le moment venu (aucun urgent)** :
  - Réservation DHCP pour l'ESP32 ;
  - Nettoyage de `data/samples/` ou filtrage du glob dans les tests ;
  - Harmoniser le nom `demo_step.py` (étudiant) vs `demo_steps.py` (session précédente) ;
  - Décider de la gestion propre des imports (package vs `sys.path`).
