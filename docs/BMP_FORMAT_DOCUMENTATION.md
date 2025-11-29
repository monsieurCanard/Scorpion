# Documentation Complète sur le Format BMP

## Table des Matières
1. [Introduction au Format BMP](#introduction-au-format-bmp)
2. [Structure Générale d'un Fichier BMP](#structure-générale-dun-fichier-bmp)
3. [En-têtes (Headers)](#en-têtes-headers)
4. [Spécifications Techniques Détaillées](#spécifications-techniques-détaillées)

---

## Introduction au Format BMP

**BMP** (Bitmap Image File) est un format d'image matricielle développé par Microsoft pour Windows. C'est un format très simple, généralement non compressé, qui stocke les pixels directement.

### Caractéristiques Principales
- **Non compressé** : La plupart des BMP stockent les pixels bruts (fichiers lourds).
- **Structure simple** : Facile à lire et à écrire par des programmes simples.
- **Little-endian** : Les nombres entiers sont stockés avec l'octet de poids faible en premier (standard Intel/Windows).
- **Stockage inversé** : Les pixels sont souvent stockés de bas en haut (Bottom-up).

### Avantages
- Très simple à décoder (pas d'algorithme complexe).
- Qualité parfaite (sans perte).
- Rapide à charger en mémoire (pas de décompression).

### Limitations
- Taille de fichier énorme comparée à PNG ou JPEG.
- Pas de support standardisé pour les métadonnées complexes (Exif, etc.).
- Peu utilisé sur le web à cause du poids.

---

## Structure Générale d'un Fichier BMP

Un fichier BMP est composé de 4 parties principales :

```
┌─────────────────────────────────────┐
│ BMP File Header (14 bytes)          │
│ (Signature, Taille fichier, Offset) │
├─────────────────────────────────────┤
│ DIB Header (Info Header)            │
│ (Largeur, Hauteur, Couleurs...)     │
├─────────────────────────────────────┤
│ Color Table (Palette)               │
│ (Optionnel, pour images <= 8 bits)  │
├─────────────────────────────────────┤
│ Pixel Data (Bitmap Data)            │
│ (Les pixels de l'image)             │
└─────────────────────────────────────┘
```

---

## En-têtes (Headers)

### 1. BMP File Header (14 bytes)

Sert à identifier le fichier.

| Offset | Taille | Champ | Description |
|--------|--------|-------|-------------|
| 0      | 2 bytes| **Signature** | Toujours `BM` (0x42 0x4D) pour Windows. |
| 2      | 4 bytes| **FileSize** | Taille totale du fichier en octets. |
| 6      | 4 bytes| Réservé | Toujours 0 (dépend de l'application). |
| 10     | 4 bytes| **DataOffset**| Adresse où commencent les données de l'image (pixels). |

### 2. DIB Header (Device Independent Bitmap)

Contient les détails de l'image. Il existe plusieurs versions, mais la plus courante est `BITMAPINFOHEADER` (40 bytes).

| Offset | Taille | Champ | Description |
|--------|--------|-------|-------------|
| 14     | 4 bytes| **HeaderSize** | Taille de ce header (souvent 40). |
| 18     | 4 bytes| **Width** | Largeur de l'image en pixels. |
| 22     | 4 bytes| **Height** | Hauteur de l'image. (Si positif: bas-vers-haut). |
| 26     | 2 bytes| Planes | Toujours 1. |
| 28     | 2 bytes| **BitCount** | Bits par pixel (1, 4, 8, 16, 24, 32). |
| 30     | 4 bytes| Compression | 0 = Pas de compression (BI_RGB). |
| 34     | 4 bytes| ImageSize | Taille des données pixels (peut être 0 si non compressé). |
| 38     | 4 bytes| XPixelsPerM | Résolution horizontale (pixels/mètre). |
| 42     | 4 bytes| YPixelsPerM | Résolution verticale. |
| 46     | 4 bytes| ColorsUsed | Nombre de couleurs dans la palette. |
| 50     | 4 bytes| ColorsImp | Nombre de couleurs importantes. |

---

## Spécifications Techniques Détaillées

### Stockage des Pixels (Pixel Data)

1. **Ordre des couleurs** :
   En 24 bits (le plus courant), les pixels sont stockés en **BGR** (Bleu, Vert, Rouge) et non RGB.
   - Byte 0 : Bleu
   - Byte 1 : Vert
   - Byte 2 : Rouge

2. **Padding (Alignement)** :
   Chaque ligne de pixels (scanline) doit avoir une taille multiple de **4 octets**.
   Si une ligne fait 10 pixels de large en 24 bits (3 bytes/pixel) :
   - Taille réelle : 10 * 3 = 30 bytes.
   - Multiple de 4 supérieur : 32 bytes.
   - Padding : On ajoute 2 octets de remplissage (0x00) à la fin de chaque ligne.

3. **Orientation** :
   Si la **Hauteur** est positive (cas standard), l'image est stockée **à l'envers** : la première ligne de données correspond au bas de l'image.
   Si la Hauteur est négative, l'image est stockée de haut en bas.

### Exemple de calcul de taille
Pour une image 100x100 en 24 bits :
- Taille ligne = 100 * 3 = 300 bytes.
- 300 est divisible par 4 ? Oui. Pas de padding.
- Taille données = 300 * 100 = 30,000 bytes.
- Taille fichier = 14 (Header) + 40 (Info) + 30,000 = 30,054 bytes.
