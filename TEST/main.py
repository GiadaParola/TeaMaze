# Importa librerie per il gioco
import pygame  # Libreria principale per creare il gioco 2D
import sys  # Per uscire dal programma
import pytmx  # Per caricare mappe Tiled
import random  # Per generare numeri casuali
from PIL import Image  # Per elaborare immagini e GIF
import os  # Per gestire i percorsi dei file
import giocatore    
import nemico
# Base directory per asset (cartella img collocata accanto a questo file)
BASE_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(BASE_DIR, "img")


# --- CONFIGURAZIONE ---
FPS = 60  # Fotogrammi al secondo
LARGHEZZA, ALTEZZA = 1920, 1080  # Risoluzione schermo principale
ZOOM_FACTOR = 2  # Fattore di zoom (riduce la risoluzione di rendering)
V_LARGHEZZA = LARGHEZZA // ZOOM_FACTOR  # Larghezza schermo virtuale (960)
V_ALTEZZA = ALTEZZA // ZOOM_FACTOR  # Altezza schermo virtuale (540)

def carica_immagine(nome, colore_fallback):
    """Carica un'immagine, se fallisce crea una superficie di colore"""  
    try:
        return pygame.image.load(nome).convert_alpha()  # Carica l'immagine e ottimizzala
    except:
        s = pygame.Surface((100, 100))  # Se fallisce, crea una superficie 100x100
        s.fill(colore_fallback)  # Riempila con il colore di fallback
        return s  # Ritorna la superficie di colore

def estrai_frames_gif(percorso, larghezza_desiderata):
    """Estrae tutti i frame da una GIF e li ridimensiona"""
    frames = []  # Lista che contiene tutti i frame
    try:
        with Image.open(percorso) as img:  # Apre il file GIF
            w_orig, h_orig = img.size  # Prende le dimensioni originali
            ratio = h_orig / w_orig  # Calcola il rapporto altezza/larghezza
            nuova_dim = (larghezza_desiderata, int(larghezza_desiderata * ratio))  # Calcola nuove dimensioni mantenendo rapporto
            for i in range(img.n_frames):  # Cicla per ogni frame della GIF
                img.seek(i)  # Vai al frame i-esimo
                f = img.convert("RGBA")  # Converte il frame in formato RGBA
                p_img = pygame.image.fromstring(f.tobytes(), img.size, "RGBA")  # Converte in surface pygame
                frames.append(pygame.transform.scale(p_img, nuova_dim))  # Ridimensiona e aggiungi a frames
    except: 
        print(f"Impossibile caricare la GIF: {percorso}")  # Se errore, stampa messaggio
    return frames  # Ritorna lista di frame


def crea_superficie_luce(raggio):
    # Crea una superficie quadrata per la luce
    superficie = pygame.Surface((raggio * 2, raggio * 2), pygame.SRCALPHA)
    for r in range(raggio, 0, -1):
        # Calcola l'alpha: più esterno = più scuro
        # 255 è nero, 0 è trasparente
        alpha = int(255 * (r / raggio)) 
        pygame.draw.circle(superficie, (0, 0, 0, alpha), (raggio, raggio), r)
    return superficie
    

