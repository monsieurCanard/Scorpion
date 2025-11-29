# Documentation Complète sur le Format PNG

## Table des Matières
1. [Introduction au Format PNG](#introduction-au-format-png)
2. [Structure Générale d'un Fichier PNG](#structure-générale-dun-fichier-png)
3. [Les Chunks (Blocs de Données)](#les-chunks-blocs-de-données)
4. [Spécifications Techniques Détaillées](#spécifications-techniques-détaillées)

---

## Introduction au Format PNG

**PNG** (Portable Network Graphics) est un format d'image ouvert créé pour remplacer le format GIF. Il est particulièrement apprécié pour sa compression sans perte et sa gestion avancée de la transparence.

### Caractéristiques Principales
- **Compression sans perte** : Utilise l'algorithme DEFLATE (combinaison de LZ77 et Huffman).
- **Transparence Alpha** : Supporte 256 niveaux de transparence (contrairement au GIF qui n'en a qu'un).
- **Couleurs** : Supporte le TrueColor (jusqu'à 48 bits) et l'échelle de gris (jusqu'à 16 bits).
- **Correction Gamma** : Permet d'ajuster la luminosité selon l'écran.

### Avantages
- Qualité d'image parfaite (pas de perte de données).
- Transparence progressive (canal Alpha).
- Format libre de droits (open source).

### Limitations
- Taille de fichier souvent plus grande que le JPEG pour les photos.
- Ne supporte pas les animations (contrairement au GIF ou APNG).

---

## Structure Générale d'un Fichier PNG

Un fichier PNG commence toujours par une signature fixe, suivie d'une série de blocs appelés **Chunks**.

```
┌─────────────────────────────────────┐
│ Signature PNG (8 bytes)             │
├─────────────────────────────────────┤
│ Chunk IHDR (Header Image)           │
├─────────────────────────────────────┤
│ Autres Chunks (PLTE, tRNS, etc.)    │
├─────────────────────────────────────┤
│ Chunk IDAT (Données de l'image)     │
│ (Peut être divisé en plusieurs)     │
├─────────────────────────────────────┤
│ Chunk IEND (Fin du fichier)         │
└─────────────────────────────────────┘
```

---

## Les Chunks (Blocs de Données)

Chaque chunk suit une structure identique de 4 parties :

| Partie | Taille | Description |
|--------|--------|-------------|
| **Length** | 4 bytes | Taille des données (Data) uniquement. |
| **Type**   | 4 bytes | Code ASCII de 4 lettres (ex: "IHDR"). |
| **Data**   | Variable| Les données du chunk (peut être vide). |
| **CRC**    | 4 bytes | Contrôle de redondance cyclique (vérification d'erreurs). |

### Types de Chunks Importants

1. **Critiques** (Obligatoires pour lire l'image)
   - `IHDR` : En-tête (dimensions, profondeur, type de couleur). Doit être le premier.
   - `PLTE` : Palette de couleurs (obligatoire pour les images indexées).
   - `IDAT` : Données de l'image compressées.
   - `IEND` : Marque la fin du fichier.

2. **Auxiliaires** (Optionnels)
   - `tEXt` : Texte (titre, auteur, description).
   - `gAMA` : Valeur gamma.
   - `pHYs` : Dimensions physiques des pixels (DPI).

---

## Spécifications Techniques Détaillées

### 1. Signature PNG (8 bytes)

Tous les fichiers PNG commencent par ces 8 octets hexadécimaux :

`89 50 4E 47 0D 0A 1A 0A`

- `89` : Bit haut mis à 1 (détection 8-bit).
- `50 4E 47` : "PNG" en ASCII.
- `0D 0A` : Retour à la ligne DOS (CRLF) pour détecter les conversions automatiques.
- `1A` : Caractère de fin de fichier DOS (EOF).
- `0A` : Retour à la ligne Unix (LF).

### 2. Chunk IHDR (Image Header)

C'est toujours le premier chunk après la signature. Il fait 13 bytes de données.

| Offset | Taille | Description |
|--------|--------|-------------|
| 0-3    | 4 bytes | Largeur (Width) en pixels |
| 4-7    | 4 bytes | Hauteur (Height) en pixels |
| 8      | 1 byte  | Profondeur de bits (Bit Depth) |
| 9      | 1 byte  | Type de couleur (Color Type) |
| 10     | 1 byte  | Méthode de compression (toujours 0) |
| 11     | 1 byte  | Méthode de filtrage (toujours 0) |
| 12     | 1 byte  | Méthode d'entrelacement (0 ou 1) |

#### Types de Couleur (Byte 9)
- `0` : Échelle de gris
- `2` : TrueColor (RGB)
- `3` : Couleurs indexées (Palette)
- `4` : Échelle de gris avec Alpha
- `6` : TrueColor avec Alpha (RGBA)

### 3. Chunk IDAT (Image Data)

Contient les données de l'image filtrées et compressées.
- Un fichier peut contenir plusieurs chunks IDAT consécutifs.
- Ils doivent être concaténés pour former le flux de données complet compressé (zlib).

### 4. Chunk IEND (Image End)

Marque la fin du fichier. Il ne contient pas de données.
Sa structure est toujours :
`00 00 00 00 49 45 4E 44 AE 42 60 82`
(Taille 0, Type "IEND", CRC).
