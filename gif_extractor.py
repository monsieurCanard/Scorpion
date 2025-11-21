from unittest import case


class GifImage:
    def __init__(self, image_delay: int, transparent_color_index: int):
        self.image_delay = image_delay
        self.transparent_color_index = transparent_color_index


class AppExtension:
    def __init__(self, app_identifier: bytes, app_data: bytes):
        self.app_identifier = app_identifier
        self.app_data: bytearray = app_data


class CommentExtension:
    def __init__(self, comment_data: str):
        self.comment_data = comment_data


class GifExtractor:
    def __init__(self, data: bytes, filename: str):
        self.data: bytes = data
        self.offset: int = 0
        self.filename = filename

        self.signature = ""
        self.version = ""
        self.width = 0
        self.height = 0
        self.global_color_table_flag = 0
        self.color_resolution = 0
        self.sort_flag = 0
        self.size_of_gct = 0
        self.background_color_index = 0
        self.images: list[GifImage] = []
        self.app_extensions: list[AppExtension] = []
        self.comment_extensions: list[CommentExtension] = []
        self.plain_text_extensions: list[str] = []

    def extract(self):
        while self.data[self.offset] != 0x3B:  # 0x3B is the GIF file terminator
            byte = self.data[self.offset]
            match byte:
                case 0x2C:  # Image Descriptor
                    self.skip_image()
                    break
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
            self.comment_extensions.append(CommentExtension(comment_text))
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
                self.images.append(GifImage(delay, transparent_index))
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
                self.offset += block_size

                app_info = AppExtension(app_identifier, bytearray())
                while self.data[self.offset] != 0:
                    size = self.data[self.offset]
                    self.offset += 1
                    app_info.app_data += self.data[self.offset : self.offset + size]
                    self.offset += size
                self.offset += 1
                self.app_extensions.append(app_info)
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

                self.plain_text_extensions.append(text_data)
                self.offset += 1
                return
            case _:
                self.offset += 2

                while self.data[self.offset] != 0:
                    block_size = self.data[self.offset]
                    self.offset += 1 + block_size
                self.offset += 1
                return self.offset

    def _identify_extension_type(self, data: bytes) -> str:
        """Identifie le type d'extension inconnue"""

        # Détection EXIF (plusieurs patterns possibles)
        if (
            data.startswith(b"Exif")
            or data.startswith(b"\xff\xd8\xff")  # JPEG marker
            or data.startswith(b"\x49\x49\x2a\x00")  # TIFF little-endian
            or data.startswith(b"\x4d\x4d\x00\x2a")  # TIFF big-endian
            or b"Exif\x00\x00" in data[:20]
        ):
            return "exif"

        # Détection XMP
        elif data.startswith(b"<?xpacket") or b"<x:xmpmeta" in data[:50]:
            return "xmp"

        # Détection ICC Profile
        elif b"ICC_PROFILE" in data[:50]:
            return "icc"

        # Texte ASCII simple
        elif data[:50].isascii() and len(data) > 3:
            text = data.decode("ascii")
            if text.isprintable():
                return "text"

        return "unknown"

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

        self.signature = signature
        self.version = version

        # ! Lsd bytes -> Logical Screen Descriptor
        # 6-7 : Width (2 bytes)
        # 8-9 : Height (2 bytes)
        # 10   : Packed Fields (1 byte) ( Global Color Table Flag, Color Resolution, Sort Flag, Size of Global Color Table)
        # 11   : Background Color Index (1 byte)
        # 12   : Pixel Aspect Ratio (1 byte)
        lsd = self.data[6:13]
        self.width = int.from_bytes(lsd[0:2], "little")
        self.height = int.from_bytes(lsd[2:4], "little")
        self.global_color_table_flag = (lsd[4] & 0b10000000) >> 7
        self.color_resolution = ((lsd[4] & 0b01110000) >> 4) + 1

        # Sort Flag : 1 bit (1 = global color table is sorted)
        # Sort Flag : 1 bit (0 = global color table is not sorted)
        self.sort_flag = (lsd[4] & 0b00001000) >> 3

        self.size_of_gct = 2 ** ((lsd[4] & 0b00000111) + 1)
        self.background_color_index = lsd[5]

        self.pixel_aspect_ratio = lsd[6]
        if self.pixel_aspect_ratio != 0:
            self.aspect_ratio = (self.pixel_aspect_ratio + 15) / 64
        else:
            self.aspect_ratio = None

        # Background Color Index : 1 byte (index in the global color table)
        # Couleur de fond de l'image
        background_color_index = lsd[5]
        print(f"Background Color Index: {background_color_index}")

        start_index = 13
        if self.global_color_table_flag:
            # ! Global Color Table
            size = 3 * self.size_of_gct
            gct = self.data[start_index : start_index + size]
            # print(f"Number of differents colors {size // 3}")
            # print("First 3 colors in Global Color Table:")
            # for i in range(size // 3):
            #     r = gct[i * 3]
            #     g = gct[i * 3 + 1]
            #     b = gct[i * 3 + 2]
            # print(f"  Color {i}: R={r} G={g} B={b}")
        return

    def print_all_infos(self):
        print("================================")
        print(f"GIF Extractor Metadata from file: {self.filename}")
        print("================================")
        print("Header Information:")
        print("--------------------------------")
        print(f"Signature: {self.signature}")
        print(f"Version: {self.version}")
        print(f"Width: {self.width} pixels")
        print(f"Height: {self.height} pixels")
        print(f"Global Color Table Flag: {self.global_color_table_flag}")
        print(f"Color Resolution: {self.color_resolution} bits per primary color")
        print(f"Sort Flag: {self.sort_flag}")
        print(f"Size of Global Color Table: {self.size_of_gct} colors")
        # print(f"Background Color Index: {self.background_color_index}")
        print("================================")
        print("Images informations:")
        print("================================")
        for i, image in enumerate(self.images):
            print(
                f"Image {i + 1}: Delay={image.image_delay} cs, Transparent Color Index={image.transparent_color_index}"
            )

        print("================================")
        print("Application Extensions:")
        print("================================")

        for i, app_ext in enumerate(self.app_extensions):
            print(
                f"Application Extension {i + 1}: Identifier={app_ext.app_identifier}, Data Length={len(app_ext.app_data)} bytes"
                f" App Data={app_ext.app_data.decode('ascii', errors='ignore')}"
            )

        print("================================")
        print("Comment Extensions:")
        print("================================")
        for i, comment_ext in enumerate(self.comment_extensions):
            print(f"Comment Extension {i + 1}: Comment Data={comment_ext.comment_data}")

    def run(self):
        self.extract_header()
        self.extract()
        self.print_all_infos()
