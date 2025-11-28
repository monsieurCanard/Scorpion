class GifImage:
    def __init__(self, image_delay: int, transparent_color_index: int):
        self.image_delay = image_delay
        self.transparent_color_index = transparent_color_index


class AppExtension:
    def __init__(self, app_identifier: bytes, app_data: bytes):
        self.app_identifier = app_identifier
        self.app_data: bytearray = app_data
        self.loop_count: int = 0


class CommentExtension:
    def __init__(self, comment_data: str):
        self.comment_data = comment_data


class GifReader:
    def __init__(self, data: bytes, filename: str):
        self.data: bytes = data
        self.offset: int = 0
        self.infos = dict()

    def extract(self):
        while self.data[self.offset] != 0x3B:  # 0x3B is the GIF file terminator
            byte = self.data[self.offset]
            match byte:
                case 0x2C:  # Image Descriptor
                    self.skip_image()
                    continue
                case 0x21:  # Extension Introducer
                    self.handle_extension()
                case _:
                    self.offset += 1
                    # Move to the next byte

    def read_comment_extension(self):
        self.offset += 2  # Skip the label byte

        while self.data[self.offset] != 0:
            block_size = self.data[self.offset]
            self.offset += 1
            comment_data = self.data[self.offset : self.offset + block_size]
            comment_text = comment_data.decode("ascii", errors="ignore")
            self.infos.setdefault("Comment Extensions", []).append(comment_text)
            self.offset += block_size  # Move to the next sub-block

        self.offset += 1  # Skip the block terminator

    def handle_extension(self):
        label = self.data[self.offset + 1]

        match label:
            case 0xF9:  # Graphic Control Extension (GIF89a)
                self.offset += 3
                delay = self.data[self.offset + 1] + (self.data[self.offset + 2] << 8)
                transparent_index = self.data[self.offset + 3]
                self.offset += 5
                self.infos.setdefault("Images", []).append(
                    {"delay": delay, "transparent_index": transparent_index}
                )
                return
            case 0xFE:
                self.read_comment_extension()
                return
            case 0xFF:
                self.offset += 2
                block_size = self.data[
                    self.offset
                ]  # La taille du bloc est variable ici
                self.offset += 1
                app_identifier = self.data[self.offset : self.offset + block_size]
                application = app_identifier.decode("ascii", errors="ignore")
                self.offset += block_size

                app_data = bytearray()
                while self.data[self.offset] != 0:
                    size = self.data[self.offset]
                    self.offset += 1
                    app_data += self.data[self.offset : self.offset + size]
                    self.offset += size
                self.offset += 1
                self.infos.setdefault("App Extensions", []).append(
                    {"application": application, "data length": len(app_data)}
                )
                return
            case 0x01:  # Plain Text Extension (GIF89a)
                self.offset += 2
                block_size = self.data[self.offset]
                self.offset += 1 + block_size
                text_data = ""
                while self.data[self.offset] != 0:
                    sub_block_size = self.data[self.offset]
                    self.offset += 1
                    text_data += self.data[
                        self.offset : self.offset + sub_block_size
                    ].decode("ascii", errors="ignore")
                    self.offset += sub_block_size

                self.infos.setdefault("Plain Text Extensions", []).append(text_data)
                self.offset += 1
                return
            case _:
                self.offset += 2
                while self.data[self.offset] != 0:
                    block_size = self.data[self.offset]
                    self.offset += 1 + block_size
                self.offset += 1
                return self.offset

    def skip_image(self):
        if self.offset + 9 >= len(self.data):
            return len(self.data)

        packed = self.data[self.offset + 9]
        local_color_table_flag = (packed & 0b10000000) >> 7
        size_of_lct = packed & 0b00000111

        if local_color_table_flag:
            entries = 2 ** (size_of_lct + 1)
            table_size = 3 * entries
            if self.offset + 10 + table_size >= len(self.data):
                return len(self.data)
            self.offset += table_size  # Each color is 3 bytes (RGB)

        self.offset += 10
        if self.offset >= len(self.data):
            return len(self.data)

        self.offset += 1  # LZW Minimum Code Size
        if self.offset >= len(self.data):
            return len(self.data)

        while self.data[self.offset] != 0:  # Data Sub-blocks
            block_size = self.data[self.offset]
            if block_size == 0:
                self.offset += 1
                break
            self.offset += block_size + 1  # Move to the next sub-block

        self.offset += 1  # Skip the block terminator

    def extract_header(self):
        # GIF89a (norme de 1989) or GIF87a (norme de 1987)
        header = self.data[:6]
        version = header[3:].decode("ascii")
        signature = header[:3].decode("ascii")
        self.infos["Signature"] = signature
        self.infos["Version"] = version

        # ! Lsd bytes -> Logical Screen Descriptor
        # 6-7 : Width (2 bytes)
        # 8-9 : Height (2 bytes)
        # 10   : Packed Fields (1 byte) ( Global Color Table Flag, Color Resolution, Sort Flag, Size of Global Color Table)
        # 11   : Background Color Index (1 byte)
        # 12   : Pixel Aspect Ratio (1 byte)
        lsd = self.data[6:13]
        self.infos["Width"] = int.from_bytes(lsd[0:2], "little")
        self.infos["Height"] = int.from_bytes(lsd[2:4], "little")
        self.infos["Global Color Table Flag"] = (lsd[4] & 0b10000000) >> 7
        self.infos["Color Resolution"] = ((lsd[4] & 0b01110000) >> 4) + 1

        # Sort Flag : 1 bit (1 = global color table is sorted)
        # Sort Flag : 1 bit (0 = global color table is not sorted)
        self.infos["Sort Flag"] = (lsd[4] & 0b00001000) >> 3
        self.infos["Size of Global Color Table"] = 2 ** ((lsd[4] & 0b00000111) + 1)
        self.infos["Background Color Index"] = lsd[5]

        self.pixel_aspect_ratio = lsd[6]
        if self.pixel_aspect_ratio != 0:
            self.infos["Aspect Ratio"] = (self.pixel_aspect_ratio + 15) / 64
        else:
            self.infos["Aspect Ratio"] = None

        # Background Color Index : 1 byte (index in the global color table)
        # Couleur de fond de l'image
        self.infos["Background Color Index"] = lsd[5]
        return

    def run(self):
        """
        Extracteur de métadonnées pour fichiers GIF87a et GIF89a.

        Attributes
        ----------
        data : bytes
            Contenu brut du fichier GIF.
        offset : int
            Position actuelle dans le parsing du fichier.
        filename : str
            Nom du fichier GIF analysé.
        signature : str
            Signature du fichier GIF (doit être "GIF").
        version : str
            Version du format GIF ("87a" ou "89a").
        width : int
            Largeur de l'image en pixels.
        height : int
            Hauteur de l'image en pixels.
        global_color_table_flag : int
            Indique la présence d'une table de couleurs globale (1 = présente, 0 = absente).
        color_resolution : int
            Résolution des couleurs (nombre de bits par couleur primaire).
        sort_flag : int
            Indique si la table de couleurs globale est triée (1 = triée, 0 = non triée).
        size_of_gct : int
            Taille de la table de couleurs globale (nombre d'entrées).
        background_color_index : int
            Index de la couleur de fond dans la table de couleurs globale.
        images : list of GifImage
            Liste des images extraites du GIF.

            Chaque GifImage contient :

            - image_delay : int
                Délai d'affichage en centièmes de seconde (0.01s par unité).
            - transparent_color_index : int
                Index de la couleur transparente dans la palette (0-255).

        app_extensions : list of AppExtension
            Application Extensions détectées dans le fichier.

            Chaque AppExtension contient :

            - app_identifier : bytes
                Identifiant de l'application sur 11 bytes.
                Format : 8 bytes nom + 3 bytes version.
                Exemple : b'NETSCAPE2.0'
            - app_data : bytearray
                Données binaires spécifiques à l'application.
            - loop_count : int, optional
                Nombre de boucles d'animation (0 = infini).
                Présent uniquement pour NETSCAPE2.0 et ANIMEXTS1.0.

        comment_extensions : list of CommentExtension
            Commentaires texte extraits du GIF.

            Chaque CommentExtension contient :

            comment_data : str
                Texte du commentaire en ASCII.
        """
        self.extract_header()
        self.extract()
