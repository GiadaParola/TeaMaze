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


def crea_superficie_luce(raggio, raggio_inizio_sfumatura=None):
    """Crea una maschera luce: zona centrale libera e sfumatura fino al nero pieno."""
    raggio = max(1, int(raggio))
    if raggio_inizio_sfumatura is None:
        raggio_inizio_sfumatura = int(raggio * 0.6)
    raggio_inizio_sfumatura = max(0, min(int(raggio_inizio_sfumatura), raggio))

    superficie = pygame.Surface((raggio * 2, raggio * 2), pygame.SRCALPHA)
    cx, cy = raggio, raggio

    # Dal centro fino a raggio_inizio_sfumatura non c'e oscurita' (alpha 0),
    # poi la sfumatura cresce fino a 255 al bordo esterno.
    for rr in range(raggio, 0, -1):
        if rr <= raggio_inizio_sfumatura:
            alpha = 0
        else:
            ampiezza = max(1, raggio - raggio_inizio_sfumatura)
            alpha = int(255 * (rr - raggio_inizio_sfumatura) / ampiezza)
        pygame.draw.circle(superficie, (0, 0, 0, alpha), (cx, cy), rr)
    return superficie
