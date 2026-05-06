import requests
import json
import os

API_KEY = "d00d07b8bf1de75485e5258ca7ddff49"
BASE_URL = "http://ws.audioscrobbler.com/2.0/"

os.makedirs("covers", exist_ok=True)

def get_cover_lastfm(artist, name):
    params = {
        "method": "track.getInfo",
        "api_key": API_KEY,
        "artist": artist,
        "track": name,
        "format": "json"
    }
    r = requests.get(BASE_URL, params=params)
    data = r.json()
    try:
        images = data["track"]["album"]["image"]
        url = images[-1]["#text"]
        return url if url else None
    except (KeyError, IndexError):
        return None

def get_cover_itunes(artist, name):
    query = f"{artist} {name}"
    r = requests.get("https://itunes.apple.com/search", params={
        "term": query,
        "media": "music",
        "limit": 1
    })
    results = r.json().get("results", [])
    if results:
        # Prend la pochette en haute qualité (600x600)
        return results[0]["artworkUrl100"].replace("100x100", "600x600")
    return None

with open("chosen_tracks.json", "r") as f:
    tracks = json.load(f)

for track in tracks:
    name = track["name"]
    artist = track["artist"]["name"]
    safe_name = f"{artist} - {name}".replace("/", "-").replace(":", "-")
    filename = os.path.join("covers", f"{safe_name}.jpg")

    if os.path.exists(filename):
        print(f"Déjà téléchargée : {safe_name}")
        continue

    # Essaie Last.fm d'abord
    cover_url = get_cover_lastfm(artist, name)

    # Fallback iTunes
    if not cover_url:
        print(f"Fallback iTunes pour {name} — {artist}")
        cover_url = get_cover_itunes(artist, name)

    if cover_url:
        img_data = requests.get(cover_url).content
        with open(filename, "wb") as f:
            f.write(img_data)
        print(f" Pochette téléchargée : {safe_name}")
    else:
        print(f" Introuvable partout : {name} — {artist}")