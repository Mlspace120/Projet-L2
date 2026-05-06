import json
import os
import yt_dlp
import librosa
import numpy as np
import soundfile as sf

os.makedirs("audio", exist_ok=True)
os.makedirs("previews", exist_ok=True)

with open("chosen_tracks.json", "r") as f:
    tracks = json.load(f)

def find_best_moment(filepath, duration=30):
    """Trouve la partie la plus énergique du son"""
    print(f"   Analyse du meilleur moment...")
    y, sr = librosa.load(filepath, mono=True)
    
    # Calcule l'énergie RMS sur des fenêtres glissantes
    frame_length = int(sr * duration)
    hop = int(sr * 1)  # glisse de 1 seconde en 1 seconde
    
    best_start = 0
    best_energy = 0
    
    for start in range(0, len(y) - frame_length, hop):
        segment = y[start:start + frame_length]
        # Énergie RMS + boost des fréquences mid (chorus)
        rms = np.sqrt(np.mean(segment**2))
        # Détecte aussi les beats
        tempo, beats = librosa.beat.beat_track(y=segment, sr=sr)
        beat_strength = len(beats) / duration
        score = rms * 0.7 + beat_strength * 0.3
        
        if score > best_energy:
            best_energy = score
            best_start = start
    
    best_time = best_start / sr
    print(f"   Meilleur moment trouvé à {best_time:.1f}s")
    return best_time

with open("chosen_tracks.json", "r") as f:
    tracks = json.load(f)

for track in tracks:
    name = track["name"]
    artist = track["artist"]["name"]
    query = f"{artist} {name} official audio"
    safe_name = f"{artist} - {name}".replace("/", "-").replace(":", "-")
    full_path = os.path.join("audio", f"{safe_name}.mp3")
    preview_path = os.path.join("previews", f"{safe_name}.mp3")

    if os.path.exists(preview_path):
        print(f"⏭️ Déjà traité : {safe_name}")
        continue

    # Télécharge le son complet
    if not os.path.exists(full_path):
        print(f"⬇️ Téléchargement : {name} — {artist}")
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join("audio", safe_name),
            "quiet": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(f"ytsearch1:{query}", download=True)

    # Trouve le meilleur moment
    best_time = find_best_moment(full_path, duration=30)

    # Coupe le preview
    y, sr = librosa.load(full_path, offset=best_time, duration=30, mono=False)
    if y.ndim == 1:
        y = np.expand_dims(y, axis=0)
    sf.write(preview_path, y.T, sr, format="mp3")
    print(f" Preview sauvegardé : {safe_name}.mp3\n")

print(" Tous les previews sont prêts !")

import shutil
shutil.rmtree("audio")
print(" Audios complets supprimés !")