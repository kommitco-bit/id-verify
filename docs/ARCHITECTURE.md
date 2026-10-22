# 🏗️ Architecture — ID-Vérif

Vue d'ensemble du prototype : modules, flux de données, contrats d'interface, choix techniques et pistes d'évolution. Le _comment installer / lancer_ est dans le [README](../README.md).

## 1. Schéma général

┌──────────────┐ HTTP GET /capture
│ ESP32-CAM │──────────────────┐
└──────────────┘ │
▼
┌──────────────┐ ┌──────────────────────────┐
│ webcam / img │──▶│ capture.get_frame(src) │──▶ frame BGR (np.ndarray)
└──────────────┘ └──────────────────────────┘
│
▼
┌──────────────────────────┐
│ imaging.prepare_card(img)│──▶ carte 1000×630 | None
└──────────────────────────┘
│
▼
┌──────────────────────────┐
│ ocr.extract_fields(card) │──▶ {nom, …, numero, raw_text}
└──────────────────────────┘
│
▼
┌──────────────────────────┐
│ face.get_embedding(img) │──▶ emb float32 (128,) | None
└──────────────────────────┘
│
▼
┌──────────────────────────┐
│ database.get_person_by_number(num) │──▶ dict | None
└──────────────────────────┘
│
▼
┌──────────────────────────┐
│ decision.decide(...) │──▶ {status, reasons, scores}
└──────────────────────────┘
│
▼
┌──────────────────────────┐
│ database.log_verification│
└──────────────────────────┘

Le tout est orchestré par `pipeline.verify(card_source, face_source)` (voir §4).

## 2. Modules — rôle et frontière

