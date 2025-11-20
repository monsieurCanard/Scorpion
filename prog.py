def main():
    with open("data/nyan.gif", "rb") as f:
        data = f.read()
        print(f"Read {len(data)} bytes from nyan.gif")

        # Header bytes -> Version of GIF
        # GIF89a (norme de 1989) or GIF87a (norme de 1987)
        header = data[:6]
        print(f"Header bytes: {header}")

        # Lsd bytes -> Logical Screen Descriptor
        # 6-7 : Width (2 bytes)
        # 8-9 : Height (2 bytes)
        # 10   : Packed Fields (1 byte) ( Global Color Table Flag, Color Resolution, Sort Flag, Size of Global Color Table)
        # 11   : Background Color Index (1 byte)
        # 12   : Pixel Aspect Ratio (1 byte)
        lsd = data[6:13]
        print(f"Width: {int.from_bytes(lsd[0:2], 'little')} pixels")
        print(f"Height: {int.from_bytes(lsd[2:4], 'little')} pixels")


if __name__ == "__main__":
    main()
