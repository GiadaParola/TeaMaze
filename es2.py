import pygame
import sys
import pytmx
import random
from PIL import Image

# --- CONFIGURAZIONE ---
FPS = 60
COL_ESTERNO = (30, 30, 30)
LARGHEZZA, ALTEZZA = 1920, 1080
ZOOM_FACTOR = 2 
V_LARGHEZZA = LARGHEZZA // ZOOM_FACTOR
V_ALTEZZA = ALTEZZA // ZOOM_FACTOR

# --- FUNZIONI DI UTILITÀ ---
def carica_immagine(nome, colore_fallback):
    try:
        return pygame.image.load(nome).convert_alpha()
    except:
        s = pygame.Surface((100, 100))
        s.fill(colore_fallback)
        return s

def estrai_frames_gif(percorso, larghezza_desiderata):
    """Estrae i frame dalla GIF mantenendo le proporzioni originali."""
    frames = []
    try:
        with Image.open(percorso) as img:
            # Calcolo dell'altezza proporzionale
            w_orig, h_orig = img.size
            ratio = h_orig / w_orig
            altezza_proporzionata = int(larghezza_desiderata * ratio)
            nuova_dimensione = (larghezza_desiderata, altezza_proporzionata)

            for i in range(img.n_frames):
                img.seek(i)
                frame_rgba = img.convert("RGBA")
                data = frame_rgba.tobytes()
                # Creazione superficie Pygame dal frame
                pygame_surface = pygame.image.fromstring(data, img.size, "RGBA")
                # Scaling proporzionato
                frames.append(pygame.transform.scale(pygame_surface, nuova_dimensione))
    except Exception as e:
        print(f"Errore nel caricamento della GIF: {e}")
    return frames

# --- CLASSI ---
class Giocatore:
    def __init__(self, x, y, img_statica, frames_animati=None):
        # Se abbiamo i frame, prendiamo la dimensione dal primo frame per evitare stretch
        if frames_animati:
            self.image = frames_animati[0]
        else:
            self.image = pygame.transform.scale(img_statica, (28, 28))
            
        self.img_fermo = self.image 
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.frames = frames_animati if frames_animati else []
        self.index_frame = 0
        self.vel_anim = 0.2
        self.sta_muovendo = False

    def muovi(self, dx, dy, muri):
        self.sta_muovendo = (dx != 0 or dy != 0)
        
        # Movimento X
        self.rect.x += dx
        for muro in muri:
            if self.rect.colliderect(muro):
                if dx > 0: self.rect.right = muro.left
                if dx < 0: self.rect.left = muro.right
        
        # Movimento Y
        self.rect.y += dy
        for muro in muri:
            if self.rect.colliderect(muro):
                if dy > 0: self.rect.bottom = muro.top
                if dy < 0: self.rect.top = muro.bottom

    def aggiorna(self):
        if self.sta_muovendo and self.frames:
            self.index_frame += self.vel_anim
            if self.index_frame >= len(self.frames):
                self.index_frame = 0
            self.image = self.frames[int(self.index_frame)]
        else:
            self.image = self.img_fermo

    def draw(self, surface, camera_pos):
        self.aggiorna()
        surface.blit(self.image, (self.rect.x - camera_pos[0], self.rect.y - camera_pos[1]))

class Nemico:
    def __init__(self, x, y, immagine):
        # Anche per il nemico usiamo una scala fissa o proporzionata
        self.image = pygame.transform.scale(immagine, (35, 35))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direzione = [random.choice([-2, 2]), random.choice([-2, 2])]

    def muovi_auto(self, muri):
        self.rect.x += self.direzione[0]
        for muro in muri:
            if self.rect.colliderect(muro):
                self.direzione[0] *= -1
                self.rect.x += self.direzione[0]

        self.rect.y += self.direzione[1]
        for muro in muri:
            if self.rect.colliderect(muro):
                self.direzione[1] *= -1
                self.rect.y += self.direzione[1]

    def draw(self, surface, camera_pos):
        surface.blit(self.image, (self.rect.x - camera_pos[0], self.rect.y - camera_pos[1]))

