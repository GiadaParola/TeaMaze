#!/usr/bin/env python3
"""Script per generare le GIF direzionali mancanti dal personaggio F"""

from PIL import Image
import os

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")

def flip_gif_frames(input_path, output_path):
    """Crea una versione speculata (flipped) di una GIF"""
    try:
        with Image.open(input_path) as img:
            frames = []
            durations = []
            
            for i in range(img.n_frames):
                img.seek(i)
                frame = img.convert("RGBA")
                # Specchia il frame orizzontalmente
                flipped_frame = frame.transpose(Image.FLIP_LEFT_RIGHT)
                frames.append(flipped_frame)
                
                # Prova a ottenere la durata del frame (se disponibile)
                try:
                    duration = img.info.get('duration', 100)
                    durations.append(duration)
                except:
                    durations.append(100)
            
            # Salva come GIF animata
            if frames:
                frames[0].save(
                    output_path,
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=0
                )
                print(f"✓ Creato: {output_path}")
            return True
    except Exception as e:
        print(f"✗ Errore per {input_path}: {e}")
        return False

# Generiamo giuAnimatoF.gif (speculamento di personaggioFAnimato.gif)
print("Generando GIF direzionali mancanti...")
flip_gif_frames(
    os.path.join(IMG_DIR, "personaggioFAnimato.gif"),
    os.path.join(IMG_DIR, "giuAnimatoF.gif")
)

print("Done!")
