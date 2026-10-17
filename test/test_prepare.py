import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import cv2
from extraire_carte_v2 import extraire_carte

import imaging

for p in ["""liste de chemin des images"""]:
    # ins = redimensionner(p)
    img = imaging.load_image(p)
    if img is None:
        print(f"{p} : illisible")
        continue
    flat = imaging.prepare_card(img)
    if flat is None:
        print(f"{p} : prepare_card -> None (rejete)")
    else:
        print(f"{p} : prepare_card -> {flat.shape}")
        out = Path("test") / (Path(p).stem + "_prepared.jpg")
        cv2.imwrite(str(out), flat)
        out = extraire_carte(str(out))
        print(f"           sauvegarde : {out}")
