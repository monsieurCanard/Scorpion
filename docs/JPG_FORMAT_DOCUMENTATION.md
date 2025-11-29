# Documentation Complète sur le Format JPEG

## Table des Matières
1. [Introduction au Format JPEG](#introduction-au-format-jpeg)
2. [Structure Générale d'un Fichier JPEG](#structure-générale-dun-fichier-jpeg)
3. [Les Marqueurs (Markers)](#les-marqueurs-markers)
4. [Spécifications Techniques Détaillées](#spécifications-techniques-détaillées)

---

## Introduction au Format JPEG

**JPEG** (Joint Photographic Experts Group) est le format standard pour la photographie numérique. Il utilise une compression avec perte conçue pour réduire la taille des fichiers d'images réalistes (photos) sans perte visible majeure pour l'œil humain.

### Caractéristiques Principales
- **Compression avec perte** : Supprime les détails haute fréquence que l'œil voit moins bien.
- **Espace colorimétrique** : Utilise souvent YCbCr (Luminance/Chrominance) au lieu de RGB.
- **Blocs 8x8** : L'image est découpée en blocs de 8x8 pixels pour la compression (DCT).

### Avantages
- Taux de compression très élevé (fichiers légers).
- Idéal pour les photographies et images complexes.
- Standard universel supporté par tous les appareils.

### Limitations
- Perte de qualité à chaque ré-enregistrement (génération d'artefacts).
- Pas de support de la transparence.
- Moins adapté pour les dessins au trait, textes ou icônes (bruit visible autour des bords nets).

---

## Structure Générale d'un Fichier JPEG

Un fichier JPEG est un flux de données délimité par des marqueurs commençant par `0xFF`.

```
┌─────────────────────────────────────┐
│ SOI (Start of Image)                │
├─────────────────────────────────────┤
│ APPn (Métadonnées: JFIF, Exif...)   │
├─────────────────────────────────────┤
│ DQT (Tables de Quantification)      │
├─────────────────────────────────────┤
│ SOF (Start of Frame - Dimensions)   │
├─────────────────────────────────────┤
│ DHT (Tables de Huffman)             │
├─────────────────────────────────────┤
│ SOS (Start of Scan)                 │
├─────────────────────────────────────┤
│ Données de l'image compressée       │
│ (Scan Data)                         │
├─────────────────────────────────────┤
│ EOI (End of Image)                  │
└─────────────────────────────────────┘
```

---

## Les Marqueurs (Markers)

Un marqueur est composé de 2 octets : `0xFF` suivi d'un octet identifiant le type.
La plupart des marqueurs sont suivis de la taille du segment (2 bytes) et des données.

| Marqueur | Nom | Description |
|----------|-----|-------------|
| `FF D8`  | **SOI** | Start of Image (Début du fichier). Pas de données après. |
| `FF E0`  | **APP0**| Application 0 (souvent JFIF). |
| `FF E1`  | **APP1**| Application 1 (souvent Exif). |
| `FF DB`  | **DQT** | Define Quantization Table (Tables de compression). |
| `FF C0`  | **SOF0**| Start of Frame (Baseline DCT). Contient largeur/hauteur. |
| `FF C4`  | **DHT** | Define Huffman Table. |
| `FF DA`  | **SOS** | Start of Scan (Début des données image). |
| `FF D9`  | **EOI** | End of Image (Fin du fichier). Pas de données après. |

---

## Spécifications Techniques Détaillées

### 1. SOI (Start of Image)
- **Valeur** : `FF D8`
- Indique le début du flux JPEG. Obligatoire.

### 2. APP0 (JFIF Header)
Souvent le premier segment après SOI pour assurer la compatibilité.
- **Marqueur** : `FF E0`
- **Identifiant** : "JFIF\0"
- Contient la version JFIF, la densité de pixels (DPI), etc.

### 3. SOF0 (Start of Frame - Baseline)
C'est ici que se trouvent les informations essentielles sur l'image.
- **Marqueur** : `FF C0`
- **Structure** :
  - Longueur du segment (2 bytes)
  - Précision (1 byte) : généralement 8 bits.
  - **Hauteur** de l'image (2 bytes).
  - **Largeur** de l'image (2 bytes).
  - Nombre de composants (1 byte) : 1 (Gris) ou 3 (YCbCr).

### 4. SOS (Start of Scan)
- **Marqueur** : `FF DA`
- Marque la fin des en-têtes et le début des données compressées de l'image.
- Tout ce qui suit ce marqueur est le flux binaire de l'image (jusqu'au marqueur EOI).
- **Note** : Si le byte `0xFF` apparaît dans les données compressées, il est suivi de `0x00` (byte stuffing) pour ne pas être confondu avec un marqueur.

### 5. EOI (End of Image)
- **Valeur** : `FF D9`
- Indique la fin du fichier.
