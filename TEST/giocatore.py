import pygame
from museEEG import MuseEEG

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
        self.direzione = -1
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
            self.direzione = 3
        elif tasti_premuti[pygame.K_UP]:
            self.direzione = 2
        elif tasti_premuti[pygame.K_LEFT]:
            self.direzione = 1
        elif tasti_premuti[pygame.K_DOWN]:
            self.direzione = 0


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
