# STATE.md — mis à jour le 18/10, jour 7, avec DeepSeek

<!-- À vérifier : si tu es encore le 17/10, ajuste la date en tête -->

## Terminé et testé

- **Environnement** : venv Python **3.14.4** confirmé. Contournement Qt/Wayland toujours en place (`QT_QPA_PLATFORM=xcb`).
- **Arborescence** : `~/Documents/DevOps/Projet/id-verif/` confirmée.
- **J2, J3, J4** : ESP32-CAM (`/` et `/capture`) fonctionnel, `src/capture.py` (3 sources) fonctionnel.
- **J5** : `imaging.py` (flou, resize, seuil, Otsu, Canny) fonctionnel.
- **J6 (17/10)** : `prepare_card(img) -> np.ndarray | None` fonctionnel (détection V2 + transformation de perspective + resize direct si déjà au bon format). Testé et confirmé par l'étudiant.
- **J7 (18/10) — OCR** :
  - **Tesseract 5.5.0** installé et vérifié sur Ubuntu ; pack **`fra`** présent (`tesseract --list-langs` confirme).
  - **`pytesseract` + `Pillow`** installés dans le venv. Test d'import : `pytesseract.get_tesseract_version() == 5.5.0`. Test lecture de texte français synthétique (`'Nom : KABILA'`) : OK.
  - **`src/ocr.py` V1** créé, conforme au contrat §6 :
    - `_preprocess(card_img)` : gris → upscale `INTER_CUBIC` si largeur < 1500 → binarisation Otsu.
    - `extract_raw_text(card_img) -> str` : appelle Tesseract avec `lang='fra'` et `--psm 6`.
  - **`test/test_ocr_raw.py`** créé : boucle sur les cartes, filtre par regex `carte_fictive_\d{2}\.jpg` (`re.fullmatch`) pour ignorer les variantes `_gray`, `_blur`, `_otsu`, `_thr_*`, `_canny_*`, `_resize_*`, `_1000x630`.
  - **`src/ocr.py` V2** : ajout de `extract_fields(card_img) -> dict` (contrat §6 respecté : clés `nom`, `postnom`, `prenom`, `date_naissance`, `numero`, `raw_text`). Regex ancrées sur les étiquettes de la carte (`Nom :`, `Postnom/Prenom :`, `Date / Lieu de naissance :`, `NI./N.I./NL:`).
  - **Bug trouvé et corrigé** dans `_RE_NUM` : `[I.L]` matchait le `.` au lieu du `I` de `N.I.` → remplacé par `\.?[IL1]\.?`. Carte 02 renvoyait `numero = None`, maintenant `'D3219824'`.
  - **Résultat confirmé par l'étudiant** : les **4 cartes fictives disponibles** extraient les **5 champs correctement** (20/20 champs lus).

## En cours ou bloqué

- **Jeu de données J7 incomplet** : seulement **4 cartes** (`carte_fictive_01..04.jpg`) disponibles dans `data/samples/`. Les cartes `05` à `10` sont absentes (soit supprimées, soit jamais générées). Le livrable J7 demande un tableau sur 10 cartes → **limite assumée et documentée** ci-dessous. À regénérer via le script J3/J4 quand pertinent.
- **`src/imaging.py`** : V1 du cadre-guide (`prepare_card` interactif) toujours **non câblée**. Prévue pour l'étape `ui.py` (customtkinter), car elle nécessite un affichage réel.
- **Imports `src/`** : toujours gérés par `sys.path.insert` dans les tests. Solution propre (package Python) toujours **en attente** (PROPOSITION DE CHANGEMENT à venir).
- **`data/samples/`** : les variantes `_gray`, `_blur`, `_otsu`, `_thr_*`, `_canny_*`, `_resize_*`, `_1000x630` ont été **retirées** par l'étudiant pendant J7 (il ne reste que les 4 cartes propres). Le filtre regex dans `test_ocr_raw.py` reste en place comme garde-fou futur.
- **IP de l'ESP32** : toujours en DHCP (`10.135.250.228`), réservation à envisager (PROPOSITION à venir).

## Décisions prises (et pourquoi)