def main():
    """Funzione principale del gioco"""
    pygame.init()  # Inizializza la libreria pygame
    
    screen = pygame.display.set_mode((LARGHEZZA, ALTEZZA))  # Crea finestra principale 1920x1080
    v_screen = pygame.Surface((V_LARGHEZZA, V_ALTEZZA))  # Superficie virtuale per il rendering (960x540)
    clock = pygame.time.Clock()  # Orologio per controllare FPS
    font = pygame.font.SysFont("Arial", 50, bold=True)  # Font per il testo

    # Carica le immagini per il gioco
    img_m_statica = carica_immagine(os.path.join(IMG_DIR, "personaggioM.png"), (0, 0, 255))  # Immagine giocatore statica (fallback blu)
    img_minotauro = carica_immagine(os.path.join(IMG_DIR, "minotauro.png"), (200, 0, 0))  # Immagine nemico (fallback rosso)
    img_scheletro = carica_immagine(os.path.join(IMG_DIR, "scheletroOro.png"), (400, 0, 0)) 
    img_bosco_base = carica_immagine(os.path.join(IMG_DIR, "bosco.png"), (30, 30, 30))  # Immagine sfondo bosco (fallback grigio)
    try:
        # Carica lo sfondo del menu
        img_menu = pygame.image.load(os.path.join(IMG_DIR, "menuPrincipale.png")).convert()
        img_menu = pygame.transform.scale(img_menu, (LARGHEZZA, ALTEZZA))
    except:
        # Fallback se l'immagine manca
        img_menu = pygame.Surface((LARGHEZZA, ALTEZZA))
        img_menu.fill((20, 20, 20))
    # Prepara lo sfondo del bosco
    
    ZOOM_SFONDO = 1.8  # Fattore di zoom per lo sfondo
    nw, nh = int(V_LARGHEZZA * ZOOM_SFONDO), int(V_ALTEZZA * ZOOM_SFONDO)  # Nuove dimensioni zoom
    img_bosco = pygame.transform.scale(img_bosco_base, (nw, nh))  # Ridimensiona l'immagine
    larghezza_btn = 300
    altezza_btn = 70
    centro_x = LARGHEZZA // 2 - larghezza_btn // 2
    inizio_y = ALTEZZA // 2 + 50 # 50 pixel sotto la metà

    rect_gioca = pygame.Rect(centro_x, inizio_y, larghezza_btn, altezza_btn)
    rect_impostazioni = pygame.Rect(centro_x, inizio_y + 100, larghezza_btn, altezza_btn)
    rect_uscita = pygame.Rect(centro_x, inizio_y + 200, larghezza_btn, altezza_btn)
    off_x = (nw - V_LARGHEZZA) // 2  # Offset X per centrare lo sfondo
    off_y = (nh - V_ALTEZZA) // 2  # Offset Y per centrare lo sfondo

    # Inizializza variabili di stato
    stato_gioco = "MENU_PRINCIPALE"  # Stato iniziale del gioco
    personaggio_scelto = None  # Personaggio non ancora scelto
    livelli_possibili = [os.path.join(IMG_DIR, 'mappa1.tmx'), os.path.join(IMG_DIR, 'mappa2.tmx'), os.path.join(IMG_DIR, 'mappa3.tmx')]  # Livello non ancora scelto]
    frames_animati = []  # Lista frames animazione giocatore
    raggio_luce = 200
    luce_mask = crea_superficie_luce(raggio_luce)
    # Personaggi disponibili per il menu di selezione
    personaggi = [
        {
            "nome": "Personaggio M",
            "codice": "M",
            "frames": estrai_frames_gif(os.path.join(IMG_DIR, "personaggioMAnimato.gif"), 200)
        },
        {
            "nome": "Personaggio F",
            "codice": "F",
            "frames": estrai_frames_gif(os.path.join(IMG_DIR, "personaggioFAnimato.gif"), 200)
        }
    ]
    indice_personaggio = 0          # Indice del personaggio mostrato nel menu
    indice_frame_personaggio = 0    # Indice del frame GIF nel menu
    # Loop principale del gioco
    while True:
        event = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()
        
        for e in event:
            if e.type == pygame.QUIT: 
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: 
                stato_gioco = "MENU_PRINCIPALE"

        # STATO: Menu principale
        if stato_gioco == "MENU_PRINCIPALE":
            # CREA I PULSANTI QUI OGNI VOLTA
            larghezza_btn, altezza_btn = 350, 80
            cx = LARGHEZZA // 2 - larghezza_btn // 2
            rect_gioca = pygame.Rect(cx, ALTEZZA // 2 + 50, larghezza_btn, altezza_btn)
            rect_impostazioni = pygame.Rect(cx, ALTEZZA // 2 + 160, larghezza_btn, altezza_btn)
            rect_uscita = pygame.Rect(cx, ALTEZZA // 2 + 270, larghezza_btn, altezza_btn)
            
            screen.blit(img_menu, (0, 0))
            
            # Pulsante GIOCA (verde)
            col_gioca = (0, 180, 0) if rect_gioca.collidepoint(mouse_pos) else (0, 130, 0)
            pygame.draw.rect(screen, col_gioca, rect_gioca, border_radius=15)
            txt_gioca = font.render("GIOCA", True, (255, 255, 255))
            screen.blit(txt_gioca, (rect_gioca.centerx - txt_gioca.get_width()//2, rect_gioca.centery - txt_gioca.get_height()//2))
            
            # Pulsante IMPOSTAZIONI (grigio)
            col_impostazioni = (100, 100, 100) if rect_impostazioni.collidepoint(mouse_pos) else (70, 70, 70)
            pygame.draw.rect(screen, col_impostazioni, rect_impostazioni, border_radius=15)
            txt_impostazioni = font.render("IMPOSTAZIONI", True, (255, 255, 255))
            screen.blit(txt_impostazioni, (rect_impostazioni.centerx - txt_impostazioni.get_width()//2, rect_impostazioni.centery - txt_impostazioni.get_height()//2))
            
            # Pulsante USCITA (rosso)
            col_uscita = (180, 0, 0) if rect_uscita.collidepoint(mouse_pos) else (130, 0, 0)
            pygame.draw.rect(screen, col_uscita, rect_uscita, border_radius=15)
            txt_uscita = font.render("USCITA", True, (255, 255, 255))
            screen.blit(txt_uscita, (rect_uscita.centerx - txt_uscita.get_width()//2, rect_uscita.centery - txt_uscita.get_height()//2))
            
            # Gestione click
            for e in event:
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if rect_gioca.collidepoint(e.pos): 
                        stato_gioco = "SELEZIONE_PERSONAGGIO"
                    if rect_uscita.collidepoint(e.pos): 
                        pygame.quit()
                        sys.exit()
                        
        elif stato_gioco == "SELEZIONE_PERSONAGGIO":

            # Sfondo bianco per il menu di selezione personaggio
            screen.fill((255, 255, 255))

            # Rettangoli per le frecce e per il pulsante "Seleziona"
            btn_sx = pygame.Rect(LARGHEZZA // 2 - 250, ALTEZZA // 2 - 60, 80, 80)
            btn_dx = pygame.Rect(LARGHEZZA // 2 + 170, ALTEZZA // 2 - 60, 80, 80)
            btn_select = pygame.Rect(LARGHEZZA // 2 - 150, ALTEZZA // 2 + 200, 300, 80)

            # Disegna il personaggio attualmente selezionato (GIF)
            personaggio_corrente = personaggi[indice_personaggio]
            frames_correnti = personaggio_corrente["frames"]

            if frames_correnti:
                # Anima la GIF: ogni 5 tick cambia frame
                frame_da_mostrare = frames_correnti[(indice_frame_personaggio // 5) % len(frames_correnti)]
                rect_gif = frame_da_mostrare.get_rect(center=(LARGHEZZA // 2, ALTEZZA // 2 - 40))
                screen.blit(frame_da_mostrare, rect_gif)
                indice_frame_personaggio = (indice_frame_personaggio + 1) % (len(frames_correnti) * 5)
            else:
                # Fallback se la GIF non è stata caricata
                rect_placeholder = pygame.Rect(LARGHEZZA // 2 - 100, ALTEZZA // 2 - 140, 200, 200)
                pygame.draw.rect(screen, (200, 200, 200), rect_placeholder, border_radius=20)

            # Nome del personaggio
            txt_nome = font.render(personaggio_corrente["nome"], True, (0, 0, 0))
            screen.blit(
                txt_nome,
                (LARGHEZZA // 2 - txt_nome.get_width() // 2, 120)
            )

            # Disegno dei pulsanti freccia
            pygame.draw.rect(screen, (220, 220, 220), btn_sx, border_radius=15)
            pygame.draw.rect(screen, (220, 220, 220), btn_dx, border_radius=15)

            txt_sx = font.render("<", True, (0, 0, 0))
            txt_dx = font.render(">", True, (0, 0, 0))
            screen.blit(txt_sx, (btn_sx.centerx - txt_sx.get_width() // 2, btn_sx.centery - txt_sx.get_height() // 2))
            screen.blit(txt_dx, (btn_dx.centerx - txt_dx.get_width() // 2, btn_dx.centery - txt_dx.get_height() // 2))

            # Pulsante di selezione
            pygame.draw.rect(screen, (0, 150, 0), btn_select, border_radius=20)
            txt_sel = font.render("SELEZIONA", True, (255, 255, 255))
            screen.blit(
                txt_sel,
                (btn_select.centerx - txt_sel.get_width() // 2, btn_select.centery - txt_sel.get_height() // 2)
            )

            # Gestione degli input del mouse nel menu personaggio
            for e in event:
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if btn_sx.collidepoint(e.pos):
                        indice_personaggio = (indice_personaggio - 1) % len(personaggi)
                        indice_frame_personaggio = 0
                    elif btn_dx.collidepoint(e.pos):
                        indice_personaggio = (indice_personaggio + 1) % len(personaggi)
                        indice_frame_personaggio = 0
                    elif btn_select.collidepoint(e.pos):
                        # Conferma selezione personaggio
                        personaggio_scelto = personaggio_corrente["codice"]
                        # Usa una versione più piccola della GIF per il gioco vero e proprio
                        if personaggio_scelto == "M":
                            frames_animati = estrai_frames_gif(os.path.join(IMG_DIR, "personaggioMAnimato.gif"), 28)
                        elif personaggio_scelto == "F":
                            frames_animati = estrai_frames_gif(os.path.join(IMG_DIR, "personaggioFAnimato.gif"), 28)
                        stato_gioco = "SELEZIONE_LIVELLO"
        elif stato_gioco == "SELEZIONE_LIVELLO":

            screen.fill((20, 20, 60))

            btn_lvl1 = pygame.Rect(700, 350, 400, 80)
            btn_lvl2 = pygame.Rect(700, 470, 400, 80)
            btn_lvl3 = pygame.Rect(700, 590, 400, 80)

            pygame.draw.rect(screen, (0,120,200), btn_lvl1, border_radius=15)
            pygame.draw.rect(screen, (0,160,220), btn_lvl2, border_radius=15)
            pygame.draw.rect(screen, (0,200,240), btn_lvl3, border_radius=15)

            screen.blit(font.render("LIVELLO 1", True, (255,255,255)), (btn_lvl1.x+90, btn_lvl1.y+15))
            screen.blit(font.render("LIVELLO 2", True, (255,255,255)), (btn_lvl2.x+90, btn_lvl2.y+15))
            screen.blit(font.render("LIVELLO 3", True, (255,255,255)), (btn_lvl3.x+90, btn_lvl3.y+15))

            for e in event:
                if e.type == pygame.MOUSEBUTTONDOWN:

                    if btn_lvl1.collidepoint(e.pos):
                        livello_scelto = livelli_possibili[0] # Livello 1 è mappa1.tmx
                        stato_gioco = "INIZIALIZZA"

                    if btn_lvl2.collidepoint(e.pos):
                        livello_scelto = livelli_possibili[1] # Livello 2 è mappa2.tmx
                        stato_gioco = "INIZIALIZZA"
                        print("livello 2 selezionato")

                    if btn_lvl3.collidepoint(e.pos):
                        livello_scelto = livelli_possibili[2] # Livello 3 è mappa3.tmx
                        stato_gioco = "INIZIALIZZA"
            # STATO: Inizializza mappa e oggetti di gioco
        elif stato_gioco == "INIZIALIZZA":
            if livello_scelto is None:
                print("ERRORE: livello non selezionato")
                return
            try:
                tmx_data = pytmx.util_pygame.load_pygame(livello_scelto)  # Carica la mappa Tiled
            except:
                print(f"Errore: {livello_scelto} non trovata!")  # Se non trova la mappa
                pygame.quit(); sys.exit()  # Esci dal gioco
                
            muri = []  # Lista che conterrà i muri (rettangoli)
            rect_uscita = None  # Area di uscita del labirinto (oggetto)
            fine_tiles = []  # Tile che terminano il livello

            # Estrae informazioni da tutti i layer della mappa
            for layer in tmx_data.visible_layers:
                layer_class = getattr(layer, "class_", None)

                # Muri: tutti i layer di tile con nome "sfondo" o classe "sfondo"
                if isinstance(layer, pytmx.TiledTileLayer) and (
                    layer.name == "sfondo" or layer_class == "sfondo"
                ):
                    for x, y, gid in layer:  # Cicla su ogni tile
                        if tmx_data.get_tile_image_by_gid(gid):  # Se tile è visibile
                            rect_tile = pygame.Rect(x*32, y*32, 32, 32)
                            muri.append(rect_tile)  # Aggiungi rettangolo muro

                # Tile con classe "Fine" fanno finire il livello
                if isinstance(layer, pytmx.TiledTileLayer):
                    for x, y, gid in layer:
                        if not gid:
                            continue
                        props = tmx_data.get_tile_properties_by_gid(gid) or {}
                        tile_class = props.get("class") or props.get("type")
                        if tile_class == "Fine":
                            fine_tiles.append(pygame.Rect(x*32, y*32, 32, 32))

            # Oggetti di uscita "Fine": leggili anche se il layer è invisibile
            for layer in tmx_data.layers:
                if isinstance(layer, pytmx.TiledObjectGroup) and layer.name == "Fine":
                    for obj in layer:
                        if getattr(obj, "name", None) == "Fine":
                            rect_uscita = pygame.Rect(obj.x, obj.y, obj.width, obj.height)

            # Crea istanze giocatore e nemico
            if(livello_scelto==livelli_possibili[0]):
            
                player = giocatore.Giocatore(90, 70, img_m_statica, frames_animati)  # Giocatore a posizione 100,100
            elif(livello_scelto==livelli_possibili[1]):
                player = giocatore.Giocatore(60, 390, img_m_statica, frames_animati)
            else:
                player = giocatore.Giocatore(440, 580, img_m_statica, frames_animati)
                
            nemico1 = nemico.Nemico(400, 400, img_minotauro)  # Nemico a posizione 400,400
            nemico2 = nemico.Nemico(800, 800, img_scheletro)  # Nemico a posizione 400,400
            stato_gioco = "IN_GIOCO"  # Inizia il gioco

        # STATO: Gioco in corso
        elif stato_gioco == "IN_GIOCO":
            keys = pygame.key.get_pressed()  # Prendi lo stato di tutte le tastiere
            # Calcola movimento in base ai tasti: RIGHT-LEFT per X, DOWN-UP per Y, moltiplicato per 2
            player.muovi((keys[pygame.K_RIGHT]-keys[pygame.K_LEFT])*2, (keys[pygame.K_DOWN]-keys[pygame.K_UP])*2, muri)
            nemico1.muovi_auto(muri)  # Muove il nemico in modo autonomo
            nemico2.muovi_auto(muri)  # Muove il nemico in modo autonomo

            # Controlla vittoria: se giocatore raggiunge l'uscita (oggetto) o una tile con classe "Fine"
            if rect_uscita and player.rect.colliderect(rect_uscita):
                stato_gioco = "VITTORIA"
            else:
                for fine_rect in fine_tiles:
                    if player.rect.colliderect(fine_rect):
                        stato_gioco = "VITTORIA"
                        break
            # Controlla sconfitta: se giocatore collide con nemico, ritorna all'inizio
            if player.rect.colliderect(nemico1.rect): player.rect.topleft = (100, 100)
            if player.rect.colliderect(nemico2.rect): player.rect.topleft = (100, 100)

            # Calcola posizione della camera centrata sul giocatore
            cam_x = player.rect.centerx - V_LARGHEZZA//2  # Camera X
            cam_y = player.rect.centery - V_ALTEZZA//2  # Camera Y
            v_screen.blit(img_bosco, (-off_x, -off_y))  # Disegna sfondo bosco
            
            # Disegna tutti i tile della mappa
            for layer in tmx_data.visible_layers:
                if isinstance(layer, pytmx.TiledTileLayer):  # Se è un layer di tile
                    for x, y, gid in layer:  # Per ogni tile
                        tile = tmx_data.get_tile_image_by_gid(gid)  # Ottieni immagine tile
                        if tile: v_screen.blit(tile, (x*32-cam_x, y*32-cam_y))  # Disegna tile adattato a camera
            
            # Disegna nemico e giocatore
            nemico1.draw(v_screen, (cam_x, cam_y))  # Disegna nemico1
            nemico2.draw(v_screen, (cam_x, cam_y))  # Disegna nemico2
            player.draw(v_screen, (cam_x, cam_y))  # Disegna giocatore
            # Ridimensiona lo schermo virtuale alla risoluzione reale e lo mostra
            screen.blit(pygame.transform.scale(v_screen, (LARGHEZZA, ALTEZZA)), (0,0))
            variazione = random.randint(-5, 5) # Piccola variazione casuale
            raggio_dinamico = raggio_luce + variazione
            
            # Se vuoi bordi ancora più morbidi, rigenera la maschera ogni tanto 
            # o scalamela leggermente:
            luce_scalata = pygame.transform.scale(luce_mask, (raggio_dinamico*2, raggio_dinamico*2))
            # --- LUCE DINAMICA ---
            # 1. Creiamo una superficie per l'oscurità (nera e con alpha)
            superficie_oscurita = pygame.Surface((V_LARGHEZZA, V_ALTEZZA), pygame.SRCALPHA)
            superficie_oscurita.fill((0, 0, 0, 235)) # Il 235 indica quanto è buio (0-255)

            # 2. Calcoliamo la posizione del giocatore sullo schermo virtuale
            # (Non la posizione nel mondo, ma dove appare fisicamente sul monitor)
            pos_schermo_x = player.rect.centerx - cam_x
            pos_schermo_y = player.rect.centery - cam_y

            # 3. "Buchiamo" l'oscurità con un cerchio trasparente
            # Usiamo blend_rgba_min per sottrarre l'oscurità dove c'è il cerchio
            pygame.draw.circle(superficie_oscurita, (0, 0, 0, 0), (pos_schermo_x, pos_schermo_y), raggio_luce)

            # 4. Applichiamo la maschera sulla virtual_screen
            v_screen.blit(superficie_oscurita, (0, 0))

            # --- INTERFACCIA (UI) ---
            # Mostriamo il valore del raggio in un angolo
            txt_raggio = font.render(f"Raggio Luce: {raggio_luce}", True, (255, 255, 255))
            v_screen.blit(txt_raggio, (10, 10))
            oscurita = pygame.Surface((V_LARGHEZZA, V_ALTEZZA), pygame.SRCALPHA)
            oscurita.fill((0, 0, 0, 250)) # 250 è quasi nero totale

            # 2. Calcoliamo dove si trova il giocatore sullo schermo
            pos_x = player.rect.centerx - cam_x - raggio_luce
            pos_y = player.rect.centery - cam_y - raggio_luce

            # 3. Usiamo il metodo BLEND_RGBA_MIN per "sottrarre" l'oscurità
            # Questo crea l'effetto dissolvenza tra luce e buio
            oscurita.blit(luce_mask, (pos_x, pos_y), special_flags=pygame.BLEND_RGBA_MIN)

            # 4. Applichiamo l'oscurità finale sullo schermo virtuale
            v_screen.blit(oscurita, (0, 0))

            # Disegno finale
            screen.blit(pygame.transform.scale(v_screen, (LARGHEZZA, ALTEZZA)), (0, 0))
        # STATO: Vittoria
        elif stato_gioco == "VITTORIA":
            screen.fill((0, 80, 0))  # Sfondo verde scuro
            txt = font.render("SEI FUGGITO!", True, (255, 255, 255))  # Testo vittoria bianco
            screen.blit(txt, (LARGHEZZA//2 - txt.get_width()//2, ALTEZZA//2 - 50))  # Disegna testo centrato
            for e in event:  # Controlla input
                if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE: stato_gioco = "MENU_PRINCIPALE"  # SPAZIO = ritorna al menu

        # Aggiorna la finestra e limita FPS
        pygame.display.flip()  # Aggiorna il display
        clock.tick(FPS)  # Limita a 60 FPS

# Punto di ingresso del programma
if __name__ == "__main__":
    main()  # Avvia il gioco