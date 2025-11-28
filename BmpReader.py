import argparse
import struct


# Converts a byte size to a human-readable string (KB, MB, GB, TB),
# and also shows the raw byte count.
# Args:
#   bytes_size (int): Size in bytes.
# Returns:
#   str: Example: "1.2 MB (1200000 bytes)"
def format_size(bytes_size):
    if bytes_size >= 1_000_000_000_000:
        size_str = f"{bytes_size / 1_000_000_000_000:.1f} TB"
    elif bytes_size >= 1_000_000_000:
        size_str = f"{bytes_size / 1_000_000_000:.1f} GB"
    elif bytes_size >= 1_000_000:
        size_str = f"{bytes_size / 1_000_000:.1f} MB"
    elif bytes_size >= 1_000:
        size_str = f"{bytes_size / 1_000:.1f} KB"
    else:
        size_str = f"{bytes_size} bytes"
    return f"{size_str} ({bytes_size} bytes)"


class BmpInfos:
    """Container for all BMP metadata extracted by BmpReader.

    Stores BMP header (file signature, size, pixel data offset) and
    DIB header (image dimensions, color depth, compression, etc.)
    information. Provides direct access to all important fields
    as attributes.

    Example usage:
                    infos = BmpInfos(bmp_header, bmp_header_info)
                    print(infos.width, infos.height, infos.bit_count)

    Args:
                    bmp_header (dict): Raw BMP header metadata.
                    bmp_header_info (dict): Raw DIB header metadata.

    """

    def __init__(self, bmp_header: dict, bmp_header_info: dict):
        self.bmp_header = bmp_header
        self.bmp_header_info = bmp_header_info

        # BMP Header fields
        self.signature: str = ""
        self.file_size: int = 0
        self.data_offset: int = 0

        # DIB header fields
        self.header_size: int = 0
        self.width: int = 0
        self.height: int = 0
        self.planes: int = 0
        self.bit_count: int = 0
        self.compression: int = 0
        self.image_size: int = 0
        self.h_res: int = 0
        self.v_res: int = 0
        self.colors_used: int = 0
        self.colors_important: int = 0

        # Extended fields (for advanced BMP versions)
        self.masks: dict[str, str] = {}
        self.alpha_mask: int = 0
        self.color_space: int = 0
        self.endpoints: dict = {}
        self.gamma_red: int = 0
        self.gamma_green: int = 0
        self.gamma_blue: int = 0
        self.rendering_intent: int = 0
        self.icc_profile: dict = {}

        self._parse_infos()

    def _parse_infos(self):
        """
        Populates attributes from the BMP and DIB header dictionaries.

        All fields are set as attributes for easy access.
        If a field is missing (older BMP version), it remains None.
        """
        self.signature = self.bmp_header.get("Signature")
        self.file_size = self.bmp_header.get("FileSize")
        self.data_offset = self.bmp_header.get("DataOffset")

        self.header_size = self.bmp_header_info.get("HeaderSize")
        self.width = self.bmp_header_info.get("Width")
        self.height = self.bmp_header_info.get("Height")
        self.planes = self.bmp_header_info.get("Planes")
        self.bit_count = self.bmp_header_info.get("BitCount")
        self.compression = self.bmp_header_info.get("Compression")
        self.image_size = self.bmp_header_info.get("ImageSize")
        self.h_res = self.bmp_header_info.get("ResolutionX")
        self.v_res = self.bmp_header_info.get("ResolutionY")
        self.colors_used = self.bmp_header_info.get("ColorsUsed")
        self.colors_important = self.bmp_header_info.get("ColorsImportant")

        self.masks = self.bmp_header_info.get("Masks")
        self.alpha_mask = self.bmp_header_info.get("AlphaMask")
        self.color_space = self.bmp_header_info.get("ColorSpace")
        self.endpoints = self.bmp_header_info.get("Endpoints")
        self.gamma_red = self.bmp_header_info.get("GammaRed")
        self.gamma_green = self.bmp_header_info.get("GammaGreen")
        self.gamma_blue = self.bmp_header_info.get("GammaBlue")
        self.rendering_intent = self.bmp_header_info.get("RenderingIntent")
        self.icc_profile = self.bmp_header_info.get("ICCProfile")


