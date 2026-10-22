"""Test J7 : lancer extract_raw_text sur les 10 cartes fictives."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import cv2  # noqa: E402

from ocr_v3 import extract_raw_text  # noqa: E402


def main() -> None:
    samples_dir = ROOT / "data" / "samples"
    # cards = [
    #     "Rose-M/test1_carte_1000x630.jpg",
    #     "Rose-M/test1_carte.jpg",
    #     "Rose-M/test2_carte.jpg",
    #     "images.jpeg",
    #     "test5.jpeg",
    # ]
    cards = sorted(
        samples_dir.glob("carte_fictive_*.jpg")
    )  # alors il faut ajoute .name à card_path pour le nom de l'emplacement

    if not cards:
        print(f"Aucune carte trouvee dans {samples_dir}")
        return

    print(f"{len(cards)} cartes a traiter\n")

    for card_path in cards:
        img = cv2.imread(str(card_path))
        if img is None:
            print(f"[SKIP] {card_path.name} : image illisible")
            print()
            continue

        text = extract_raw_text(img)
        print(f"===== {card_path.name} =====")
        print(text.rstrip() if text else "(vide)")
        print()


if __name__ == "__main__":
    main()
