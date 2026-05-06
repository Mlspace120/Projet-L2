import json
import os
import random
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy import VideoClip, AudioFileClip

os.makedirs("videos", exist_ok=True)

with open("chosen_tracks.json", "r") as f:
    tracks = json.load(f)

W, H = 512, 912
DURATION = 30
FPS = 30

def get_random_background():
    backgrounds = [f for f in os.listdir("backgrounds") if f.endswith((".jpg", ".png", ".jpeg"))]
    return random.choice(backgrounds)

def make_frame(t, bg_array, cover_array, name, artist):
    bg = Image.fromarray(bg_array).resize((W, H), Image.LANCZOS)

    # Overlay sombre
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 120))
    bg = bg.convert("RGBA")
    bg = Image.alpha_composite(bg, overlay).convert("RGB")

    # Pochette
    cover_size = 280
    cover = Image.fromarray(cover_array).resize((cover_size, cover_size), Image.LANCZOS)
    cx = (W - cover_size) // 2
    cy = H // 4 - cover_size // 2
    bg.paste(cover, (cx, cy))

    draw = ImageDraw.Draw(bg)
    try:
        font_title = ImageFont.truetype("arial.ttf", 32)
        font_artist = ImageFont.truetype("arial.ttf", 24)
    except:
        font_title = ImageFont.load_default()
        font_artist = ImageFont.load_default()

    ty = H * 2 // 3 + 20
    draw.text((W//2 + 1, ty + 1), name, font=font_title, fill=(0,0,0), anchor="mm")
    draw.text((W//2, ty), name, font=font_title, fill=(255,255,255), anchor="mm")

    ay = ty + 50
    draw.text((W//2 + 1, ay + 1), artist, font=font_artist, fill=(0,0,0), anchor="mm")
    draw.text((W//2, ay), artist, font=font_artist, fill=(200,200,200), anchor="mm")

    return np.array(bg)

print("Appuie sur Ctrl+C pour arreter la generation\n")

try:
    for track in tracks:
        name = track["name"]
        artist = track["artist"]["name"]
        safe_name = f"{artist} - {name}".replace("/", "-").replace(":", "-")

        preview_path = os.path.join("previews", f"{safe_name}.mp3")
        cover_path = os.path.join("covers", f"{safe_name}.jpg")
        output_path = os.path.join("videos", f"{safe_name}.mp4")

        if not os.path.exists(preview_path):
            print(f"Preview manquant : {safe_name}")
            continue
        if not os.path.exists(cover_path):
            print(f"Pochette manquante : {safe_name}")
            continue
        if os.path.exists(output_path):
            print(f"Deja fait : {safe_name}")
            continue

        print(f"Assemblage : {name} - {artist}")

        bg_file = get_random_background()
        bg = Image.open(os.path.join("backgrounds", bg_file)).convert("RGB")
        bg_array = np.array(bg)

        cover = Image.open(cover_path).convert("RGB")
        cover_array = np.array(cover)

        def frame_maker(t):
            return make_frame(t, bg_array, cover_array, name, artist)

        # Volume a 50%
        audio = AudioFileClip(preview_path).with_duration(DURATION)
        audio = audio.with_volume_scaled(0.1)

        clip = VideoClip(frame_maker, duration=DURATION)
        clip = clip.with_audio(audio)
        clip.write_videofile(output_path, fps=FPS, codec="libx264", audio_codec="aac")
        print(f"Video sauvegardee : {output_path}\n")

except KeyboardInterrupt:
    print("\nGeneration arretee proprement !")

print("Toutes les videos sont pretes !")