class BmpReader:
    """
    Reads and parses BMP image files to extract metadata.

    Usage:
            reader = BmpReader(file_path="image.bmp")
            infos = reader.run()
            print(infos.width, infos.height, infos.bit_count, ...)

    Features:
            - Validates BMP signature.
            - Reads BMP header (file size, pixel data offset).
            - Reads DIB header (dimensions, color depth, compression, etc.).
            - Handles advanced BMP versions (color masks, color space, ICC profile).
            - Returns all metadata in a BmpInfos object.

    Args:
            data_file (bytes|None): BMP file data in memory.
            file_path (str|None): Path to BMP file (used if data_file is None).

    Raises:
            ValueError: If file is not a valid BMP or no data/path is provided.
    """

    def __init__(self, data_file=None, file_path=None):
        self.data_file: bytes = data_file
        self.file_path: str = file_path

        # If data is provided, check BMP signature immediately.
        # if not data_file.startswith(b"BM"):
        #     raise ValueError("Not a valid BMP file")

    def _get_img_compression(self, compression: int) -> str:
        """
        Returns a readable description for a BMP compression code.

        Args:
                compression (int): Compression code from DIB header.

        Returns:
                str: Compression type description.
        """
        compression_types = {
            0: "BI_RGB (no compression)",
            1: "BI_RLE8 (RLE 8-bit/pixel)",
            2: "BI_RLE4 (RLE 4-bit/pixel)",
            3: "BI_BITFIELDS (bit field or Huffman 1D compression)",
            4: "BI_JPEG (JPEG image for printing devices)",
            5: "BI_PNG (PNG image for printing devices)",
            6: "BI_ALPHABITFIELDS (RGBA bit field masks)",
            11: "BI_CMYK (no compression)",
            12: "BI_CMYKRLE8 (RLE-8 compression)",
            13: "BI_CMYKRLE4 (RLE-4 compression)",
        }
        return compression_types.get(compression, "Unknown compression type")

    def _get_csTypes(self, csType: int) -> str:
        """
        Returns a readable name for a BMP color space identifier.

        Args:
                csType (int): Color space code.

        Returns:
                str: Color space name.
        """
        csTypes = {
            0x73524742: "sRGB",
            0x57696E20: "Windows Color Space",
            0x4C494E4B: "Linked Color Profile",
            0x4D424544: "MBED Color Profile",
        }
        return csTypes.get(csType, "Unknown Color Space Type")

    def _get_img_header(self) -> dict:
        """
        Reads the BMP header (first 14 bytes).

        Returns:
                dict: Contains signature, file size, and pixel data offset.
        """
        header = {}
        bmp_header = self.data_file[:14]
        signature, FileSize, reserved, DataOffset = struct.unpack("<2sI4sI", bmp_header)
        header["Signature"] = f"Signature: {signature.decode('ascii')}"
        header["FileSize"] = f"FileSize: {format_size(FileSize)}"
        header["DataOffset"] = f"DataOffset: {DataOffset} bytes"
        return header

    def _get_img_header_info(self) -> dict:
        """
        Reads the DIB header (image info header).

        Handles all BMP header versions:
                - BITMAPCOREHEADER (12 bytes)
                - BITMAPINFOHEADER (40 bytes)
                - BITMAPV2INFOHEADER (52 bytes)
                - BITMAPV3INFOHEADER (56 bytes)
                - BITMAPV4HEADER (108 bytes)
                - BITMAPV5HEADER (124 bytes)

        Returns:
                dict: All extracted image metadata.
        """
        header_info = {}
        header_seek = 0

        bmp_BiSize = struct.unpack("<I", self.data_file[14:18])[0]
        header_info["HeaderSize"] = f"BMP Info Header Size: {bmp_BiSize} bytes"

        # BITMAPCOREHEADER (12 bytes)
        if bmp_BiSize == 12:
            size, width, height, planes, bpp = struct.unpack(
                "<IHHHH", self.data_file[14 : 14 + bmp_BiSize]
            )
            header_info["CoreHeader"] = size
            header_info["Width"] = width
            header_info["Height"] = height
            header_info["Planes"] = planes
            header_info["BitCount"] = bpp

        # BITMAPINFOHEADER and newer (>= 40 bytes)
        if bmp_BiSize >= 40:
            (
                size,
                width,
                height,
                planes,
                bpp,
                compression,
                imgSize,
                HRes,
                VRes,
                ColorUsed,
                ImpColor,
            ) = struct.unpack("<IIIHHIIIIII", self.data_file[14 : 14 + 40])
            header_info["InfoHeader"] = size
            header_info["Width"] = width
            header_info["Height"] = height
            header_info["Planes"] = planes
            header_info["BitCount"] = bpp
            header_info["Compression"] = self._get_img_compression(compression)
            header_info["ImageSize"] = imgSize
            header_info["ResolutionX"] = HRes
            header_info["ResolutionY"] = VRes
            header_info["ColorsUsed"] = "all" if ColorUsed == 0 else ColorUsed
            header_info["ColorsImportant"] = "all" if ImpColor == 0 else ImpColor
            header_seek = 54  # 14 (header) + 40 (info header)

        # RGB Masks (>= 52 bytes)
        if bmp_BiSize >= 52:
            redMask, greenMask, blueMask = struct.unpack(
                "<III", self.data_file[header_seek : header_seek + 12]
            )
            header_info["Masks"] = (
                f"RedMask: 0x{redMask:08X}, "
                f"GreenMask: 0x{greenMask:08X}, "
                f"BlueMask: 0x{blueMask:08X}"
            )
            header_seek += 12

        # Alpha mask (>= 56 bytes)
        if bmp_BiSize >= 56:
            alphaMask = struct.unpack(
                "<I", self.data_file[header_seek : header_seek + 4]
            )[0]
            header_info["AlphaMask"] = f"AlphaMask: 0x{alphaMask:08X}"
            header_seek += 4

        # BITMAPV4HEADER (>= 108 bytes)
        if bmp_BiSize >= 108:
            csType, *endpoints, gammaRed, gammaGreen, gammaBlue = struct.unpack(
                "<I9i3i", self.data_file[header_seek : header_seek + 52]
            )
            header_info["ColorSpace"] = (
                f"Color Space Type: 0x{csType:08X} ({self._get_csTypes(csType)})"
            )
            header_info["Endpoints"] = [
                f"X:{endpoints[0]}, Y:{endpoints[1]}, Z:{endpoints[2]}",
                f"X:{endpoints[3]}, Y:{endpoints[4]}, Z:{endpoints[5]}",
                f"X:{endpoints[6]}, Y:{endpoints[7]}, Z:{endpoints[8]}",
            ]
            header_info["GammaRed"] = (
                f"{'No correction' if gammaRed == 0 else gammaRed}"
            )
            header_info["GammaGreen"] = (
                f"{'No correction' if gammaGreen == 0 else gammaGreen}"
            )
            header_info["GammaBlue"] = (
                f"{'No correction' if gammaBlue == 0 else gammaBlue}"
            )
            header_seek += 52

        # BITMAPV5HEADER (>= 124 bytes)
        if bmp_BiSize >= 124:
            intent, profileData, profileSize, reserved = struct.unpack(
                "<IIII", self.data_file[header_seek : header_seek + 16]
            )
            intents_types = {
                0: "LCS_GM_ABS_COLORIMETRIC",
                1: "LCS_GM_BUSINESS",
                2: "LCS_GM_GRAPHICS",
                4: "LCS_GM_IMAGES",
            }
            header_info["RenderingIntent"] = f"{intents_types.get(intent, intent)}"
            if profileSize != 0:
                header_info["ICCProfile"] = (
                    f"ICC Profile embedded at offset {profileData}, "
                    f"size {profileSize} bytes"
                )
            else:
                header_info["ICCProfile"] = (
                    "ICC Profile: No profile embedded; standard sRGB is used."
                )
            header_seek += 16

        return header_info

    def run(self) -> BmpInfos:
        """
        Reads the BMP file and returns all metadata.

        Usage:
                infos = BmpReader(file_path="image.bmp").run()
                print(infos.width, infos.height, infos.bit_count, ...)

        Returns:
                BmpInfos: Object containing all BMP metadata (see Attributes).
                None: If an error occurs.

        Attributes:
                bmp_header (dict): Raw BMP header metadata.
                bmp_header_info (dict): Raw DIB header metadata.
                signature (str): BMP file signature (e.g., 'BM').
                file_size (int): Total size of the BMP file in bytes.
                data_offset (int): Offset to the start of pixel data.

                header_size (int): Size of the DIB header.
                width (int): Image width in pixels.
                height (int): Image height in pixels.
                planes (int): Number of color planes (usually 1).
                bit_count (int): Number of bits per pixel.
                compression (int): Compression method used.
                image_size (int): Size of the raw bitmap data.
                h_res (int): Horizontal resolution (pixels per meter).
                v_res (int): Vertical resolution (pixels per meter).
                colors_used (int): Number of colors in the palette.
                colors_important (int): Number of important colors.

                masks (dict): Color masks for bitfields compression.
                alpha_mask (int): Alpha channel mask.
                color_space (int): Color space type.
                endpoints (dict): Color space endpoints.
                gamma_red (int): Red channel gamma correction.
                gamma_green (int): Green channel gamma correction.
                gamma_blue (int): Blue channel gamma correction.
                rendering_intent (int): Rendering intent.
                icc_profile (dict): ICC color profile data.
        """
        try:
            if not self.data_file:
                if not self.file_path:
                    raise ValueError("No data or file path provided")
                with open(self.file_path, "rb") as f:
                    self.data_file = f.read()
            bmp_header = self._get_img_header()
            header_info = self._get_img_header_info()
            return BmpInfos(bmp_header, header_info)
        except Exception as e:
            print(f"Error reading BMP file: {e}")
            return None


