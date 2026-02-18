import pygame
import time
from museEEG import MuseEEG
from museGYRO import MuseGYRO

class Giocatore:
    """Classe che rappresenta il giocatore controllabile"""
    def __init__(self, x, y, img_statica, frames_animati=None):
        """Inizializza il giocatore con posizione e immagini"""
        self.frames = frames_animati  # Memorizza i frame animati
        self.img_fermo = self.frames[0] if frames_animati else pygame.transform.scale(img_statica, (28, 28))  # Immagine quando fermo
        self.image = self.img_fermo  # Immagine attuale da disegnare
        
        # Rect di collisione FISSO (28x28) per evitare bug di cambio dimensione
        self.rect = pygame.Rect(x, y, 28, 28)
        self.index_frame = 0  # Indice del frame attuale
        self.sta_muovendo = False  # Flag per sapere se il giocatore si sta muovendo
        self.ultimo_frames = frames_animati  # Memorizza l'ultimo set di frame per rilevare il cambio

        # --- EEG ---
        self.direzione = 0
        self.eeg = MuseEEG()
        if self.eeg.connect():
            print("Muse EEG pronto")
        else:
            print("Muse EEG non trovato, useremo valori simulati")

        # --- Gryo ---
        self.gyro = MuseGYRO()
        if self.gyro.connect():
            print("Muse GYRO pronto")
        else:
            print("Muse GYRO non trovato, useremo valori simulati")


    def muovi(self, muri):
        """Muove il giocatore controllato da EEG Beta e tastiera"""

        # --- Aggiorna buffer EEG ---
        self.eeg.update()
        band_powers = self.eeg.get_band_powers()

        # --- Aggiorna buffer GYRO ---
        self.gyro.update()
        gyro_mean = self.gyro.get_xyz()

        # --- Soglia Beta ---
        soglia_beta = 0.1
        beta = band_powers.get('Beta', 0)
        print(f"Beta: {beta:.3f}")
        vel = 2 if beta > soglia_beta else 0

        # --- Cambia direzione con i tasti ---
        print(f"GYRO: {gyro_mean}")
        soglia = 190
        if gyro_mean["y"] > soglia: #giu
            self.direzione = 0
            time.sleep(1)
        elif gyro_mean["y"] < -soglia: #su
            self.direzione = 2
            time.sleep(1)
        elif gyro_mean["z"] > soglia: #sx
            self.direzione = 1
            time.sleep(1)
        elif gyro_mean["z"] < -soglia: #dx
            self.direzione = 3
            time.sleep(1)


        # --- Calcola dx, dy ---
        dx = dy = 0
        if self.direzione == 0:  # giù
            dy = vel
        elif self.direzione == 1:  # sx
            dx = -vel
        elif self.direzione == 2:  # su
            dy = -vel
        elif self.direzione == 3:  # dx
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
        """Aggiorna l'animazione del giocatore"""
        # Se i frame sono stati cambiati, reset dell'indice
        if self.frames != self.ultimo_frames:
            self.index_frame = 0
            self.ultimo_frames = self.frames
            if self.frames and len(self.frames) > 0:
                self.img_fermo = self.frames[0]
        
        if self.sta_muovendo and self.frames:  # Se si sta muovendo e ha frame animati
            self.index_frame += 0.1  # Incrementa indice frame per l'animazione
            if self.index_frame >= len(self.frames): self.index_frame = 0  # Riavvolgi animazione
            self.image = self.frames[int(self.index_frame)]  # Imposta il frame corrente
        else:
            self.image = self.img_fermo  # Se fermo, usa immagine statica

    def draw(self, surface, camera_pos):
        """Disegna il giocatore sulla screen corretta per la camera"""
        self.aggiorna()  # Aggiorna stato animazione
        # Disegna l'immagine centrata sul rect di collisione fisso
        img_rect = self.image.get_rect(center=self.rect.center)
        surface.blit(self.image, (img_rect.x - camera_pos[0], img_rect.y - camera_pos[1]))
