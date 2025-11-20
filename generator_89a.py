from PIL import Image, GifImagePlugin

# Crée une image 2x2 simple
im = Image.new("RGB", (2, 2), color=(255, 0, 0))

# Ajouter un commentaire
im.info["comment"] = b"Created by ChatGPT on 2025-11-20"

# Ajouter une Application Extension (NETSCAPE2.0 loop)
im.info["loop"] = 0  # 0 = boucle infinie

# Sauver le GIF avec metadata
im.save("test_metadata.gif", save_all=True, append_images=[im], loop=0)
