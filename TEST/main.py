# Importa librerie per il gioco
import pygame
import sys
import pytmx
import random
import os


# Importa moduli locali
import giocatore    
import nemico
from utilita import carica_immagine, estrai_frames_gif, crea_superficie_luce
from costanti import *
from domande import DOMANDE
   


def main():
    """Funzione principale del gioco"""
    pygame.init()  # Inizializza la libreria pygame
    # Inizializza il mixer audio (se possibile)
    try:
        pygame.mixer.init()
    except Exception:
        pass


    # Mappa delle musica: assegna i file presenti in TEST/sounds
    SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")
    MUSIC_FILES = {
        "MENU": os.path.join(SOUNDS_DIR, "awesomeness.wav"),
        "LIVELLO1": os.path.join(SOUNDS_DIR, "01_First_Light.mp3"),
        "LIVELLO2": os.path.join(SOUNDS_DIR, "05_Sanctuary.mp3"),
        "LIVELLO3": os.path.join(SOUNDS_DIR, "11_Chronicles_of_the_Archive.mp3"),
    }


    current_music = None


    def play_music(path, volume=None):
        nonlocal current_music, volume_audio
        try:
            if not path or current_music == path:
                return
            pygame.mixer.music.load(path)
            vol = volume if volume is not None else volume_audio
            pygame.mixer.music.set_volume(vol)
            pygame.mixer.music.play(-1)  # loop infinito
            current_music = path
        except Exception:
            # Se il file non esiste o mixer non inizializzato, ignoriamo
            current_music = None
   
    screen = pygame.display.set_mode((LARGHEZZA, ALTEZZA))  # Crea finestra principale 1920x1080
    v_screen = pygame.Surface((V_LARGHEZZA, V_ALTEZZA))  # Superficie virtuale per il rendering (960x540)
    clock = pygame.time.Clock()  # Orologio per controllare FPS
    font = pygame.font.SysFont("Arial", 50, bold=True)  # Font per il testo


    # Carica le immagini per il gioco
    img_m_statica = carica_immagine(os.path.join(IMG_DIR, "personaggioM.png"), (0, 0, 255))  # Immagine giocatore statica (fallback blu)
    img_minotauro = carica_immagine(os.path.join(IMG_DIR, "minotauro.png"), (200, 0, 0))  # Immagine nemico (fallback rosso)
    img_ghost = carica_immagine(os.path.join(IMG_DIR, "ghost.gif"), (400, 0, 0))
    img_drago = carica_immagine(os.path.join(IMG_DIR, "drago.png"), (200, 100, 0))  # Immagine drago
    img_scheletro_oro = carica_immagine(os.path.join(IMG_DIR, "scheletroOro.png"), (220, 180, 0))  # Immagine scheletro oro
    img_bosco_base = carica_immagine(os.path.join(IMG_DIR, "bosco.png"), (30, 30, 30))  # Immagine sfondo bosco (fallback grigio)
    try:
        # Carica lo sfondo del menu
        img_menu = pygame.image.load(os.path.join(IMG_DIR, "menuPrincipale.png")).convert()
        img_menu = pygame.transform.scale(img_menu, (LARGHEZZA, ALTEZZA))
    except:
        # Fallback se l'immagine manca
        img_menu = pygame.Surface((LARGHEZZA, ALTEZZA))
        img_menu.fill((20, 20, 20))
    
    try:
        # Carica lo sfondo del seleziona livello
        img_seleziona_livello = pygame.image.load(os.path.join(IMG_DIR, "sfondoSceltaLivello.jpg")).convert()
        img_seleziona_livello = pygame.transform.scale(img_seleziona_livello, (LARGHEZZA, ALTEZZA))
    except:
        # Fallback se l'immagine manca
        img_seleziona_livello = pygame.Surface((LARGHEZZA, ALTEZZA))
        img_seleziona_livello.fill((20, 20, 20))
    
    try:
        # Carica lo sfondo del seleziona livello
        img_seleziona_personaggio = pygame.image.load(os.path.join(IMG_DIR, "sfondoSceltaPersonaggio.jpg")).convert()
        img_seleziona_personaggio = pygame.transform.scale(img_seleziona_personaggio, (LARGHEZZA, ALTEZZA))
    except:
        # Fallback se l'immagine manca
        img_seleziona_personaggio = pygame.Surface((LARGHEZZA, ALTEZZA))
        img_seleziona_personaggio.fill((20, 20, 20))


    preview1 = carica_immagine(os.path.join(IMG_DIR, "imgMappe", "mappa1.png"), (80, 80, 80))
    preview2 = carica_immagine(os.path.join(IMG_DIR, "imgMappe", "mappa2.png"), (80, 80, 80))
    preview3 = carica_immagine(os.path.join(IMG_DIR, "imgMappe", "mappa3.png"), (80, 80, 80))
    # Prepara lo sfondo del bosco
   
    ZOOM_SFONDO = 1.8  # Fattore di zoom per lo sfondo
    nw, nh = int(V_LARGHEZZA * ZOOM_SFONDO), int(V_ALTEZZA * ZOOM_SFONDO)  # Nuove dimensioni zoom
    img_bosco = pygame.transform.scale(img_bosco_base, (nw, nh))  # Ridimensiona l'immagine
    # Carica animazioni direzionali (versione piccola per il gioco)
    anim_M_forward = estrai_frames_gif(os.path.join(IMG_DIR, "personaggioMAnimato.gif"), 40)
    anim_M_up = estrai_frames_gif(os.path.join(IMG_DIR, "suAnimatoM.gif"), 28)
    anim_M_down = estrai_frames_gif(os.path.join(IMG_DIR, "giuAnimatoM.gif"), 28)
    anim_M_left = [pygame.transform.flip(f, True, False) for f in anim_M_forward] if anim_M_forward else []


    anim_F_forward = estrai_frames_gif(os.path.join(IMG_DIR, "personaggioFAnimato.gif"), 26)
    anim_F_up = estrai_frames_gif(os.path.join(IMG_DIR, "suAnimatoF.gif"), 20)
    anim_F_down = estrai_frames_gif(os.path.join(IMG_DIR, "giuAnimatoF.gif"), 20)
    anim_F_left = [pygame.transform.flip(f, True, False) for f in anim_F_forward] if anim_F_forward else []


    # Dizionari utili per selezione animazioni runtime
    anims_M = {"forward": anim_M_forward, "up": anim_M_up, "down": anim_M_down, "left": anim_M_left, "right": anim_M_forward}
    anims_F = {"forward": anim_F_forward, "up": anim_F_up, "down": anim_F_down, "left": anim_F_left, "right": anim_F_forward}
    anims_corrente = None
    # Animazioni nemici (attacchi/pose da fermo)
    anim_drago_fuoco = estrai_frames_gif(os.path.join(IMG_DIR, "dragoFuoco.gif"), 120)
    anim_minotauro_sbuffa = estrai_frames_gif(os.path.join(IMG_DIR, "sbuffoGif.gif"), 100)
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
    prev_state = None
    personaggio_scelto = None  # Personaggio non ancora scelto
    
    # Variabili per impostazioni
    volume_audio = 0.6  # Volume audio (0.0 - 1.0)
    dimensione_schermo = 1.0  # Fattore di scala (0.5 - 2.0)
    schermo_intero = False  # Modalità schermo intero
    larghezza_attuale = LARGHEZZA
    altezza_attuale = ALTEZZA
    livelli_possibili = [os.path.join(IMG_DIR, 'mappa1.tmx'), os.path.join(IMG_DIR, 'mappa2.tmx'), os.path.join(IMG_DIR, 'mappa3.tmx')]  # Livello non ancora scelto]
    frames_animati = []  # Lista frames animazione giocatore
    raggio_luce = 200
    raggio_luce_min = 100  # Raggio minimo del campo visivo
    raggio_luce_max = 400  # Raggio massimo del campo visivo
    incremento_raggio = 3  # Incremento lineare del raggio per frame quando si preme E
    luce_mask = crea_superficie_luce(raggio_luce)
   
    # Sistema di domande e risposte (importato da domande.py)
    domanda_attiva = None  # Domanda corrente
    nemico_che_ha_colpito = None  # Quale nemico ha colpito (1 o 2)
    risposta_selezionata = None  # Risposta selezionata dall'utente
    mostra_feedback = False  # Se mostrare il feedback (verde/rosso)
    feedback_colore = False  # True se risposta giusta, False se sbagliata
    timer_feedback = 0  # Counter per il feedback (90 = 1.5 secondi a 60 FPS)
   
    # Variabili per i nemici e il giocatore (saranno inizializzate nello stato INIZIALIZZA)
    player = None
    nemico1 = None
    nemico2 = None
    tmx_data = None
    muri = []
    rect_uscita = None
    fine_tiles = []
    pos_iniziale_giocatore = (0, 0)
    livello_scelto = None
    # Posizioni iniziali dei nemici (per reset dopo animazione)
    nemico1_start = None
    nemico2_start = None
    # Stato animazione nemico dopo risposta sbagliata
    enemy_anim_timer = 0
    enemy_anim_frames = []
    enemy_anim_owner = None
    enemy_anim_index = 0
    enemy_anim_frame_hold = 5
   
    # Personaggi disponibili per il menu di selezione
    personaggi = [
        {
            "nome": "Jamie",
            "codice": "M",
            "frames": estrai_frames_gif(os.path.join(IMG_DIR, "personaggioMAnimato.gif"), 200)
        },
        {
            "nome": "Angel",
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
        # Cambia la traccia se lo stato è cambiato
        if stato_gioco != prev_state:
            if stato_gioco == "MENU_PRINCIPALE":
                play_music(MUSIC_FILES.get("MENU"))
            elif stato_gioco == "IN_GIOCO":
                # Scegli la musica in base al livello selezionato
                try:
                    if livello_scelto == livelli_possibili[0]:
                        play_music(MUSIC_FILES.get("LIVELLO1"))
                    elif livello_scelto == livelli_possibili[1]:
                        play_music(MUSIC_FILES.get("LIVELLO2"))
                    else:
                        play_music(MUSIC_FILES.get("LIVELLO3"))
                except Exception:
                    pass
            # aggiorna lo stato precedente
            prev_state = stato_gioco
       
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
            cx = larghezza_attuale // 2 - larghezza_btn // 2
            rect_gioca = pygame.Rect(cx, altezza_attuale // 2 + 50, larghezza_btn, altezza_btn)
            rect_impostazioni = pygame.Rect(cx, altezza_attuale // 2 + 160, larghezza_btn, altezza_btn)
            rect_uscita = pygame.Rect(cx, altezza_attuale // 2 + 270, larghezza_btn, altezza_btn)
           
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
                    if rect_impostazioni.collidepoint(e.pos):
                        stato_gioco = "IMPOSTAZIONI"
                    if rect_uscita.collidepoint(e.pos):
                        pygame.quit()
                        sys.exit()
        
        # --- SELEZIONA PERSONAGGIO ---
        elif stato_gioco == "SELEZIONE_PERSONAGGIO":

            # Sfondo
            screen.blit(img_seleziona_personaggio, (0, 0))

            # Rettangoli pulsanti
            btn_sx = pygame.Rect(LARGHEZZA // 2 - 250, ALTEZZA // 2 - 60, 80, 80)
            btn_dx = pygame.Rect(LARGHEZZA // 2 + 170, ALTEZZA // 2 - 60, 80, 80)
            btn_select = pygame.Rect(LARGHEZZA // 2 - 150, ALTEZZA // 2 + 200, 300, 80)

            # Personaggio corrente
            personaggio_corrente = personaggi[indice_personaggio]
            frames_correnti = personaggio_corrente["frames"]

            # Animazione GIF
            if frames_correnti:
                frame_da_mostrare = frames_correnti[(indice_frame_personaggio // 5) % len(frames_correnti)]
                rect_gif = frame_da_mostrare.get_rect(center=(LARGHEZZA // 2, ALTEZZA // 2 - 40))
                screen.blit(frame_da_mostrare, rect_gif)
                indice_frame_personaggio = (indice_frame_personaggio + 1) % (len(frames_correnti) * 5)
            else:
                rect_placeholder = pygame.Rect(LARGHEZZA // 2 - 100, ALTEZZA // 2 - 140, 200, 200)
                pygame.draw.rect(screen, (200, 200, 200), rect_placeholder, border_radius=20)

            # ===============================
            # NOME PERSONAGGIO CON SFONDO + OMBRA
            # ===============================

            txt_nome = font.render(personaggio_corrente["nome"], True, (0, 0, 0))
            rect_nome = txt_nome.get_rect(center=(LARGHEZZA // 2, 160))

            padding_x = 20
            padding_y = 10
            ombra_offset = 6

            # Rettangolo sfondo bianco
            rect_sfondo = pygame.Rect(
                rect_nome.x - padding_x,
                rect_nome.y - padding_y,
                rect_nome.width + padding_x * 2,
                rect_nome.height + padding_y * 2
            )

            # Rettangolo ombra
            rect_ombra = rect_sfondo.copy()
            rect_ombra.x += ombra_offset
            rect_ombra.y += ombra_offset

            # Disegno ombra (semi-trasparente)
            ombra_surface = pygame.Surface((rect_ombra.width, rect_ombra.height), pygame.SRCALPHA)
            ombra_surface.fill((0, 0, 0, 100))  # nero con alpha
            screen.blit(ombra_surface, (rect_ombra.x, rect_ombra.y))

            # Disegno rettangolo bianco sopra l’ombra
            pygame.draw.rect(screen, (255, 255, 255), rect_sfondo, border_radius=12)

            # Disegno testo sopra tutto
            screen.blit(txt_nome, rect_nome)

            # ===============================

            # Pulsanti freccia
            pygame.draw.rect(screen, (220, 220, 220), btn_sx, border_radius=15)
            pygame.draw.rect(screen, (220, 220, 220), btn_dx, border_radius=15)

            txt_sx = font.render("<", True, (0, 0, 0))
            txt_dx = font.render(">", True, (0, 0, 0))

            screen.blit(txt_sx, (btn_sx.centerx - txt_sx.get_width() // 2,
                                btn_sx.centery - txt_sx.get_height() // 2))

            screen.blit(txt_dx, (btn_dx.centerx - txt_dx.get_width() // 2,
                                btn_dx.centery - txt_dx.get_height() // 2))

            # Pulsante selezione
            pygame.draw.rect(screen, (0, 150, 0), btn_select, border_radius=20)
            txt_sel = font.render("SELEZIONA", True, (255, 255, 255))

            screen.blit(txt_sel,
                        (btn_select.centerx - txt_sel.get_width() // 2,
                        btn_select.centery - txt_sel.get_height() // 2))

            # Gestione input mouse
            for e in event:
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if btn_sx.collidepoint(e.pos):
                        indice_personaggio = (indice_personaggio - 1) % len(personaggi)
                        indice_frame_personaggio = 0

                    elif btn_dx.collidepoint(e.pos):
                        indice_personaggio = (indice_personaggio + 1) % len(personaggi)
                        indice_frame_personaggio = 0

                    elif btn_select.collidepoint(e.pos):
                        personaggio_scelto = personaggio_corrente["codice"]

                        if personaggio_scelto == "M":
                            anims_corrente = anims_M
                            frames_animati = anim_M_forward
                        elif personaggio_scelto == "F":
                            anims_corrente = anims_F
                            frames_animati = anim_F_forward

                        stato_gioco = "SELEZIONE_LIVELLO"

        # --- SELEZIONA LIVELLO ---
        elif stato_gioco == "SELEZIONE_LIVELLO":

            screen.blit(img_seleziona_livello, (0, 0))

            mouse_pos = pygame.mouse.get_pos()

            pv_w, pv_h = 340, 210
            spacing = 70
            total_w = pv_w * 3 + spacing * 2
            start_x = LARGHEZZA // 2 - total_w // 2
            y = ALTEZZA // 2 - pv_h // 2 + 80   # leggermente più in basso per lasciare spazio al titolo

            # Ordine visivo (2 e 3 invertiti)
            previews = [preview1, preview3, preview2]

            # Mappa reale dei livelli
            mappa_livelli = [0, 2, 1]

            rects = []

            for i, pv in enumerate(previews):

                x = start_x + i * (pv_w + spacing)
                pv_scaled = pygame.transform.smoothscale(pv, (pv_w, pv_h))
                rect = pygame.Rect(x, y, pv_w, pv_h)
                rects.append(rect)

                # =============================
                # SCRITTA SOPRA L'IMMAGINE
                # =============================

                txt = font.render(f"LIVELLO {i+1}", True, (0, 0, 0))
                rect_txt = txt.get_rect(center=(x + pv_w // 2, y - 50))

                padding_x = 20
                padding_y = 10
                ombra_offset = 6

                # Rettangolo bianco
                rect_bg = pygame.Rect(
                    rect_txt.x - padding_x,
                    rect_txt.y - padding_y,
                    rect_txt.width + padding_x * 2,
                    rect_txt.height + padding_y * 2
                )

                # Rettangolo ombra
                rect_shadow = rect_bg.copy()
                rect_shadow.x += ombra_offset
                rect_shadow.y += ombra_offset

                # Disegno ombra
                shadow_surface = pygame.Surface((rect_shadow.width, rect_shadow.height), pygame.SRCALPHA)
                shadow_surface.fill((0, 0, 0, 110))
                screen.blit(shadow_surface, (rect_shadow.x, rect_shadow.y))

                # Disegno rettangolo bianco
                pygame.draw.rect(screen, (255, 255, 255), rect_bg, border_radius=14)

                # Disegno testo
                screen.blit(txt, rect_txt)

                # =============================
                # HIGHLIGHT HOVER
                # =============================
                if rect.collidepoint(mouse_pos):
                    pygame.draw.rect(screen, (255, 200, 0), rect.inflate(16, 16), 5, border_radius=18)
                else:
                    pygame.draw.rect(screen, (0, 0, 0), rect.inflate(10, 10), 3, border_radius=18)

                # Disegno preview
                screen.blit(pv_scaled, (x, y))

            # =============================
            # GESTIONE CLICK
            # =============================
            for e in event:
                if e.type == pygame.MOUSEBUTTONDOWN:
                    for i, r in enumerate(rects):
                        if r.collidepoint(e.pos):
                            livello_scelto = livelli_possibili[mappa_livelli[i]]
                            stato_gioco = "INIZIALIZZA"

        # --- INIZIALIZZA ---
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
            # Costruisci mappa di tile percorribili: tile non coincidono con muri o con tile "Fine"
            tile_w = getattr(tmx_data, 'tilewidth', 32)
            tile_h = getattr(tmx_data, 'tileheight', 32)
            map_w = tmx_data.width
            map_h = tmx_data.height


            passable_tiles = set()
            for ty in range(map_h):
                for tx in range(map_w):
                    tile_rect = pygame.Rect(tx*tile_w, ty*tile_h, tile_w, tile_h)
                    blocked = False
                    for m in muri:
                        if tile_rect.colliderect(m):
                            blocked = True
                            break
                    if blocked:
                        continue
                    # escludi tile di fine livello
                    for fr in fine_tiles:
                        if tile_rect.colliderect(fr):
                            blocked = True
                            break
                    if blocked:
                        continue
                    passable_tiles.add((tx, ty))


            grid_info = {
                'passable': passable_tiles,
                'tile_w': tile_w,
                'tile_h': tile_h,
                'map_w': map_w,
                'map_h': map_h
            }


            if(livello_scelto==livelli_possibili[0]):
                # Livello 1: Minotauro + Ghost
                pos_iniziale_giocatore = (90, 70)
                player = giocatore.Giocatore(90, 70, img_m_statica, frames_animati)
                nemico1 = nemico.Nemico(400, 400, img_minotauro, grid_info)
                nemico1.start_pos = (400, 400)
                nemico1.tipo = "MINOTAURO"
                nemico2 = nemico.Nemico(500, 300, img_ghost, grid_info)
                nemico2.start_pos = (500, 300)
                nemico2.tipo = "GHOST"
            elif(livello_scelto==livelli_possibili[1]):
                # Livello 2: Ghost + Scheletro Oro
                pos_iniziale_giocatore = (110, 390)
                player = giocatore.Giocatore(110, 390, img_m_statica, frames_animati)
                nemico1 = nemico.Nemico(500, 300, img_ghost, grid_info)
                nemico1.start_pos = (500, 300)
                nemico1.tipo = "GHOST"
                nemico2 = nemico.Nemico(600, 400, img_scheletro_oro, grid_info)
                nemico2.start_pos = (600, 400)
                nemico2.tipo = "SCHELETRO_ORO"
            else:
                # Livello 3: Ghost + Drago
                pos_iniziale_giocatore = (440, 580)
                player = giocatore.Giocatore(440, 580, img_m_statica, frames_animati)
                nemico1 = nemico.Nemico(500, 300, img_ghost, grid_info)
                nemico1.start_pos = (500, 300)
                nemico1.tipo = "GHOST"
                nemico2 = nemico.Nemico(600, 400, img_drago, grid_info)
                nemico2.start_pos = (600, 400)
                nemico2.tipo = "DRAGO"
            stato_gioco = "IN_GIOCO"  # Inizia il gioco


        # --- IN GIOCO ---
        elif stato_gioco == "IN_GIOCO":
            keys = pygame.key.get_pressed()  # Prendi lo stato di tutte le tastiere

            player.gyro.update()
            gyro = player.gyro.get_xyz()
           
            # Gestione animazioni in base alla direzione
            if anims_corrente:
                if gyro["y"] < -player.soglia:
                    player.frames = anims_corrente["up"]
                elif gyro["y"] > player.soglia:
                    player.frames = anims_corrente["down"]
                elif gyro["z"] > player.soglia:
                    player.frames = anims_corrente["left"]
                elif gyro["z"] < -player.soglia:
                    player.frames = anims_corrente["right"]

            player.eeg.update()
            eeg = player.eeg.get_band_powers()
            beta_value = eeg.get('Beta', 0)

            raggio_luce = raggio_luce_min + beta_value * (raggio_luce_max - raggio_luce_min)
           
            # Calcola movimento in base a come muovi la testa
            player.muovi(muri)
            if nemico1:
                nemico1.muovi_auto(muri)
            if nemico2:
                nemico2.muovi_auto(muri)


            # Controlla vittoria: se giocatore raggiunge l'uscita (oggetto) o una tile con classe "Fine"
            if rect_uscita and player.rect.colliderect(rect_uscita):
                stato_gioco = "VITTORIA"
            else:
                for fine_rect in fine_tiles:
                    if player.rect.colliderect(fine_rect):
                        stato_gioco = "VITTORIA"
                        break
            # Controlla sconfitta: se giocatore collide con nemico, apre domanda
            if nemico1 and player.rect.colliderect(nemico1.rect):
                domanda_attiva = random.choice(DOMANDE)
                nemico_che_ha_colpito = 1
                risposta_selezionata = None
                mostra_feedback = False
                indice_selezionato = 0
                cooldown_gyro = 0
                stato_gioco = "DOMANDA_RISPOSTA"
            if nemico2 and player.rect.colliderect(nemico2.rect):
                domanda_attiva = random.choice(DOMANDE)
                nemico_che_ha_colpito = 2
                risposta_selezionata = None
                mostra_feedback = False
                indice_selezionato = 0
                cooldown_gyro = 0
                stato_gioco = "DOMANDA_RISPOSTA"


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
            if nemico1:
                nemico1.draw(v_screen, (cam_x, cam_y))  # Disegna nemico1
            if nemico2:
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
            # Disegno finale
            screen.blit(pygame.transform.scale(v_screen, (LARGHEZZA, ALTEZZA)), (0, 0))
       
        elif stato_gioco == "DOMANDA_RISPOSTA":

            # ---------------------------
            # AGGIORNAMENTO GIROSCOPIO
            # ---------------------------
            player.gyro.update()
            gyro = player.gyro.get_xyz()

            if cooldown_gyro > 0:
                cooldown_gyro -= 1

            # ---------------------------
            # CONTROLLO TRAMITE TESTA
            # ---------------------------
            if not mostra_feedback and cooldown_gyro == 0:

                if gyro["y"] < -player.soglia:
                    indice_selezionato -= 1
                    if indice_selezionato < 0:
                        indice_selezionato = len(domanda_attiva["opzioni"]) - 1
                    cooldown_gyro = 15

                elif gyro["y"] > player.soglia:
                    indice_selezionato += 1
                    if indice_selezionato >= len(domanda_attiva["opzioni"]):
                        indice_selezionato = 0
                    cooldown_gyro = 15

                elif gyro["z"] < -player.soglia or gyro["z"] > player.soglia:

                    risposta_selezionata = indice_selezionato
                    feedback_colore = (
                        indice_selezionato == domanda_attiva["risposta_corretta"]
                    )

                    mostra_feedback = True
                    timer_feedback = 90
                    cooldown_gyro = 40

                    # -------- LOGICA RISPOSTA --------
                    if feedback_colore:
                        if nemico_che_ha_colpito == 1 and nemico1:
                            nemico1.rect.topleft = (-1000, -1000)
                        elif nemico_che_ha_colpito == 2 and nemico2:
                            nemico2.rect.topleft = (-1000, -1000)

                    else:
                        player.rect.topleft = pos_iniziale_giocatore
                        enemy_anim_timer = FPS * 2
                        enemy_anim_index = 0

            # ---------------------------
            # DISEGNO SFONDO
            # ---------------------------
            screen.blit(pygame.transform.scale(v_screen, (LARGHEZZA, ALTEZZA)), (0, 0))

            overlay = pygame.Surface((LARGHEZZA, ALTEZZA))
            overlay.set_alpha(80)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))

            # ---------------------------
            # FINESTRA DOMANDA
            # ---------------------------
            larghezza_finestra = 650
            altezza_finestra = 400
            x_finestra = LARGHEZZA // 2 - larghezza_finestra // 2
            y_finestra = ALTEZZA // 2 - altezza_finestra // 2

            pygame.draw.rect(screen, (255, 255, 255),
                            (x_finestra, y_finestra, larghezza_finestra, altezza_finestra))
            pygame.draw.rect(screen, (0, 0, 0),
                            (x_finestra, y_finestra, larghezza_finestra, altezza_finestra), 3)

            # Testo domanda
            font_domanda = pygame.font.SysFont("Arial", 24, bold=True)
            txt_domanda = font_domanda.render(domanda_attiva["testo"], True, (0, 0, 0))
            screen.blit(txt_domanda, (x_finestra + 30, y_finestra + 20))

            # ---------------------------
            # OPZIONI
            # ---------------------------
            font_opzioni = pygame.font.SysFont("Arial", 18)
            lettere = ['A', 'B', 'C', 'D']

            for i, opzione in enumerate(domanda_attiva["opzioni"]):

                y_opzione = y_finestra + 100 + i * 60
                x_opzione = x_finestra + 30
                rect_opt = pygame.Rect(x_opzione, y_opzione,
                                    larghezza_finestra - 60, 50)

                if mostra_feedback:
                    if i == domanda_attiva["risposta_corretta"]:
                        colore = (0, 200, 0)
                    elif i == risposta_selezionata:
                        colore = (200, 0, 0)
                    else:
                        colore = (200, 200, 200)
                else:
                    if i == indice_selezionato:
                        colore = (255, 255, 150)
                    else:
                        colore = (200, 200, 200)

                pygame.draw.rect(screen, colore, rect_opt)
                pygame.draw.rect(screen, (0, 0, 0), rect_opt, 2)

                txt_lettera = font_opzioni.render(f"{lettere[i]})", True, (0, 0, 0))
                txt_opzione = font_opzioni.render(opzione, True, (0, 0, 0))

                screen.blit(txt_lettera, (x_opzione + 15, y_opzione + 10))
                screen.blit(txt_opzione, (x_opzione + 60, y_opzione + 10))

            # ---------------------------
            # TIMER FEEDBACK
            # ---------------------------
            if mostra_feedback:
                timer_feedback -= 1
                if timer_feedback <= 0:
                    stato_gioco = "IN_GIOCO"
                    mostra_feedback = False
                    timer_feedback = 0


        
        # --- IMPOSTAZIONI ---
        elif stato_gioco == "IMPOSTAZIONI":
            screen.fill((40, 40, 40))  # Sfondo grigio scuro
            
            font_titolo = pygame.font.SysFont("Arial", 60, bold=True)
            font_normale = pygame.font.SysFont("Arial", 30)
            font_piccolo = pygame.font.SysFont("Arial", 24)
            
            # Titolo centrato
            txt_titolo = font_titolo.render("IMPOSTAZIONI", True, (255, 255, 255))
            screen.blit(txt_titolo, (larghezza_attuale // 2 - txt_titolo.get_width() // 2, 180))
            
            y_start = 350
            spacing = 120
            
            # Calibrazione Audio
            txt_audio = font_normale.render("Audio:", True, (255, 255, 255))
            screen.blit(txt_audio, (larghezza_attuale // 2 - txt_audio.get_width() // 2, y_start))
            
            # Slider volume
            slider_x = larghezza_attuale // 2 - 200
            slider_y = y_start + 50
            slider_w = 400
            slider_h = 30
            slider_rect = pygame.Rect(slider_x, slider_y, slider_w, slider_h)
            pygame.draw.rect(screen, (100, 100, 100), slider_rect)
            pygame.draw.rect(screen, (255, 255, 255), slider_rect, 2)
            
            # Indicatore volume
            indicator_x = slider_x + int(volume_audio * slider_w)
            pygame.draw.circle(screen, (255, 255, 255), (indicator_x, slider_y + slider_h // 2), 15)
            pygame.draw.line(screen, (0, 200, 0), (slider_x, slider_y + slider_h // 2), 
                           (indicator_x, slider_y + slider_h // 2), 4)
            
            # Valore volume (centrato sotto lo slider)
            txt_volume_val = font_piccolo.render(f"{int(volume_audio * 100)}%", True, (255, 255, 255))
            screen.blit(txt_volume_val, (larghezza_attuale // 2 - txt_volume_val.get_width() // 2, slider_y + slider_h + 10))
            
            # Pulsante Istruzioni
            btn_istruzioni_w = 300
            btn_istruzioni_h = 60
            btn_istruzioni_x = larghezza_attuale // 2 - btn_istruzioni_w // 2
            btn_istruzioni_y = y_start + spacing + 20
            btn_istruzioni = pygame.Rect(btn_istruzioni_x, btn_istruzioni_y, btn_istruzioni_w, btn_istruzioni_h)
            
            col_istruzioni = (100, 100, 200) if btn_istruzioni.collidepoint(mouse_pos) else (70, 70, 150)
            pygame.draw.rect(screen, col_istruzioni, btn_istruzioni, border_radius=15)
            txt_istruzioni = font_normale.render("COME FUNZIONA", True, (255, 255, 255))
            screen.blit(txt_istruzioni, (btn_istruzioni.centerx - txt_istruzioni.get_width() // 2, 
                                        btn_istruzioni.centery - txt_istruzioni.get_height() // 2))
            
            # Pulsante Indietro (avvicinato al centro)
            btn_indietro_w = 200
            btn_indietro_h = 60
            btn_indietro_x = larghezza_attuale // 2 - btn_indietro_w // 2
            btn_indietro_y = altezza_attuale // 2 + 200
            btn_indietro = pygame.Rect(btn_indietro_x, btn_indietro_y, btn_indietro_w, btn_indietro_h)
            
            col_indietro = (150, 0, 0) if btn_indietro.collidepoint(mouse_pos) else (100, 0, 0)
            pygame.draw.rect(screen, col_indietro, btn_indietro, border_radius=15)
            txt_indietro = font_normale.render("INDIETRO", True, (255, 255, 255))
            screen.blit(txt_indietro, (btn_indietro.centerx - txt_indietro.get_width() // 2, 
                                      btn_indietro.centery - txt_indietro.get_height() // 2))
            
            # Gestione input
            for e in event:
                if e.type == pygame.MOUSEBUTTONDOWN:
                    # Click su slider volume
                    if slider_rect.collidepoint(e.pos):
                        rel_x = e.pos[0] - slider_x
                        volume_audio = max(0.0, min(1.0, rel_x / slider_w))
                        pygame.mixer.music.set_volume(volume_audio)
                    
                    # Click su istruzioni
                    elif btn_istruzioni.collidepoint(e.pos):
                        stato_gioco = "ISTRUZIONI"
                    
                    # Click su indietro
                    elif btn_indietro.collidepoint(e.pos):
                        stato_gioco = "MENU_PRINCIPALE"
            
            # Gestione drag slider volume
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0] and slider_rect.collidepoint(mouse_pos):
                rel_x = mouse_pos[0] - slider_x
                volume_audio = max(0.0, min(1.0, rel_x / slider_w))
                pygame.mixer.music.set_volume(volume_audio)
        
        # STATO: Istruzioni
        elif stato_gioco == "ISTRUZIONI":
            screen.fill((40, 40, 40))  # Sfondo grigio scuro
            
            font_titolo = pygame.font.SysFont("Arial", 60, bold=True)
            font_normale = pygame.font.SysFont("Arial", 28)
            font_piccolo = pygame.font.SysFont("Arial", 22)
            
            # Titolo centrato
            txt_titolo = font_titolo.render("COME FUNZIONA IL GIOCO", True, (255, 255, 255))
            screen.blit(txt_titolo, (larghezza_attuale // 2 - txt_titolo.get_width() // 2, 120))
            
            # Testo istruzioni
            istruzioni = [
                "Benvenuto in TeaMaze!",
                "",
                "OBIETTIVO:",
                "Raggiungi l'uscita del labirinto evitando i nemici.",
                "",
                "CONTROLLI:",
                "- Muovi la testa nella direzione in cui desideri far andare il personaggio",
                "- Concentrati per muovere il personaggio in quella direzione",
                "",
                "NEMICI:",
                "Se un nemico ti cattura, dovrai rispondere a una domanda.",
                "Rispondi correttamente per eliminare il nemico.",
                "Rispondi sbagliato e tornerai all'inizio del livello.",
                "",
                "Buona fortuna!"
            ]
            
            y_start = 200
            line_height = 35
            for i, riga in enumerate(istruzioni):
                if riga:
                    colore = (255, 255, 255) if i == 0 else (200, 200, 200) if riga.endswith(":") else (180, 180, 180)
                    font_uso = font_normale if (i == 0 or riga.endswith(":")) else font_piccolo
                    txt_riga = font_uso.render(riga, True, colore)
                    screen.blit(txt_riga, (larghezza_attuale // 2 - txt_riga.get_width() // 2, y_start + i * line_height))
            
            # Pulsante Indietro
            btn_indietro_w = 200
            btn_indietro_h = 60
            btn_indietro_x = larghezza_attuale // 2 - btn_indietro_w // 2
            btn_indietro_y = altezza_attuale - 200
            btn_indietro = pygame.Rect(btn_indietro_x, btn_indietro_y, btn_indietro_w, btn_indietro_h)
            
            col_indietro = (150, 0, 0) if btn_indietro.collidepoint(mouse_pos) else (100, 0, 0)
            pygame.draw.rect(screen, col_indietro, btn_indietro, border_radius=15)
            txt_indietro = font_normale.render("INDIETRO", True, (255, 255, 255))
            screen.blit(txt_indietro, (btn_indietro.centerx - txt_indietro.get_width() // 2, 
                                      btn_indietro.centery - txt_indietro.get_height() // 2))
            
            # Gestione click
            for e in event:
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if btn_indietro.collidepoint(e.pos):
                        stato_gioco = "IMPOSTAZIONI"
       
        # STATO: Vittoria
        elif stato_gioco == "VITTORIA":
            screen.fill((0, 80, 0))  # Sfondo verde scuro
            txt = font.render("SEI FUGGITO!!!!!", True, (255, 255, 255))  # Testo vittoria bianco
            screen.blit(txt, (LARGHEZZA//2 - txt.get_width()//2, ALTEZZA//2 - 50))  # Disegna testo centrato
            for e in event:  # Controlla input
                if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE: stato_gioco = "MENU_PRINCIPALE"  # SPAZIO = ritorna al menu


        # Aggiorna la finestra e limita FPS
        pygame.display.flip()  # Aggiorna il display
        clock.tick(FPS)  # Limita a 60 FPS


# Punto di ingresso del programma
if __name__ == "__main__":
    main()  # Avvia il gioco
