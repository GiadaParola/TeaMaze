"""Costanti del gioco"""
import os

# Configurazione schermo
FPS = 60
LARGHEZZA, ALTEZZA = 1920, 1080
ZOOM_FACTOR = 2
V_LARGHEZZA = LARGHEZZA // ZOOM_FACTOR
V_ALTEZZA = ALTEZZA // ZOOM_FACTOR

# Percorsi asset
BASE_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(BASE_DIR, "img")

# Campo visivo
RAGGIO_LUCE_INIZIALE = 200
RAGGIO_LUCE_MIN = 100
RAGGIO_LUCE_MAX = 400
INCREMENTO_RAGGIO = 3

# Zoom sfondo
ZOOM_SFONDO = 1.8

# Colori
COL_ESTERNO = (30, 30, 30)
COL_BIANCO = (255, 255, 255)
COL_NERO = (0, 0, 0)
COL_GRIGIO = (200, 200, 200)
COL_VERDE = (0, 200, 0)
COL_ROSSO = (200, 0, 0)