| Module             | Rôle                                           | Frontière (ce qu'il ne fait PAS)       |
| ------------------ | ---------------------------------------------- | -------------------------------------- |
| `capture.py`       | Récupérer une frame (ESP32, webcam, fichier)   | Ne fait aucun prétraitement            |
| `imaging.py`       | Détecter et redresser la carte (1000×630)      | Ne lit aucun texte                     |
| `ocr.py`           | Extraire les champs texte (Tesseract `fra`)    | Ne valide pas la cohérence métier      |
| `face.py`          | Détecter un visage (YuNet) + empreinte (SFace) | Ne décide pas d'un seuil d'acceptation |
| `database.py`      | Persister personnes + vérifications (SQLite)   | N'applique aucune règle de décision    |
| `vector_search.py` | Recherche 1:N par similarité cosinus (numpy)   | Ne logge rien                          |
| `decision.py`      | Combiner indices → statut                      | N'accède ni à la base ni aux fichiers  |
| `pipeline.py`      | Orchestrer les modules dans l'ordre            | N'affiche rien (aucune dépendance UI)  |
| `ui.py`            | Interface customtkinter                        | Ne contient aucune logique métier      |
| `config.py`        | Seuils + chemins                               | Aucun code exécuté à l'import          |

## 3. Contrats d'interface (figés §6)

Signatures immuables sans accord explicite. Échecs → `None`, jamais d'exception propagée.

- `capture.get_frame(source: str) -> np.ndarray | None`
- `imaging.prepare_card(img: np.ndarray) -> np.ndarray | None`
- `ocr.extract_fields(card_img: np.ndarray) -> dict` (clés : `nom, postnom, prenom, date_naissance, numero, raw_text`)
- `face.get_embedding(img: np.ndarray) -> np.ndarray | None` (float32, 128 valeurs)
- `face.compare(a, b) -> float`
- `database.init_db() -> None`
- `database.add_person(fields: dict, embedding) -> int`
- `database.get_person_by_number(numero: str) -> dict | None`
- `database.log_verification(person_id, status: str, scores: dict) -> None`
- `vector_search.find_nearest(embedding, k=3) -> list[tuple[int, float]]`
- `decision.decide(fields, card_emb, live_emb, person) -> dict`
- `pipeline.verify(card_source, face_source) -> dict`

**Conventions** : images = `np.ndarray` BGR (OpenCV) ; empreintes = `float32` ; statuts ∈ `{VALIDE, ANOMALIE, VERIFICATION_COMPLEMENTAIRE}`.

## 4. Flux d'une vérification (`pipeline.verify`)

1. `capture.get_frame(card_source)` → frame carte (ou `None` → `ANOMALIE`).
2. `imaging.prepare_card` → carte normalisée 1000×630 (ou `None` → `ANOMALIE`).
3. `ocr.extract_fields` → champs (champs manquants ⇒ `VERIFICATION_COMPLEMENTAIRE`).
4. `capture.get_frame(face_source)` + `face.get_embedding` → empreinte porteur.
5. `face.get_embedding(carte)` → empreinte carte.
6. `database.get_person_by_number(numero)` → personne de référence (ou `None`).
7. `face.compare(card_emb, live_emb)` → score.
8. `decision.decide(...)` → statut + raisons + scores.
9. `database.log_verification(person_id, status, scores)`.

**Règle d'agrégation** : le **pire** statut l'emporte (`ANOMALIE` > `VERIFICATION_COMPLEMENTAIRE` > `VALIDE`). Court-circuit R1 : si la carte est illisible, on renvoie `ANOMALIE` sans appeler les modules suivants.

## 5. Choix techniques et justifications

| Choix                          | Raison                                           | Alternative écartée                                |
| ------------------------------ | ------------------------------------------------ | -------------------------------------------------- |
| **Python + venv**              | Portable, écosystème CV/IA mature, pas de compil | C++ (trop lent à développer en 15 j)               |
| **OpenCV DNN (YuNet + SFace)** | Modèles ONNX légers, CPU-friendly, ≥4.8          | dlib (lent, dépendances lourdes), TensorFlow (GPU) |
| **Tesseract `fra`**            | Simple, gratuit, PSM 6 adapté aux cartes         | OCR cloud (hors-scope, fuite de données)           |
| **SQLite**                     | Zéro-config, fichier unique, `sqlite3` stdlib    | PostgreSQL (surdimensionné pour un prototype)      |
| **numpy force brute 1:N**      | N petit (< 1000) → O(N) instantané               | ChromaDB (dépendance supplémentaire, en bonus C)   |
| **customtkinter**              | UI moderne sans framework web                    | Flask/FastAPI (dérive de stack)                    |
| **Séparation pipeline / UI**   | Testable en CLI, aucune dépendance tkinter       | UI qui appelle tout directement (non testable)     |
| **Threads + `self.after`**     | UI non figée, thread-safety Tkinter respectée    | Appels synchrones (UI gelée pendant verify)        |

## 6. Modèle de données (SQLite)

- **`persons`** : `id INTEGER PK`, `numero TEXT UNIQUE`, `nom, postnom, prenom, date_naissance TEXT`, `embedding BLOB`, `created_at TIMESTAMP`.
- **`verifications`** : `id INTEGER PK`, `person_id INTEGER FK`, `status TEXT`, `scores_json TEXT`, `created_at TIMESTAMP`.
- `embedding` stocké en `BLOB` (`np.ndarray.tobytes()`), relu via `np.frombuffer(..., dtype=np.float32)`.

## 7. Sécurité et vie privée

- ❌ Aucune **vraie** carte, aucune **vraie** photo. Jeu de test = cartes fictives + personnes consentantes.
- 🔒 Base locale uniquement, pas d'appel réseau hors ESP32 (LAN).
- 🧪 Pas d'anti-spoofing : une photo-de-photo peut tromper le système (hors-scope, voir README §Limites).

## 8. Pistes d'évolution (non implémentées)

- **Calibration** de `SEUIL_SFACE` sur un jeu > 50 paires.
- **Anti-spoofing** léger (détection de reflet / mouvement oculaire).
- **ChromaDB** (bonus C) : remplacer la force brute si N dépasse ~1000.
- **Migration `ESP32_URL`** de `ui.py` vers `config.py` (PROP. 6).
- **Package `src/`** avec `__init__.py` + imports relatifs (PROP. 3).
- **Tests automatisés** (`pytest`) sur les modules purs (`decision`, `vector_search`).

## 9. Références

- Brief maître : [`PROJECT_BRIEF.md`](PROJECT_BRIEF.md)
- État d'avancement : [`STATE.md`](STATE.md)
- Démonstration : [`DEMO.md`](DEMO.md)
- README projet : [`../README.md`](../README.md)