- **18/10 (J7)** — **`TESSERACT_PSM = 6`**. Raison : mode « bloc de texte uniforme », adapté à une carte (texte dense et homogène). À revoir si un champ spécifique (ex. zone photo) est mal isolé.
- **18/10 (J7)** — **`OCR_MIN_WIDTH = 1500`**. Raison : en dessous, Tesseract lit des caractères de trop petite taille et confond `I/1/L`, `0/O`, `4/9`. Testé sur `_resize_500x315` : illisible. 1500 px de large est un compromis coût CPU / qualité sur AMD 3020e.
- **18/10 (J7)** — **Prétraitement `gris + upscale + Otsu`**. Raison : Tesseract préfère nettement le noir-sur-blanc binaire ; nos tests préliminaires (thr_127, thr_200, otsu en J5) ont montré qu'Otsu généralise mieux sans réglage manuel.
- **18/10 (J7)** — **Regex ancrées sur les étiquettes**, pas sur des valeurs « n'importe où ». Raison : le texte brut est pollué par les armoiries, zones photo, bordures et filigranes. S'ancrer sur `Nom :`, `NI.`, etc. élimine le bruit sans filtrage lourd.
- **18/10 (J7)** — **Deux groupes dans `_RE_NUM`** `([A-Z])\s*(\d{6,8})` puis concaténation. Raison : le format est `LETTRE + 6-8 chiffres`. Deux groupes + concaténation = `B8078673` propre, sans espace parasite.
- **18/10 (J7)** — **Filtre regex `carte_fictive_\d{2}\.jpg`** dans le test plutôt que `glob("carte_fictive_*")`. Raison : robuste aux futures variantes ; documenté dans le code.

## Signatures réelles des fonctions écrites (si elles diffèrent du contrat)

- **`src/config.py`** : toujours inchangé (contient `TESSERACT_LANG`, `TESSERACT_PSM`, `OCR_MIN_WIDTH` si présents, sinon valeurs par défaut utilisées via `getattr`).
- **`src/imaging.py`** : inchangé depuis J6.
  - `prepare_card(img) -> np.ndarray | None` (conforme contrat §6).
  - Helpers privés : `_order_corners`, `_quad_min_side`, `_detect_card_quad`.
- **`src/capture.py`** : inchangé.
- **`src/ocr.py`** (nouveau J7, conforme contrat §6) :
  - `_preprocess(card_img: np.ndarray) -> np.ndarray` _(privée)_
  - `extract_raw_text(card_img: np.ndarray) -> str`
  - `extract_fields(card_img: np.ndarray) -> dict`
  - Regex compilées module-level : `_RE_NOM`, `_RE_PP`, `_RE_DATE`, `_RE_NUM`.
- **`test/test_ocr_raw.py`** (nouveau J7, pédagogique) : `main()`.
- **`test/demo_quad.py`, `test/demo_perspective.py`, `test/test_prepare_card.py`** : inchangés (J6).

## Valeurs importantes (seuils, IP de l'ESP32, chemins)

- Racine projet : `~/Documents/DevOps/Projet/id-verif/`
- Python : 3.14.4 (dans `env/`)
- ESP32-CAM : IP `10.135.250.228` (DHCP)
- Taille cible carte : 1000 × 630 px (ratio ≈ 1.587)
- **Seuils `prepare_card` (J6)** : tolérance ratio 10 %, taille min « déjà carte » 600×375, epsilon `approxPolyDP` 0.01–0.08, rectangularité ≥ 0.55, aire quad ≥ 5 %, côté min quad 150 px.
- **Seuils OCR (J7)** : `TESSERACT_LANG = "fra"`, `TESSERACT_PSM = 6`, `OCR_MIN_WIDTH = 1500`.
- Seuil similarité faciale (SFace) : `0.363` (à calibrer en J9+).
- Variable d'environnement Qt : `QT_QPA_PLATFORM=xcb`.
- **Tesseract** : version **5.5.0**, packs `fra` + `eng` + `osd` présents.

## Notions apprises (pour me réinterroger plus tard)

