import pygame

class Giocatore:
    """Classe che rappresenta il giocatore controllabile"""
    def __init__(self, x, y, img_statica, frames_animati=None):
        """Inizializza il giocatore con posizione e immagini"""
        self.frames = frames_animati  # Memorizza i frame animati
        self.img_fermo = self.frames[0] if frames_animati else pygame.transform.scale(img_statica, (28, 28))  # Immagine quando fermo
        self.image = self.img_fermo  # Immagine attuale da disegnare
        self.rect = self.image.get_rect(topleft=(x, y))  # Rettangolo per posizione e collisioni
        self.index_frame = 0  # Indice del frame attuale
        self.sta_muovendo = False  # Flag per sapere se il giocatore si sta muovendo

    def muovi(self, dx, dy, muri):
        """Muove il giocatore e gestisce le collisioni con i muri"""
        self.sta_muovendo = (dx != 0 or dy != 0)  # Aggiorna flag movimento
        self.rect.x += dx  # Muove in orizzontale
        for m in muri:  # Controlla collisioni con ogni muro
            if self.rect.colliderect(m):  # Se collide
                if dx > 0: self.rect.right = m.left  # Se va a destra, fermati al muro sinistro
                if dx < 0: self.rect.left = m.right  # Se va a sinistra, fermati al muro destro
        self.rect.y += dy  # Muove in verticale
        for m in muri:  # Controlla collisioni con ogni muro
            if self.rect.colliderect(m):  # Se collide
                if dy > 0: self.rect.bottom = m.top  # Se va giù, fermati al muro superiore
                if dy < 0: self.rect.top = m.bottom  # Se va su, fermati al muro inferiore

    def aggiorna(self):
        """Aggiorna l'animazione del giocatore"""
        if self.sta_muovendo and self.frames:  # Se si sta muovendo e ha frame animati
            self.index_frame += 0.1  # Incrementa indice frame per l'animazione
            if self.index_frame >= len(self.frames): self.index_frame = 0  # Riavvolgi animazione
            self.image = self.frames[int(self.index_frame)]  # Imposta il frame corrente
        else:
            self.image = self.img_fermo  # Se fermo, usa immagine statica

    def draw(self, surface, camera_pos):
        """Disegna il giocatore sulla screen corretta per la camera"""
        self.aggiorna()  # Aggiorna stato animazione
        surface.blit(self.image, (self.rect.x - camera_pos[0], self.rect.y - camera_pos[1]))  # Disegna adattando alla camera