def main():
    """
    Command-line usage:
            python BmpReader.py image1.bmp image2.bmp ...

    Prints metadata for each BMP file provided.
    """
    parser = argparse.ArgumentParser(
        prog="scorpion", description="Read metadata from image files"
    )
    parser.add_argument(
        "image_files", nargs="+", help="List of image files in these formats: [.bmp]"
    )
    args = parser.parse_args()

    for file in args.image_files:
        with open(file, "rb") as f:
            data = f.read()
        bmp_infos: BmpInfos = BmpReader(data_file=data).run()
        print(f"{bmp_infos.signature}")
        print(f"{bmp_infos.file_size}")
        print(f"{bmp_infos.data_offset}")
        print(f"{bmp_infos.header_size}")
        print(f"{bmp_infos.width} x {bmp_infos.height} pixels")
        print(f"{bmp_infos.bit_count} bits per pixel")
        print(f"{bmp_infos.compression}")
        print(f"{bmp_infos.image_size} bytes image data")
        print(f"{bmp_infos.h_res} px/m horizontal resolution")
        print(f"{bmp_infos.v_res} px/m vertical resolution")
        print(f"{bmp_infos.colors_used} colors used")
        print(f"{bmp_infos.colors_important} colors important")
        if bmp_infos.masks:
            print(f"{bmp_infos.masks}")
        if bmp_infos.alpha_mask:
            print(f"{bmp_infos.alpha_mask}")
        if bmp_infos.color_space:
            print(f"{bmp_infos.color_space}")
        if bmp_infos.endpoints:
            print("Color Endpoints:")
            for idx, endpoint in enumerate(bmp_infos.endpoints):
                print(f"  Primary {idx + 1}: {endpoint}")
        if bmp_infos.gamma_red:
            print(f"Gamma Red: {bmp_infos.gamma_red}")
        if bmp_infos.gamma_green:
            print(f"Gamma Green: {bmp_infos.gamma_green}")
        if bmp_infos.gamma_blue:
            print(f"Gamma Blue: {bmp_infos.gamma_blue}")
        if bmp_infos.rendering_intent:
            print(f"Rendering Intent: {bmp_infos.rendering_intent}")
        if bmp_infos.icc_profile:
            print(f"{bmp_infos.icc_profile}")


if __name__ == "__main__":
    main()