- **J6 — Contours, polygones, perspective, ratio d'image** : voir session précédente (conservées).
- **J7 — OCR** : transforme des pixels en caractères. Tesseract segmente en lignes → mots → caractères et compare à des formes apprises. Il préfère le **noir-sur-blanc binaire** à une photo brute.
- **J7 — `pytesseract` vs `Tesseract`** : `pytesseract` est une **télécommande Python** ; le moteur `tesseract` (binaire système) doit être installé séparément avec ses packs de langue.
- **J7 — PSM (Page Segmentation Mode)** : `6` = « suppose un bloc de texte uniforme » ; adapté aux cartes. D'autres modes ciblent une ligne unique (`7`), un seul mot (`8`), etc.
- **J7 — Prétraitement OCR** : `gris → upscale INTER_CUBIC → Otsu`. L'upscale avant binarisation est **volontaire** : si on binarise d'abord puis qu'on agrandit, on crée des marches d'escalier ; agrandir d'abord garde des contours propres.
- **J7 — Expressions régulières (regex)** : `\s*` = espaces optionnels ; `[A-Za-zÀ-ÿ]` = classe de lettres (accents inclus) ; `\.?` = point littéral optionnel ; `:=` (walrus) = assigne et teste en une expression.
- **J7 — Piège classe de caractères** : `[I.L]` = « I ou . ou L » (le `.` est un caractère littéral **dans** une classe). Écrire `\.?[IL1]\.?` pour dire « point optionnel, puis I/L/1, puis point optionnel ».
- **J7 — Ancrage sur étiquette** : chercher `Nom\s*:\s*(.+)` plutôt que de chercher un nom inconnu. L'étiquette élimine 99 % du bruit visuel (armoiries, filigranes).
- **J7 — `re.fullmatch` vs `glob`** : `fullmatch` exige que **tout** le nom corresponde ; parfait pour écarter `carte_fictive_01_gray.jpg` quand on veut `carte_fictive_\d{2}\.jpg`.
- **J7 — Confusion de caractères Tesseract** : `I ↔ L ↔ 1`, `0 ↔ O`, `4 ↔ 9`, accents perdus sur flou. Contournable partiellement en tolérant les classes (`[IL1]`).
- **J7 — Deux causes d'erreur identifiées (livrable)** :
  1. **Confusion de caractères** par Tesseract (fix regex possible).
  2. **Bruit visuel de la carte** (armoiries, bordures, photo) qui s'invite dans le texte brut (fix par ancrage sur étiquettes).

### Livrable J7 — Tableau du taux de lecture (état honnête)

Sur **4 cartes fictives propres disponibles** (les seules restantes, `05..10` absentes) :

| Champ            | C01           | C02                       | C03           | C04           | Taux    |
| ---------------- | ------------- | ------------------------- | ------------- | ------------- | ------- |
| `nom`            | ✅ MARTIN     | ✅ KABILA                 | ✅ MUKENDI    | ✅ ROBERT     | **4/4** |
| `postnom`        | ✅ DUPONT     | ✅ MARTIN                 | ✅ DUPONT     | ✅ ROBERT     | **4/4** |
| `prenom`         | ✅ Esther     | ✅ Alice                  | ✅ Chantal    | ✅ Joseph     | **4/4** |
| `date_naissance` | ✅ 08/03/1966 | ✅ 03/09/1975             | ✅ 26/07/2002 | ✅ 16/04/1977 | **4/4** |
| `numero`         | ✅ B8078673   | ✅ D3219824 _(après fix)_ | ✅ D5476257   | ✅ G6639317   | **4/4** |

**Total : 20/20 champs lus sur 4 cartes.** ⚠️ Échantillon plus petit que les 10 demandés → à regénérer pour solidifier.

## Prochaine étape

- **J1 à J7 clos.**
- **À faire en début de prochaine session** :
  - Fournir la **section J8** de la feuille de route avant tout nouveau code.
  - Choisir : **`database.py`** (J8 probable — `init_db`, `add_person`, `get_person_by_number`, `log_verification`) **ou** avancer d'abord sur **`ui.py`** pour câbler la V1 `prepare_card` (cadre-guide).
- **Points à intégrer le moment venu (aucun urgent)** :
  - **Regénérer `carte_fictive_05..10`** avec le script J3/J4 pour solidifier le tableau J7 (échantillon 10/10).
  - Réservation DHCP pour l'ESP32.
  - Gestion propre des imports `src/` (package vs `sys.path`).
  - Harmoniser `demo_step.py` / `demo_steps.py`.
  - Calibrer le seuil SFace (0.363 par défaut) en J9+.