# --- MAIN ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((LARGHEZZA, ALTEZZA))
    virtual_screen = pygame.Surface((V_LARGHEZZA, V_ALTEZZA))
    clock = pygame.time.Clock()
    
    font_titolo = pygame.font.SysFont("Arial", 80, bold=True)
    font_testo = pygame.font.SysFont("Arial", 35)

    # Asset
    img_Minotauro = carica_immagine("./img/minotauro.png", (255, 0, 0))
    img_m = carica_immagine("./img/personaggioM.png", (0, 0, 255))
    img_f = carica_immagine("./img/personaggioF.png", (255, 105, 180))
    img_bosco_base = carica_immagine("./img/bosco.png", COL_ESTERNO)
    
    # Sfondo bosco zoomato
    ZOOM_SFONDO = 1.8
    nw, nh = int(V_LARGHEZZA * ZOOM_SFONDO), int(V_ALTEZZA * ZOOM_SFONDO)
    img_bosco = pygame.transform.scale(img_bosco_base, (nw, nh))
    off_x, off_y = (nw - V_LARGHEZZA)//2, (nh - V_ALTEZZA)//2

    stato_gioco = "MENU_PRINCIPALE"
    personaggio_scelto = None
    frames_m_animato = []

    while True:
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                stato_gioco = "MENU_PRINCIPALE"

        if stato_gioco == "MENU_PRINCIPALE":
            screen.fill((20, 20, 20))
            titolo = font_titolo.render("LABYRINTH QUEST", True, (255, 215, 0))
            screen.blit(titolo, (LARGHEZZA//2 - titolo.get_width()//2, 200))
            rect_start = pygame.Rect(LARGHEZZA//2 - 150, 500, 300, 80)
            pygame.draw.rect(screen, (0, 150, 0), rect_start, border_radius=15)
            txt = font_testo.render("START", True, (255,255,255))
            screen.blit(txt, (rect_start.centerx - txt.get_width()//2, rect_start.centery - txt.get_height()//2))
            
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and rect_start.collidepoint(event.pos):
                    stato_gioco = "SELEZIONE"

        elif stato_gioco == "SELEZIONE":
            screen.fill((30, 30, 30))
            rect_m = pygame.Rect(LARGHEZZA//2 - 250, 400, 150, 150)
            rect_f = pygame.Rect(LARGHEZZA//2 + 100, 400, 150, 150)
            screen.blit(pygame.transform.scale(img_m, (140, 140)), rect_m)
            screen.blit(pygame.transform.scale(img_f, (140, 140)), rect_f)
            
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if rect_m.collidepoint(event.pos):
                        personaggio_scelto = "M"
                        # Larghezza 28, l'altezza si adatta automaticamente
                        frames_m_animato = estrai_frames_gif("./img/personaggioManimato.gif", 28)
                        stato_gioco = "INIZIALIZZA"
                    if rect_f.collidepoint(event.pos):
                        personaggio_scelto = "F"
                        stato_gioco = "INIZIALIZZA"

        elif stato_gioco == "INIZIALIZZA":
            tmx_data = pytmx.util_pygame.load_pygame("./img/mappa1.tmx")
            muri_solidi = []
            for layer in tmx_data.visible_layers:
                if isinstance(layer, pytmx.TiledTileLayer) and layer.name == "sfondo":
                    for x, y, gid in layer:
                        if tmx_data.get_tile_image_by_gid(gid):
                            muri_solidi.append(pygame.Rect(x*tmx_data.tilewidth, y*tmx_data.tileheight, tmx_data.tilewidth, tmx_data.tileheight))
            
            img_base = img_m if personaggio_scelto == "M" else img_f
            anim = frames_m_animato if personaggio_scelto == "M" else None
            player = Giocatore(100, 100, img_base, anim)
            nemico = Nemico(400, 300, img_Minotauro)
            stato_gioco = "IN_GIOCO"

        elif stato_gioco == "IN_GIOCO":
            virtual_screen.blit(img_bosco, (-off_x, -off_y))
            
            keys = pygame.key.get_pressed()
            player.muovi((keys[pygame.K_RIGHT]-keys[pygame.K_LEFT])*4, (keys[pygame.K_DOWN]-keys[pygame.K_UP])*4, muri_solidi)
            nemico.muovi_auto(muri_solidi)

            if player.rect.colliderect(nemico.rect):
                stato_gioco = "DOMANDA"

            cam_x = player.rect.centerx - V_LARGHEZZA//2
            cam_y = player.rect.centery - V_ALTEZZA//2

            for layer in tmx_data.visible_layers:
                if isinstance(layer, pytmx.TiledTileLayer):
                    for x, y, gid in layer:
                        tile = tmx_data.get_tile_image_by_gid(gid)
                        if tile: virtual_screen.blit(tile, (x*tmx_data.tilewidth - cam_x, y*tmx_data.tileheight - cam_y))
            
            nemico.draw(virtual_screen, (cam_x, cam_y))
            player.draw(virtual_screen, (cam_x, cam_y))
            screen.blit(pygame.transform.scale(virtual_screen, (LARGHEZZA, ALTEZZA)), (0, 0))

        elif stato_gioco == "DOMANDA":
            screen.fill((50, 0, 0))
            msg = font_testo.render("TI HO PRESO! Premi SPAZIO per tornare all'inizio", True, (255, 255, 255))
            screen.blit(msg, (LARGHEZZA//2 - msg.get_width()//2, ALTEZZA//2))
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    player.rect.topleft = (100, 100)
                    stato_gioco = "IN_GIOCO"

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()