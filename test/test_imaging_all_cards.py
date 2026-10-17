# tests/test_imaging_all_cards.py
# Vérifie que toutes les fonctions de imaging.py tournent sur les 10 cartes fictives.
# Outil de test, hors contrat §6.

import sys
from pathlib import Path

# Permet d'importer imaging.py depuis src/ sans package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from config import SAMPLES_DIR  # noqa: E402
from imaging import (  # noqa: E402
    apply_blur,
    apply_otsu,
    apply_threshold,
    detect_edges,
    load_image,
    resize_image,
    to_grayscale,
)


def run_on_one(path: Path) -> bool:
    img = load_image(str(path))
    if img is None:
        print(f"ECHEC chargement : {path.name}")
        return False
    gray = to_grayscale(img)
    blurred = apply_blur(img, 5)
    resized = resize_image(img, 500, 315)
    thr = apply_threshold(gray, 127)
    otsu = apply_otsu(gray)
    edges = detect_edges(img, 50, 150)
    all_ok = all(x is not None for x in (gray, blurred, resized, thr, otsu, edges))
    if not all_ok:
        print(f"ECHEC traitement : {path.name}")
        return False
    print(f"OK : {path.name}")
    return True


def main() -> None:
    cards = sorted(SAMPLES_DIR.glob("carte_fictive_*.jpg"))
    if not cards:
        print(f"Aucune carte trouvée dans {SAMPLES_DIR}")
        sys.exit(1)
    print(f"{len(cards)} carte(s) trouvée(s)")
    ok = sum(run_on_one(c) for c in cards)
    print(f"\nBilan : {ok}/{len(cards)} cartes OK")
    sys.exit(0 if ok == len(cards) else 1)


if __name__ == "__main__":
    main()
