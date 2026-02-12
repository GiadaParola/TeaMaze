import pygame
from museEEG import MuseEEG

class Giocatore:
    """Classe che rappresenta il giocatore controllabile"""
    def __init__(self, x, y, img_statica, frames_animati=None):
        self.frames = frames_animati
        self.img_fermo = self.frames[0] if frames_animati else pygame.transform.scale(img_statica, (28, 28))
        self.image = self.img_fermo
        self.rect = self.image.get_rect(topleft=(x, y))
        self.index_frame = 0
        self.sta_muovendo = False
        self.vel = 0
        self.direzione = -1

        # --- EEG ---
        self.eeg = MuseEEG()
        if self.eeg.connect():
            print("Muse EEG pronto")
        else:
            print("Muse EEG non trovato, useremo valori simulati")

    def muovi(self, tasti_premuti, muri):
        """Muove il giocatore controllato da EEG Beta e tastiera"""

        # --- Aggiorna buffer EEG ---
        self.eeg.update()
        band_powers = self.eeg.get_band_powers()

        # --- Soglia Beta ---
        soglia_beta = 0.2
        beta = band_powers.get('Beta', 0)
        print(f"Beta: {beta:.3f}")
        vel = 2 if beta > soglia_beta else 0

        # --- Cambia direzione con i tasti ---
        if tasti_premuti[pygame.K_RIGHT]:
            self.direzione = (self.direzione + 1) % 4

        # --- Calcola dx, dy ---
        dx = dy = 0
        if self.direzione == 0:  # giù
            dy = vel
        elif self.direzione == 1:  # sinistra
            dx = -vel
        elif self.direzione == 2:  # su
            dy = -vel
        elif self.direzione == 3:  # destra
            dx = vel

        # Aggiorna stato movimento
        self.sta_muovendo = (dx != 0 or dy != 0)

        # --- Movimento con collisioni ---
        self.rect.x += dx
        for m in muri:
            if self.rect.colliderect(m):
                if dx > 0:
                    self.rect.right = m.left
                elif dx < 0:
                    self.rect.left = m.right

        self.rect.y += dy
        for m in muri:
            if self.rect.colliderect(m):
                if dy > 0:
                    self.rect.bottom = m.top
                elif dy < 0:
                    self.rect.top = m.bottom

    def aggiorna(self):
        """Aggiorna animazione"""
        if self.sta_muovendo and self.frames:
            self.index_frame += 0.1
            if self.index_frame >= len(self.frames):
                self.index_frame = 0
            self.image = self.frames[int(self.index_frame)]
        else:
            self.image = self.img_fermo

    def draw(self, surface, camera_pos):
        """Disegna il giocatore adattando alla camera"""
        self.aggiorna()
        surface.blit(self.image, (self.rect.x - camera_pos[0], self.rect.y - camera_pos[1]))
