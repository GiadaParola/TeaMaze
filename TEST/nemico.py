import pygame
import random

class Nemico:
    """Classe che rappresenta il nemico che si muove in modo autonomo"""
    def __init__(self, x, y, img):
        """Inizializza il nemico con posizione e immagine"""
        self.image = pygame.transform.scale(img, (35, 35))  # Ridimensiona immagine a 35x35 pixel
        self.rect = self.image.get_rect(topleft=(x, y))  # Crea rettangolo per posizione
        self.dir = [random.choice([-1, 1]), random.choice([-1, 1])]  # Direzione casuale X e Y (-1 o 1) 

    def muovi_auto(self, muri):
        """Muove il nemico automaticamente rimbalzando sui muri"""
        self.rect.x += self.dir[0]  # Muove in orizzontale nella direzione corrente
        for m in muri:  # Controlla collisioni con ogni muro
            if self.rect.colliderect(m):  # Se collide con un muro
                self.dir[0] *= -1  # Inverte direzione orizzontale (rimbalza)
                self.rect.x += self.dir[0]  # Muove nella nuova direzione
        self.rect.y += self.dir[1]  # Muove in verticale nella direzione corrente
        for m in muri:  # Controlla collisioni con ogni muro
            if self.rect.colliderect(m):  # Se collide con un muro
                self.dir[1] *= -1  # Inverte direzione verticale (rimbalza)
                self.rect.y += self.dir[1]  # Muove nella nuova direzione

    def draw(self, surface, camera_pos):
        """Disegna il nemico sulla screen corretta per la camera"""
        surface.blit(self.image, (self.rect.x - camera_pos[0], self.rect.y - camera_pos[1]))  # Disegna adattando alla camera