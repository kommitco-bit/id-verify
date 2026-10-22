"""Configuration centrale du projet id-verif.

Tous les chemins, seuils et paramètres vivent ici.
Aucune autre partie du code ne doit contenir de valeur "magique".
"""

from pathlib import Path

# --- Racine du projet -------------------------------------------------------
# __file__ est le chemin de ce fichier (src/config.py).
# .resolve() donne le chemin absolu.
# .parent.parent remonte de src/ vers la racine id-verif/.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# --- Dossiers ---------------------------------------------------------------
DATA_DIR = PROJECT_ROOT / "data"
SAMPLES_DIR = DATA_DIR / "samples"  # photos de test fictives
DB_DIR = DATA_DIR / "db"  # fichier SQLite
MODELS_DIR = PROJECT_ROOT / "models"  # modèles .onnx
DOCS_DIR = PROJECT_ROOT / "docs"

# --- Fichiers ---------------------------------------------------------------
DB_PATH = DB_DIR / "id_verif.db"

# Modèles ONNX (à télécharger plus tard, J4 et J5)
YUNET_MODEL = MODELS_DIR / "face_detection_yunet_2023mar.onnx"
SFACE_MODEL = MODELS_DIR / "face_recognition_sface_2021dec.onnx"

# --- Réseau / ESP32-CAM -----------------------------------------------------
# Adresse par défaut de l'ESP32-CAM sur le réseau local.
# À modifier quand tu connaîtras son IP réelle.
ESP32_URL = "http://10.135.250.228/capture"
HTTP_TIMEOUT_SECONDS = 5

# --- Paramètres images ------------------------------------------------------
CARD_WIDTH = 1000  # largeur cible après redressement de la carte
CARD_HEIGHT = 630  # hauteur cible (ratio proche d'une carte d'identité)

# --- Seuils de décision -----------------------------------------------------
# Similarité cosinus minimale pour considérer deux visages identiques.
# Valeur de départ issue du papier SFace, à calibrer sur nos propres tests.
FACE_MATCH_THRESHOLD = 0.363

# Écart toléré entre la similarité carte/porteur et la meilleure
# correspondance en base : sert à détecter une incohérence.
FACE_AMBIGUITY_MARGIN = 0.05

# Nombre de voisins à examiner lors d'une recherche 1:N.
VECTOR_SEARCH_K = 3

# --- Codes de statut (ne pas modifier sans accord) --------------------------
STATUS_VALID = "VALIDE"
STATUS_ANOMALY = "ANOMALIE"
STATUS_NEED_MORE = "VERIFICATION_COMPLEMENTAIRE"
VALID_STATUSES = {"VALIDE", "ANOMALIE", "VERIFICATION_COMPLEMENTAIRE"}
# ===== J9 : seuils SFace — À AJOUTER à la fin de src/config.py =====
# Calibré le 19/10 sur 6 paires (2 même-personne, 4 différentes) :
#   min(même-personne) = 0.3414
#   max(différentes)   = 0.0352
# Compromis retenu : marge forte au-dessus du bruit, marge modérée sous le signal.
SEUIL_SFACE = 0.30

# Référence officielle OpenCV/SFace (sur grands jeux de données).
# Conservée pour comparaison ; NE PAS l'utiliser comme seuil de décision ici
# (rejetterait la personne A sur notre échantillon).
SEUIL_SFACE_REFERENCE = 0.363


# --- Utilitaires ------------------------------------------------------------
def ensure_dirs() -> None:
    """Crée les dossiers nécessaires s'ils n'existent pas."""
    for d in (DATA_DIR, SAMPLES_DIR, DB_DIR, MODELS_DIR):
        d.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    # Petit test rapide : affiche la racine et crée les dossiers.
    ensure_dirs()
    print(f"PROJECT_ROOT = {PROJECT_ROOT}")
    print(f"SAMPLES_DIR  = {SAMPLES_DIR}")
    print(f"DB_PATH      = {DB_PATH}")
    print("Dossiers créés/vérifiés.")
