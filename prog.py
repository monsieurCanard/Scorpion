import argparse

def init_arg_parse():
    parser = argparse.ArgumentParser(description="Analyse and extract metadata from file(s)")
    parser.add_argument(
        'files',
        nargs="+",
        help="Un ou plusieurs fichiers a analyser"
    )

    args = parser.parse_args()
    return args.files

def handle_gif87a(data: bytes, index: int):
    i = index
    while data[i] != 0x3B:  # 0x3B is the GIF file terminator
        # Process GIF87a specific blocks here
        byte = data[i]
        if byte == 0x2C:  # Image Descriptor
            i = skip_image(data, i)
            continue  # Image Descriptor is 10 bytes long
        elif byte == 0x21:  # Extension Introducer
            i = handle_extension(data, i)
        else:
            i += 1
            # Move to the next byte


def read_comment_extension(data: bytes, index: int):
    index += 2  # Skip the label byte

    while data[index] != 0:  # Data Sub-blocks
        block_size = data[index]
        comment_data = data[index + 1 : index + 1 + block_size]
        comment_text = comment_data.decode("ascii", errors="ignore")
        print(f"Comment Extension: {comment_text}")
        index += block_size + 1  # Move to the next sub-block

    index += 1  # Skip the block terminator
    return index  # Return the number of bytes skipped


def handle_extension(data: bytes, index: int):
    label = data[index + 1]

    if label == 0xFE:  # Comment Extension
        return read_comment_extension(data, index)

    elif label == 0xF9:  # Graphic Control Extension (GIF89a)
        index += 2
        block_size = data[index]
        index += 1
        packed = data[index]
        delay = data[index + 1] + (data[index + 2] << 8)
        transparent_index = data[index + 3]
        index += 4
        index += 1  # terminator
        print(f"GCE: Delay={delay} Transparent={transparent_index} Packed={packed}")
        return index
    elif label == 0xFF:
        index += 2
        block_size = data[index]  # should be 11
        index += 1
        app_identifier = data[index : index + block_size]
        index += block_size

        app_data = bytearray()
        while data[index] != 0:
            size = data[index]
            index += 1
            app_data += data[index : index + size]
            index += size
        index += 1  # terminator
        print(f"Application Extension: {app_identifier} Data length={len(app_data)}")
        return index
    else:
        # Skip unknown extensions
        index += 2
        while data[index] != 0:
            block_size = data[index]
            index += 1 + block_size
        index += 1
        return index


def skip_image(data: bytes, index: int):
    if index + 9 >= len(data):
        return len(data)

    packed = data[index + 9]
    local_color_table_flag = (packed & 0b10000000) >> 7
    size_of_lct = packed & 0b00000111

    if local_color_table_flag:
        entries = 2 ** (size_of_lct + 1)
        table_size = 3 * entries
        if index + 10 + table_size >= len(data):
            return len(data)
        index += table_size  # Each color is 3 bytes (RGB)

    index += 10  # Move past Image Descriptor

    if index >= len(data):
        return len(data)

    index += 1  # LZW Minimum Code Size
    if index >= len(data):
        return len(data)

    while data[index] != 0:  # Data Sub-blocks
        block_size = data[index]
        if block_size == 0:
            index += 1
            break
        index += block_size + 1  # Move to the next sub-block

    index += 1  # Skip the block terminator
    return index  # Return the number of bytes skipped

def decode_header(data: bytes):
  # ! Header bytes -> Version of GIF
    # GIF89a (norme de 1989) or GIF87a (norme de 1987)
    header = data[:6]
    version = header[3:].decode("ascii")
    print(f"Signature: {header[:3].decode('ascii')}")
    print(f"Version: {version}")

    # ! Lsd bytes -> Logical Screen Descriptor
    # 6-7 : Width (2 bytes)
    # 8-9 : Height (2 bytes)
    # 10   : Packed Fields (1 byte) ( Global Color Table Flag, Color Resolution, Sort Flag, Size of Global Color Table)
    # 11   : Background Color Index (1 byte)
    # 12   : Pixel Aspect Ratio (1 byte)
    lsd = data[6:13]
    print(f"Width: {int.from_bytes(lsd[0:2], 'little')} pixels")
    print(f"Height: {int.from_bytes(lsd[2:4], 'little')} pixels")

    print("Packed Fields:")
    packed_fields = lsd[4]

    # Global Color Table Flag : 1 bit (1 = global color table is present)
    global_color_table_flag = (packed_fields & 0b10000000) >> 7
    print(f"  Global Color Table Flag: {global_color_table_flag}")

    # Color Resolution : 3 bits (number of bits per primary color - 1)
    print(
        f"  Color Resolution: {((packed_fields & 0b01110000) >> 4) + 1} bits per primary color"
    )

    # Sort Flag : 1 bit (1 = global color table is sorted)
    # Sort Flag : 1 bit (0 = global color table is not sorted)
    print(f"  Sort Flag: {(packed_fields & 0b00001000) >> 3}")
    size_of_gct = packed_fields & 0b00000111

    # Size of Global Color Table : 3 bits (actual size is 2^(N+1))
    print(f"  Size of Global Color Table: {2 ** (size_of_gct + 1)} colors")

    # Background Color Index : 1 byte (index in the global color table)
    # Couleur de fond de l'image
    background_color_index = lsd[5]
    print(f"Background Color Index: {background_color_index}")

    # Pixel Aspect Ratio : 1 byte
    # If not 0, the aspect ratio is (pixel_aspect_ratio + 15) / 64
    # Precise the aspect ratio of the pixels
    pixel_aspect_ratio = lsd[6]
    if pixel_aspect_ratio != 0:
        aspect_ratio = (pixel_aspect_ratio + 15) / 64
        print(f"Pixel Aspect Ratio: {aspect_ratio:.2f}")
    else:
        print("Pixel Aspect Ratio: Not specified")
    start_index = 13
    size = 0
    if global_color_table_flag:
        # ! Global Color Table
        size = 3 * (1 << (size_of_gct + 1))  # Each color is 3 bytes (RGB)
        print(f"Global Color Table Size: {size} bytes")
        gct = data[start_index : start_index + size]
        print(f"Number of differents colors {size // 3}")
        # print("First 3 colors in Global Color Table:")
        # for i in range(size // 3):
        #     r = gct[i * 3]
        #     g = gct[i * 3 + 1]
        #     b = gct[i * 3 + 2]
            # print(f"  Color {i}: R={r} G={g} B={b}")
    return start_index + size

def main():
    files = init_arg_parse()
    for file in files:
        with open(file, "rb") as f:
            index = 0
            data = f.read()
            index = decode_header(data)
            handle_gif87a(data, index)


if __name__ == "__main__":
    main()
