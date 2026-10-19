# test/test_face_detect.py — J8 étape 1 : test isolé de la détection YuNet
import sys

sys.path.insert(0, "src")  # contournement temporaire, comme les autres tests
import cv2

from face import _crop_face, _detect_faces


def main():
    # On utilise une carte fictive existante : elle contient une photo de visage.
    img = cv2.imread("test4.jpg")
    if img is None:
        print("ERREUR : image introuvable. Vérifie le chemin.")
        return

    faces = _detect_faces(img)
    print(f"Visages détectés : {len(faces)}")

    for i, f in enumerate(faces):
        print(f"  Visage {i + 1} : bbox={f['bbox']}, score={f['score']:.3f}")
        crop = _crop_face(img, f["bbox"])
        if crop is not None:
            out_path = f"test/face_crop_{i + 1}.jpg"
            cv2.imwrite(out_path, crop)
            print(f"  → recadrage sauvegardé : {out_path}")


if __name__ == "__main__":
    main()
