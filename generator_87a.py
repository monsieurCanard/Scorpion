from PIL import Image

# Crée une image simple
im = Image.new("RGB", (2, 2), color=(0, 255, 0))

# Ajouter un commentaire
im.info['comment'] = b"Created by ChatGPT GIF87a test"

# Sauver en GIF89a par défaut
im.save("test_87a.gif")

# Modifier le header pour forcer GIF87a
with open("test_87a.gif", "r+b") as f:
    f.write(b"GIF87a")  # Remplace les 6 premiers octets (Header)
