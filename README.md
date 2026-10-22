# 🪪 ID-Vérif — Prototype de vérification d'identité

Petit prototype pédagogique de **vérification d'identité en 3 contrôles** :

1. La carte est-elle **lisible et cohérente** ? (OCR + contrôles simples)
2. Ses données existent-elles dans une **base de référence locale** ?
3. Le visage du porteur correspond-il à la **photo de la carte** ? (comparaison 1:1)

Tout tourne sur un **PC sans GPU** (CPU uniquement), avec une **ESP32-CAM** qui capture les images par Wi-Fi et envoie au PC pour le traitement lourd en Python.

> ⚠️ **Limite assumée** : sans accès à la base de l'organisme émetteur, on vérifie la **cohérence** avec une base locale — pas l'**authenticité absolue** du document. Ce projet est un prototype pédagogique, **pas** un système de production.

---

## 📑 Sommaire

- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Configuration](#️-configuration)
- [Structure du projet](#-structure-du-projet)
- [Tests](#-tests)
- [Limites](#️-limites)
- [Démonstration](#-démonstration)
- [Auteur](#-auteur)
- [Remerciements](#-remerciements)

---

## ✨ Fonctionnalités

- 📷 **Capture d'image** : ESP32-CAM (HTTP `/capture`), webcam locale, ou fichier image.
- 🔍 **OCR** : extraction des champs (nom, postnom, prénom, date de naissance, numéro) via Tesseract (langue `fra`).
- 🧠 **Empreinte faciale** : détection **YuNet** + reconnaissance **SFace** (modèles ONNX, exécutés sur CPU).
- 💾 **Base locale SQLite** : enrôlement des personnes de référence, journal des vérifications.
- 🔎 **Recherche vectorielle** : comparaison par force brute (`numpy`) pour la vérification **1:N**.
- ⚖️ **Décision** : 3 statuts — `VALIDE`, `ANOMALIE`, `VERIFICATION_COMPLEMENTAIRE`.
- 🖥️ **Interface graphique** : `customtkinter` avec statut coloré et zone de log.

---

## 🏗️ Architecture

Vue synthétique (le détail complet est dans **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**) :

```

ESP32-CAM ──Wi-Fi──▶ PC (Python)
├─ capture.py (frame BGR)
├─ imaging.py (carte redressée 1000×630)
├─ ocr.py (champs texte)
├─ face.py (empreinte faciale 128-D)
├─ database.py (SQLite : persons + verifications)
├─ vector_search (1:N numpy)
└─ decision.py (statut final)

```

> 📘 `docs/ARCHITECTURE.md` contient : le **schéma détaillé** du pipeline, le **flux de données** entre modules, les **contrats d'interface** (§6 du brief), les **choix techniques** (pourquoi YuNet/SFace, pourquoi SQLite, pourquoi pas de GPU) et les **pistes d'amélioration** (ChromaDB, anti-spoofing).

---

## 🔧 Prérequis

- **Python 3.10+** (testé avec **Python 3.14.4**)
- **Tesseract OCR** avec pack de langue **`fra`**
- **Ubuntu** (ou dérivé Debian) — testé sous Ubuntu
- **~8 Go de RAM** (CPU uniquement, **pas de GPU requis**)
- (Optionnel) **ESP32-CAM AI-Thinker** pour la capture sans fil

### Installation de Tesseract

```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-fra
tesseract --version
tesseract --list-langs   # doit inclure "fra"
```

---

## 🚀 Installation

### 1. Cloner le dépôt

```bash
git clone <URL_DU_DEPOT> id-verif
cd id-verif
```

### 2. Créer et activer un environnement virtuel

```bash
python3 -m venv env
source env/bin/activate
```

### 3. Installer les dépendances Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> ℹ️ Aucun framework lourd (TensorFlow, PyTorch, dlib) — tout tient sur CPU.

### 4. Télécharger les modèles ONNX

Créer `models/` et y placer les 2 fichiers :

| Fichier attendu                       | Source                                                                                                   |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `face_detection_yunet_2023mar.onnx`   | [OpenCV Model Zoo — YuNet](https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet)   |
| `face_recognition_sface_2021dec.onnx` | [OpenCV Model Zoo — SFace](https://github.com/opencv/opencv_zoo/tree/main/models/face_recognition_sface) |

```bash
mkdir -p models
# télécharger les 2 fichiers puis :
ls models/
# face_detection_yunet_2023mar.onnx
# face_recognition_sface_2021dec.onnx
```

### 5. Initialiser la base de données

```bash
python -c "from src.database import init_db; init_db()"
```

Crée `data/db/id_verif.db` (tables `persons` et `verifications`).

### 6. (Optionnel) ESP32-CAM

Flasher `firmware/esp32cam/` sur la carte, noter son IP et la renseigner dans `src/config.py`. Sans ESP32-CAM, utiliser **webcam** (`webcam:0`) ou **image** (`file:data/samples/...`) : la démo fonctionne sans matériel embarqué.

---

## 🎮 Utilisation

### CLI — vérifier une carte

```bash
python -c "
from src.pipeline import verify
print(verify('file:data/samples/carte_fictive_01.jpg', 'webcam:0'))
"
```

**Sortie attendue** :

```python---

## Auteur

Projet réalisé dans le cadre d'un apprentissage de l'ingénierie informatique (15 jours, J1 → J15). Étudiant francophone, débutant sur Arduino/ESP32, OpenCV, IA embarquée et bases vectorielles.
{
  'status': 'VALIDE',
  'reasons': ['numero_trouve', 'visage_correspond'],
  'scores': {'score_face': 0.79, 'numero_trouve': True, 'ocr_ok': True, ...}
}
```

### CLI — enrôler une personne (idempotent)

```bash
python test/test_enroll_from_card.py
```

Relançable sans `IntegrityError` : vérifie `get_person_by_number` avant `add_person`.

### Interface graphique

```bash
export QT_QPA_PLATFORM=xcb     # contournement Qt/Wayland (Ubuntu 22+)
python src/ui.py
```

Boutons : 🎥 **Capturer carte**, 🤳 **Capturer porteur**, ✅ **Vérifier**, 📋 **Log des raisons**.

---

## ⚙️ Configuration

Tous les seuils et chemins sont centralisés dans **`src/config.py`** :

| Constante               | Valeur par défaut     | Rôle                                                                                     |
| ----------------------- | --------------------- | ---------------------------------------------------------------------------------------- |
| `TESSERACT_LANG`        | `"fra"`               | Langue OCR                                                                               |
| `TESSERACT_PSM`         | `6`                   | Mode de segmentation Tesseract                                                           |
| `OCR_MIN_WIDTH`         | `1500`                | Largeur minimale pour l'OCR                                                              |
| `SEUIL_SFACE`           | `0.30`                | Seuil d'acceptation faciale                                                              |
| `SEUIL_SFACE_REFERENCE` | `0.363`               | Seuil de référence (à calibrer)                                                          |
| `SCORE_FACE_REJECT`     | `0.20`                | Score plancher → rejet                                                                   |
| `DB_PATH`               | `data/db/id_verif.db` | Chemin SQLite                                                                            |
| `ESP32_URL`             | `http://<ip>/capture` | URL de l'ESP32-CAM — ⚠️ encore dans `ui.py`, migration vers `config.py` prévue (PROP. 6) |

> ⚠️ **Calibration en cours** : `SEUIL_SFACE` / `SEUIL_SFACE_REFERENCE` sont à consolider sur un jeu plus large.

---

## 📁 Structure du projet

```
id-verif/
├── main.py
├── README.md                # ← vous êtes ici
├── docs/
│   ├── PROJECT_BRIEF.md
│   ├── STATE.md
│   ├── ARCHITECTURE.md
│   └── DEMO.md
├── models/                  # .onnx (non versionnés)
├── data/
│   ├── samples/             # photos de test fictives
│   └── db/                  # base SQLite (non versionnée)
├── firmware/esp32cam/       # code Arduino
├── src/
│   ├── config.py
│   ├── capture.py
│   ├── imaging.py
│   ├── ocr.py
│   ├── face.py
│   ├── database.py
│   ├── vector_search.py
│   ├── decision.py
│   ├── pipeline.py
│   └── ui.py
└── test/
    ├── test_enroll_from_card.py
    └── ...
```

---

## 🧪 Tests

```bash
# Détection de visage
python test/test_face_detect.py

# Scores SFace sur des paires
python test/test_sface_scores.py

# Pipeline complet en CLI
python -c "from src.pipeline import verify; print(verify('file:data/samples/carte_fictive_01.jpg', 'file:data/samples/porteur_01.jpg'))"
```

**État** : J1 → J13 confirmés (voir `docs/STATE.md`). J14 reporté.

---

## ⚠️ Limites

- ❌ **Pas d'authenticité absolue** : on vérifie la cohérence avec une base locale, pas l'émission du document par un organisme.
- ❌ **Pas d'anti-spoofing** : une photo de photo peut tromper le système (hors scope).
- ⚠️ **Seuil facial fragile** : calibré sur peu d'échantillons ; marge observée ~0.79 sur le visage test.
- ⚠️ **Jeux de données réduits** : à enrichir pour une évaluation statistique.
- 🔒 **Données sensibles** : jamais de vraies cartes / vraies photos. **Cartes fictives** et **personnes consentantes** uniquement.

---

## 🎤 Démonstration

Scénario pas-à-pas (type diapositives Markdown) : **[docs/DEMO.md](docs/DEMO.md)** — utile pour soutenance / présentation.

---

## Stack Vital

- [OpenCV](https://opencv.org/) — YuNet & SFace
- [Tesseract](https://github.com/tesseract-ocr/tesseract) — OCR
- [customtkinter](https://github.com/TomSchimansky/CustomTkinter) — UI moderne
- [SQLite](https://www.sqlite.org/) — persistance légère

````

---

## 🔍 Explication bloc par bloc

- **Titre + pitch + `> ⚠️ Limite`** : un visiteur doit savoir en 5 secondes *ce que fait le projet* et *ce qu'il ne fait pas*. La limite assumée est exigée par ton brief (§2) et rassure sur ton honnêteté technique.
- **Sommaire avec ancres** : GitHub génère automatiquement les liens `#slug-du-titre`. Les emoji dans les titres n'empêchent pas les ancres (GitHub les ignore pour le slug).
- **Fonctionnalités** : liste à puces courte — c'est ce qu'un recruteur/enseignant lit en 1er.
- **Architecture (résumé + lien)** : un mini-schéma ASCII suffit dans le README ; le détail complet est **délégué** à `docs/ARCHITECTURE.md` (c'est ce que tu m'as demandé).
- **Prérequis / Installation** : 6 étapes numérotées, chacune avec la commande exacte. Vérification Tesseract incluse (erreur n°1 habituelle).
- **Utilisation** : 3 cas d'usage (verify CLI, enroll CLI, UI). On insiste sur `QT_QPA_PLATFORM=xcb` car c'est le contournement validé (STATE.md).
- **Configuration** : table exhaustive des constantes réelles lues depuis `STATE.md`. On signale honnêtement que `ESP32_URL` est encore dans `ui.py` (PROP. 6 non appliquée).
- **Structure** : `tree` en bloc code — GitHub le rend monospace proprement.
- **Tests** : commandes copiables, état (J1→J13 validés, J14 reporté) honnête.
- **Limites** : déjà préparées, formelles, alignées avec le brief. **Anti-spoofing** mentionné pour ne pas survendre.
- **Démo / Auteur / Remerciements** : derniers blocs classiques GitHub.

---

## ▶️ Commande pour visualiser

```bash
# Si tu as `code` (VS Code)
code README.md

# Ou directement en HTML dans le navigateur
pandoc README.md -o /tmp/readme.html && xdg-open /tmp/readme.html

# Ou plus simple : pousser sur GitHub et ouvrir la page du dépôt
````

---
