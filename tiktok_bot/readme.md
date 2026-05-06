# Auto Music Video Generator

Automatise la création de vidéos courtes (TikTok / Reels) à partir de musiques populaires.

---

## Overview

Ce projet prend des sons tendance et génère automatiquement des vidéos prêtes à être postées.

Pipeline :

```
Last.fm → sélection → YouTube → analyse audio → preview → cover → vidéo
```

---

## Features

* récupération des sons populaires via Last.fm
* sélection manuelle via terminal
* téléchargement audio via YouTube
* détection du moment le plus pertinent (énergie + rythme)
* génération d’extraits de 30 secondes
* récupération automatique des pochettes
* génération de vidéos verticales
* historique pour éviter les doublons

---

## Project Structure

```
.
├── backgrounds/        # images de fond (obligatoire)
├── covers/             # pochettes
├── previews/           # extraits audio
├── videos/             # vidéos finales
├── audio/              # audios complets (temp)
├── chosen_tracks.json
├── history.json
├── script.py
```

---

## Installation


### 1. Dependencies

```bash
pip install yt-dlp librosa numpy soundfile requests pillow moviepy
```

### 2. FFmpeg

Requis pour audio/vidéo.

Linux :

```bash
sudo apt install ffmpeg
```

Windows : installer FFmpeg et l’ajouter au PATH.

---

## Configuration

Dans le script :

```python
API_KEY = "YOUR_LASTFM_API_KEY"
```

[https://www.last.fm/api](https://www.last.fm/api)

---

## Usage

### Step 1 — Fetch tracks

Le script récupère les sons populaires et les affiche.

### Step 2 — Select tracks

Entrer les numéros :

```
1,3,7
```

### Step 3 — Processing

Le script fait tout :

* téléchargement audio
* analyse du meilleur moment
* création preview
* téléchargement cover
* génération vidéo

---

## How it works

### Audio analysis

* RMS (énergie du signal)
* détection des beats (librosa)
* score = `0.7 * energy + 0.3 * beat_density`
* fenêtre glissante de 30 secondes

### Video generation

* format vertical : 512x912
* fond aléatoire
* overlay sombre
* pochette centrée
* titre + artiste
* volume réduit

---

## Requirements

* dossier `backgrounds/` avec images
* connexion internet
* FFmpeg installé

---

## Limitations

* dépend de YouTube pour l’audio
* qualité variable selon la source
* certaines pochettes peuvent manquer
* pas optimisé pour gros volumes

---

## Possible improvements

* sous-titres automatiques
* génération de captions
* upload automatique
* meilleur scoring audio (ML)
* UI / dashboard

---

## Notes

* les audios complets sont supprimés après traitement
* fallback iTunes si Last.fm échoue
