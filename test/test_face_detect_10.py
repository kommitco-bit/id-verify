# test/test_face_detect_10.py — J8 étape 2 : taux de détection sur 10 frames live
import sys
import time

sys.path.insert(0, "src")

from capture import get_frame
from face import _detect_faces

# Source : 'webcam:0' ou 'http://10.135.250.228/capture'
SOURCE = "webcam:0"
N_FRAMES = 10
DELAY_S = 0.3  # laisse le temps entre deux captures


def main():
    detected = 0

    for i in range(N_FRAMES):
        img = get_frame(SOURCE)
        if img is None:
            print(f"Frame {i + 1:02d} : capture échouée")
            time.sleep(DELAY_S)
            continue

        faces = _detect_faces(img)
        n = len(faces)

        if n >= 1:
            detected += 1
            best = max(faces, key=lambda f: f["score"])
            print(
                f"Frame {i + 1:02d} : {n} visage(s) — score max = {best['score']:.3f}"
            )
        else:
            print(f"Frame {i + 1:02d} : aucun visage détecté")

        time.sleep(DELAY_S)

    print("\n--- Résultat ---")
    print(f"Détection : {detected}/{N_FRAMES} frames avec au moins 1 visage")
    taux = 100 * detected / N_FRAMES
    print(f"Taux : {taux:.0f}%")


if __name__ == "__main__":
    main()
