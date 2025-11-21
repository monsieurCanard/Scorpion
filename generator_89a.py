from PIL import Image, GifImagePlugin

# Crée une image 2x2 simple
im = Image.new("RGB", (2, 2), color=(255, 0, 0))

# Ajouter un commentaire
im.info["comment"] = b"Created by ChatGPT on 2025-11-20"

# Ajouter une Application Extension (NETSCAPE2.0 loop)
im.info["loop"] = 0  # 0 = boucle infinie

# Sauver le GIF avec metadata
im.save("test_metadata.gif", save_all=True, append_images=[im], loop=0)


# ✨ Ajouter manuellement une Plain Text Extension
def add_plain_text_extension(
    gif_path: str,
    text: str,
    left: int = 0,
    top: int = 0,
    width: int = 100,
    height: int = 50,
    char_width: int = 8,
    char_height: int = 12,
    fg_color: int = 1,
    bg_color: int = 0,
):
    """
    Injecte une Plain Text Extension dans un GIF existant.

    Args:
        gif_path: Chemin du fichier GIF
        text: Texte à insérer
        left, top: Position du texte (x, y)
        width, height: Dimensions de la zone de texte
        char_width, char_height: Taille des caractères en pixels
        fg_color: Index de couleur du texte dans la palette
        bg_color: Index de couleur du fond dans la palette
    """
    with open(gif_path, "rb") as f:
        data = bytearray(f.read())

    # Trouver où insérer (juste avant le premier Image Descriptor 0x2C)
    insert_pos = data.index(0x2C)

    # Construire la Plain Text Extension
    plain_text_ext = bytearray()

    # Extension Introducer + Label
    plain_text_ext.append(0x21)  # Extension Introducer
    plain_text_ext.append(0x01)  # Plain Text Label

    # Block Size (toujours 12)
    plain_text_ext.append(0x0C)

    # Text Grid Left Position (2 bytes, little-endian)
    plain_text_ext.extend(left.to_bytes(2, "little"))

    # Text Grid Top Position (2 bytes, little-endian)
    plain_text_ext.extend(top.to_bytes(2, "little"))

    # Text Grid Width (2 bytes, little-endian)
    plain_text_ext.extend(width.to_bytes(2, "little"))

    # Text Grid Height (2 bytes, little-endian)
    plain_text_ext.extend(height.to_bytes(2, "little"))

    # Character Cell Width
    plain_text_ext.append(char_width)

    # Character Cell Height
    plain_text_ext.append(char_height)

    # Text Foreground Color Index
    plain_text_ext.append(fg_color)

    # Text Background Color Index
    plain_text_ext.append(bg_color)

    # Plain Text Data (sub-blocks)
    text_bytes = text.encode("ascii", errors="ignore")

    # Découper le texte en blocs de max 255 bytes
    offset = 0
    while offset < len(text_bytes):
        chunk_size = min(255, len(text_bytes) - offset)
        plain_text_ext.append(chunk_size)  # Sub-block size
        plain_text_ext.extend(text_bytes[offset : offset + chunk_size])
        offset += chunk_size

    # Block Terminator
    plain_text_ext.append(0x00)

    # Insérer l'extension dans le GIF
    data[insert_pos:insert_pos] = plain_text_ext

    # Sauvegarder le fichier modifié
    with open(gif_path, "wb") as f:
        f.write(data)

    print(f'✅ Plain Text Extension ajoutée: "{text}"')


# Utilisation
add_plain_text_extension(
    "test_metadata.gif",
    text="Hello from Plain Text Extension!",
    left=10,
    top=20,
    width=200,
    height=50,
    char_width=8,
    char_height=12,
    fg_color=1,  # Index 1 de la palette (probablement blanc)
    bg_color=0,  # Index 0 de la palette (probablement noir)
)

print("✅ GIF créé avec Plain Text Extension: test_metadata.gif")
