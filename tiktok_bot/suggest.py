import requests
import json
import os

API_KEY = "d00d07b8bf1de75485e5258ca7ddff49"
BASE_URL = "http://ws.audioscrobbler.com/2.0/"
HISTORY_FILE = "history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def get_top_tracks():
    params = {
        "method": "chart.gettoptracks",
        "api_key": API_KEY,
        "format": "json",
        "limit": 50  # on prend plus pour avoir assez après filtrage
    }
    r = requests.get(BASE_URL, params=params)
    tracks = r.json()["tracks"]["track"]
    return tracks

def filter_new(tracks, history):
    already_done = {(t["name"].lower(), t["artist"].lower()) for t in history}
    return [t for t in tracks if (t["name"].lower(), t["artist"]["name"].lower()) not in already_done]

def display_tracks(tracks):
    print("\n Sons disponibles  :\n")
    for i, track in enumerate(tracks):
        print(f"{i+1}. {track['name']} — {track['artist']['name']}")
    print()

def choose_tracks(tracks):
    print("Entre les numéros des sons que tu veux (ex: 1,3,7) :")
    raw = input("> ")
    indices = [int(x.strip()) - 1 for x in raw.split(",")]
    return [tracks[i] for i in indices if 0 <= i < len(tracks)]

# Main
history = load_history()
tracks = get_top_tracks()
new_tracks = filter_new(tracks, history)

if not new_tracks:
    print("Tous les sons ont déjà été utilisés !")
else:
    display_tracks(new_tracks)
    chosen = choose_tracks(new_tracks)

    print(f"\nTu as choisi {len(chosen)} sons :")
    for t in chosen:
        print(f"  - {t['name']} — {t['artist']['name']}")

    # Ajoute à l'historique
    for t in chosen:
        history.append({
            "name": t["name"],
            "artist": t["artist"]["name"]
        })
    save_history(history)

    # Sauvegarde les choix pour la suite
    with open("chosen_tracks.json", "w") as f:
        json.dump(chosen, f, indent=2)

    print("\nChoix sauvegardé ✅")
    print(f"📚 Historique total : {len(history)} sons")