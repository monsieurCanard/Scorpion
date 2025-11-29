import argparse
import os
from metadata_readers.GifReader import GifReader
from metadata_readers.BmpReader import BmpReader, BmpInfos
from metadata_readers.PngReader import PngReader
from metadata_readers.JpgReader import JPGParser
from utils.printer import print_metadata


def init_arg_parse():
    parser = argparse.ArgumentParser(
        description="Analyse and extract metadata from file(s)"
    )
    parser.add_argument("files", nargs="+", help="Un ou plusieurs fichiers a analyser")

    args = parser.parse_args()
    return args.files


def identify_file_type(data: bytes):
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "PNG"
    elif data.startswith(b"BM"):
        return "BMP"
    elif data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return "GIF"
    elif data.startswith(b"\xff\xd8\xff"):
        return "JPEG"
    else:
        return "UNKNOWN"


def extract_gif(data: bytes, filename: str):
    extractor = GifReader(data, filename)
    metadata = extractor.run()
    print_metadata(filename, "GIF", extractor.infos)


def extract_jpg(data: bytes, filename: str):
    parser = JPGParser(filename)
    metadata = parser.run()
    print_metadata(filename, "JPEG", metadata)


def extract_bmp(data: bytes, filename: str):
    extractor = BmpReader(data, filename)
    metadata = extractor.run()
    print_metadata(filename, "BMP", metadata.bmp_header_info)


def extract_png(data: bytes, filename: str):
    extractor = PngReader(data, filename)
    metadata = extractor.run()
    print_metadata(filename, "PNG", extractor.img_info)


def error_extension(data, filename):
    print(f"Error while extracting {filename}, extension of file unknown")


def main():
    files = init_arg_parse()

    ext_to_ft = {
        "BMP": extract_bmp,
        "GIF": extract_gif,
        "PNG": extract_png,
        "JPEG": extract_jpg,
        "UNKNOWN": error_extension,
    }

    for file in files:
        if not os.path.isfile(file):
            continue
        with open(file, "rb") as f:
            data = f.read()
            extension = identify_file_type(data)
            ext_to_ft[extension](data, file)


if __name__ == "__main__":
    main()
