"""Funzioni di utilità per il gioco"""
import pygame
from PIL import Image


def carica_immagine(nome, colore_fallback):
    """Carica un'immagine, se fallisce crea una superficie di colore"""  
    try:
        return pygame.image.load(nome).convert_alpha()
    except:
        s = pygame.Surface((100, 100))
        s.fill(colore_fallback)
        return s


def estrai_frames_gif(percorso, larghezza_desiderata):
    """Estrae tutti i frame da una GIF e li ridimensiona"""
    frames = []
    try:
        with Image.open(percorso) as img:
            w_orig, h_orig = img.size
            ratio = h_orig / w_orig
            nuova_dim = (larghezza_desiderata, int(larghezza_desiderata * ratio))
            for i in range(img.n_frames):
                img.seek(i)
                f = img.convert("RGBA")
                p_img = pygame.image.fromstring(f.tobytes(), img.size, "RGBA")
                frames.append(pygame.transform.scale(p_img, nuova_dim))
    except: 
        print(f"Impossibile caricare la GIF: {percorso}")
    return frames


def crea_superficie_luce(raggio):
    """Crea una superficie circolare per l'effetto luce"""
    superficie = pygame.Surface((raggio * 2, raggio * 2), pygame.SRCALPHA)
    for r in range(raggio, 0, -1):
        alpha = int(255 * (r / raggio)) 
        pygame.draw.circle(superficie, (0, 0, 0, alpha), (raggio, raggio), r)
    return superficie
