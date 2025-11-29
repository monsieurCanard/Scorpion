from PIL import Image
from io import BytesIO
import argparse

from metadata_readers.JpgReader import JPGParser


class PngReader:
    """
    PngReader is a class for reading and extracting metadata from PNG image files.
    Attributes:
            path_file (str): Path to the PNG file.
            data (bytes): Raw image data in bytes.
            img (PIL.Image.Image): Opened image object.
            img_info (dict): Dictionary containing extracted image information.
    Methods:
            __init__(data=None, path_file=None):
                    Initializes the PngReader with image data or a file path.
            _open_img():
                    Opens the image from the provided data or path. Raises ValueError if the image is not a valid PNG.
            _extract_infos():
                    Extracts metadata and information from the opened image, including signature, format, size, byte size, mode, info, and EXIF data.
            run():
                    Opens the image and returns the dictionary of extracted information if successful.
    """

    def __init__(self, data: bytes | None = None, path_file: str | None = None):
        self.path_file = path_file
        self.data = data

        self.img = None
        self.img_info = dict()

    def _open_img(self):
        try:
            if self.data:
                img = Image.open(BytesIO(self.data))
            else:
                img = Image.open(self.path_file)
            if img.format != "PNG":
                raise ValueError("Not a valid PNG file")
            self.img = img
        except Exception as e:
            print(f"Error opening image {self.path_file}: {e}")

    def _extract_infos(self) -> dict:
        # Taille du fichier complet en bytes (avec Pillow)
        buf = BytesIO()
        self.img.save(buf, format=self.img.format)
        data = buf.getvalue()

        self.img_info.update(
            {
                "Signature": buf.getvalue()[:8].hex(" ").upper(),
                "Format": self.img.format,
                "Size (width, height)": self.img.size,
                "Size (bytes)": len(data),
                "Color Mode": self.img.mode,
                # "Info": self.img.info,
                "EXIF": JPGParser.extract_exif(self.path_file),
            }
        )

        return self.img_info

    def run(self) -> dict:
        """Extrait et retourne les métadonnées principales de l'image PNG.

        Construit et enrichit le dictionnaire `self.img_info` avec les clés suivantes :

        Retourne:
                dict: Dictionnaire contenant:
                        - Signature (str): Les 8 premiers octets du fichier PNG (signature PNG) en hexadécimal
                            séparés par des espaces, en majuscules. Exemple: "89 50 4E 47 0D 0A 1A 0A".
                        - Format (str): Format reconnu par Pillow (doit être "PNG").
                        - Taille (tuple[int,int]): Dimensions de l'image (largeur, hauteur) en pixels.
                        - Poids (bytes) (int): Taille totale en octets lors de la réécriture complète via Pillow.
                        - Mode (str): Mode couleur Pillow (ex: "RGB", "RGBA", "P", etc.).
                        - Info (dict): Métadonnées internes Pillow extraites du chunk IHDR et autres chunks
                            interprétés (peut contenir par exemple "gamma", "dpi", "interlace", "background",
                            "transparency", "comment", etc. selon le fichier). Ce contenu dépend des chunks présents.
                        - EXIF (dict | None): Données EXIF si présentes et reconnues (rare dans PNG), sous forme
                            de mapping { nom_tag: valeur }. `None` si aucune donnée EXIF disponible.

        Notes:
                - La signature PNG est toujours: 89 50 4E 47 0D 0A 1A 0A.
                - Le champ "Size (bytes)" correspond à la taille des données réencodées par Pillow, ce qui
                    peut différer légèrement de la taille sur disque originale (optimisations, réorganisation).
                - Le champ EXIF est généralement absent dans les PNG (préférer les chunks tEXt / iTXt / zTXt
                    ou XMP pour les métadonnées). Pillow expose EXIF seulement si présent.
        """
        self._open_img()
        if self.img:
            return self._extract_infos()


def main():
    parser = argparse.ArgumentParser(
        prog="scorpion", description="reading metadata of images file"
    )
    parser.add_argument(
        "image_files", nargs="+", help="list of image file in thoses format : [.png]"
    )
    args = parser.parse_args()

    for file in args.image_files:
        with open(file, "rb") as f:
            data = f.read()
        print(f"{PngReader(data=data).run()}")


if __name__ == "__main__":
    main()
