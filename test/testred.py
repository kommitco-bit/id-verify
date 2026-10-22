from pathlib import Path

from PIL import Image, ImageOps

LARGEUR, HAUTEUR = 1000, 630


def redimensionner(entree, sortie=None, qualite=85):
    entree = Path(entree)
    sortie = Path(sortie) if sortie else entree.with_name(f"{entree.stem}_1000x630.jpg")

    with Image.open(entree) as img:
        # Accélère le chargement des gros JPEG (décodage à échelle réduite)
        img.draft("RGB", (LARGEUR * 2, HAUTEUR * 2))

        # Corrige l'orientation selon les données EXIF (photos de téléphone)
        img = ImageOps.exif_transpose(img)

        # Redimensionne ET recadre au centre pour éviter toute déformation
        img = ImageOps.fit(
            img,
            (LARGEUR, HAUTEUR),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )

        # Le JPEG ne gère pas la transparence
        if img.mode != "RGB":
            img = img.convert("RGB")

        img.save(sortie, "JPEG", quality=qualite, optimize=True, progressive=True)

    print(f"OK : {sortie} ({sortie.stat().st_size / 1024:.1f} Ko)")

    return str(sortie)


if __name__ == "__main__":
    redimensionner("Rose-M/test1_carte.jpg")
