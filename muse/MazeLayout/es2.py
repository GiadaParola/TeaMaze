import pygame
import sys

# --- CONFIGURAZIONE ---
TILE_SIZE = 50  # Dimensione ridotta per vedere bene i bordi del labirinto
FPS = 60

# Colori
COL_ESTERNO = (30, 30, 30)   # Sfondo fuori dal labirinto
COL_PERCORSO = (255, 255, 255) # Gli "0" ora sono bianchi
COL_MURO_NERO = (0, 0, 0)
COL_MURO_ROSSO = (255, 0, 0)
COL_END = (255, 215, 0)
COL_TESTO = (255, 255, 255)

# Mappa (20 colonne x 15 righe)
mappa = [
    "11111111111111111111",
    "1S001000001000000111",
    "11R10000100000100011",
    "10000011010011010011",
    "10100100000100000111",
    "10110101000000000011",
    "10110R11011011000111",
    "10100000000000000011",
    "10001011110110111001",
    "11011011110RR0001011",
    "10010010000110011101",
    "10111000011110000111",
    "100000000111111000E1",
    "10000000000000000001",
    "11111111111111111111"
]

class Giocatore:
    def __init__(self, x, y, immagine):
        self.image = immagine
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel = 3

    def muovi(self, dx, dy, muri):
        self.rect.x += dx
        for muro in muri:
            if self.rect.colliderect(muro):
                if dx > 0: self.rect.right = muro.left
                if dx < 0: self.rect.left = muro.right
        self.rect.y += dy
        for muro in muri:
            if self.rect.colliderect(muro):
                if dy > 0: self.rect.bottom = muro.top
                if dy < 0: self.rect.top = muro.bottom

    def draw(self, surface):
        surface.blit(self.image, self.rect)

def draw_button(screen, font, testo, x, y, w, h, col_base, col_hover):
    mouse = pygame.mouse.get_pos()
    cliccato = pygame.mouse.get_pressed()
    sopra = x < mouse[0] < x + w and y < mouse[1] < y + h
    corrente = col_hover if sopra else col_base
    pygame.draw.rect(screen, corrente, (x, y, w, h), border_radius=12)
    txt_surf = font.render(testo, True, COL_TESTO)
    screen.blit(txt_surf, txt_surf.get_rect(center=(x + w/2, y + h/2)))
    return sopra and cliccato[0]

def main():
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    pygame.display.set_caption("Teamaze - White Path Edition")
    clock = pygame.time.Clock()
    
    font_titolo = pygame.font.SysFont("Arial", 100, bold=True)
    font_menu = pygame.font.SysFont("Arial", 40)

    files_personaggi = ["personaggioF.png", "personaggioM.png"]
    indice_p = 0
    
    # Calcolo offset per centrare il labirinto (1000x750) nello schermo 1920x1080
    larg_mappa = len(mappa[0]) * TILE_SIZE
    alt_mappa = len(mappa) * TILE_SIZE
    offset_x = (1920 - larg_mappa) // 2
    offset_y = (1080 - alt_mappa) // 2

    def get_p_img(size):
        try:
            img = pygame.image.load(files_personaggi[indice_p]).convert_alpha()
            return pygame.transform.scale(img, (size, size))
        except:
            surf = pygame.Surface((size, size))
            surf.fill((0, 150, 255))
            return surf

    stato = "menu"
    muri_solidi = []
    muri_rossi = []
    pavimento = [] 
    trigger_fine = None
    player = None

    running = True
    while running:
        screen.fill(COL_ESTERNO)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if stato == "menu":
            txt = font_titolo.render("TEAMAZE", True, (0, 200, 255))
            screen.blit(txt, (1920//2 - txt.get_width()//2, 100))
            anteprima = get_p_img(150)
            screen.blit(anteprima, (1920//2 - 75, 250))
            
            if draw_button(screen, font_menu, "GIOCA", 1920//2 - 150, 450, 300, 60, (0, 150, 0), (0, 200, 0)):
                muri_solidi = []
                muri_rossi = []
                pavimento = []
                for r, riga in enumerate(mappa):
                    for c, cella in enumerate(riga):
                        rect = pygame.Rect(c*TILE_SIZE + offset_x, r*TILE_SIZE + offset_y, TILE_SIZE, TILE_SIZE)
                        
                        # Ogni cella che NON è un muro nero viene disegnata bianca come base
                        if cella != "1":
                            pavimento.append(rect)
                            
                        if cella == "1":
                            muri_solidi.append(rect)
                        elif cella == "R":
                            muri_rossi.append(rect)
                        elif cella == "E":
                            trigger_fine = rect
                        elif cella == "S":
                            p_size = 40 # Personaggio più piccolo per muoversi meglio
                            p_off = (TILE_SIZE - p_size) // 2
                            player = Giocatore(rect.x + p_off, rect.y + p_off, get_p_img(p_size))
                stato = "gioco"
                pygame.time.delay(200)

            if draw_button(screen, font_menu, "CAMBIA PERSONAGGIO", 1920//2 - 200, 550, 400, 60, (0, 100, 200), (0, 150, 255)):
                indice_p = (indice_p + 1) % len(files_personaggi)
                pygame.time.delay(200)

            if draw_button(screen, font_menu, "ESCI", 1920//2 - 150, 650, 300, 60, (150, 0, 0), (200, 0, 0)):
                running = False

        elif stato == "gioco":
            tasti = pygame.key.get_pressed()
            dx, dy = 0, 0
            if tasti[pygame.K_LEFT] or tasti[pygame.K_a]: dx = -player.vel
            if tasti[pygame.K_RIGHT] or tasti[pygame.K_d]: dx = player.vel
            if tasti[pygame.K_UP] or tasti[pygame.K_w]: dy = -player.vel
            if tasti[pygame.K_DOWN] or tasti[pygame.K_s]: dy = player.vel

            player.muovi(dx, dy, muri_solidi)
            if tasti[pygame.K_ESCAPE]: stato = "menu"

            # 1. DISEGNA PAVIMENTO BIANCO
            for p in pavimento:
                pygame.draw.rect(screen, COL_PERCORSO, p)
            
            # 2. DISEGNA MURI E FINE
            for m in muri_solidi: pygame.draw.rect(screen, COL_MURO_NERO, m)
            for r in muri_rossi: pygame.draw.rect(screen, COL_MURO_ROSSO, r)
            if trigger_fine: pygame.draw.rect(screen, COL_END, trigger_fine)
            
            # 3. DISEGNA PERSONAGGIO
            player.draw(screen)

            if trigger_fine and player.rect.colliderect(trigger_fine):
                stato = "menu"
                pygame.time.delay(500)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()