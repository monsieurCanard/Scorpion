import argparse
from gif_extractor import GifExtractor


def init_arg_parse():
    parser = argparse.ArgumentParser(
        description="Analyse and extract metadata from file(s)"
    )
    parser.add_argument("files", nargs="+", help="Un ou plusieurs fichiers a analyser")

    args = parser.parse_args()
    return args.files


def main():
    files = init_arg_parse()
    for file in files:
        with open(file, "rb") as f:
            data = f.read()
            extractor = GifExtractor(data, file)
            extractor.run()


if __name__ == "__main__":
    main()
