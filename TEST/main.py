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
from museGYRO import MuseGYRO
   


def main():
    # Funzione principale del gioco
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

    def scrivi_testo_descrizione(stato_gioco):
        font_descrizione = pygame.font.SysFont("Arial", 22, italic=True)
        descr_text = descrizioni_stati[stato_gioco]
        txt_descrizione = font_descrizione.render(descr_text, True, (220, 220, 220))
        # Posizione centrale orizzontale e verticale a 250px (puoi cambiare)
        x_text = larghezza_attuale // 2 - txt_descrizione.get_width() // 2
        y_text = altezza_attuale - 150
        # Rettangolo ombra sotto la scritta
        padding_x = 10  # spazio orizzontale attorno al testo
        padding_y = 5   # spazio verticale attorno al testo
        rect_ombra = pygame.Rect(
            x_text - padding_x,
            y_text - padding_y,
            txt_descrizione.get_width() + 2 * padding_x,
            txt_descrizione.get_height() + 2 * padding_y
        )
        # Superficie trasparente per l'ombra
        ombra_surface = pygame.Surface((rect_ombra.width, rect_ombra.height), pygame.SRCALPHA)
        ombra_surface.fill((0, 0, 0, 100))  # nero semi-trasparente (alpha 100/255)
        screen.blit(ombra_surface, (rect_ombra.x, rect_ombra.y))
        # Disegno del testo sopra il rettangolo
        screen.blit(txt_descrizione, (x_text, y_text))
   
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

    try:
        # Carica lo sfondo della vittoria
        img_vittoria = pygame.image.load(os.path.join(IMG_DIR, "sfondoVittoria.webp")).convert()
        img_vittoria = pygame.transform.scale(img_vittoria, (LARGHEZZA, ALTEZZA))
    except:
        # Fallback se l'immagine manca
        img_vittoria = pygame.Surface((LARGHEZZA, ALTEZZA))
        img_vittoria.fill((20, 20, 20))


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

    # DESCRIZIONE DI COSA BISOGNA FARE IN CIASCUNO STATO
    descrizioni_stati = {
        "MENU_PRINCIPALE": "Muovi la testa su/giù per navigare nel menu e conferma con destra/sinistra.",
        "SELEZIONE_PERSONAGGIO": "Muovi la testa a destra/sinistra per cambiare personaggio, su/giù per confermare.",
        "SELEZIONE_LIVELLO": "Muovi la testa a destra/sinistra per selezionare un livello, su/giù per confermare.",
        "IN_GIOCO": "Muovi la testa nella direzione desiderata per muovere il personaggio.",
        "DOMANDA_RISPOSTA": "Muovi la testa su/giù per selezionare la risposta, destra/sinistra per confermare.",
        "IMPOSTAZIONI": "Muovi la testa su/giù per selezionare voce, destra/sinistra per modificare o confermare.",
        "ISTRUZIONI": "Muovi la testa in qualunque direzione per tornare alle impostazioni.",
        "VITTORIA": "Muovi la testa in qualunque direzione per tornare al menù principale.",
    }

    
    cooldown_gyro = 0
    indice_menu = 0
    voci_menu = ["GIOCA", "IMPOSTAZIONI", "USCITA"]
    indice_personaggio = 0          # Indice del personaggio mostrato nel menu
    indice_frame_personaggio = 0    # Indice del frame GIF nel menu
    indice_livello = 0
    indice_impostazioni = 0
    sogliaGYRO = 180
    gyro = MuseGYRO()
    if gyro.connect():
        print("Muse GYRO pronto")
    else:
        print("Muse GYRO non trovato, useremo valori simulati")

    # Loop principale del gioco
    while True:
        event = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()
        # --- MENU PRINCIPALE ---
        if stato_gioco == "MENU_PRINCIPALE":
            #MUSICA
            play_music(MUSIC_FILES["MENU"])

            # AGGIORNAMENTO GIRO
            gyro.update()
            gyro_value = gyro.get_xyz()

            if cooldown_gyro > 0:
                cooldown_gyro -= 1

            # CONTROLLO TESTA
            if cooldown_gyro == 0:

                # SU
                if gyro_value["y"] < -sogliaGYRO:
                    indice_menu -= 1
                    if indice_menu < 0:
                        indice_menu = len(voci_menu) - 1
                    cooldown_gyro = 15

                # GIÙ
                elif gyro_value["y"] > sogliaGYRO:
                    indice_menu += 1
                    if indice_menu >= len(voci_menu):
                        indice_menu = 0
                    cooldown_gyro = 15

                # CONFERMA con movimento testa
                elif gyro_value["z"] < -sogliaGYRO or gyro_value["z"] > sogliaGYRO:
                    cooldown_gyro = 40
                    if indice_menu == 0:
                        stato_gioco = "SELEZIONE_PERSONAGGIO"
                        indice_menu = 0
                    elif indice_menu == 1:
                        stato_gioco = "IMPOSTAZIONI"
                        indice_menu = 0
                    elif indice_menu == 2:
                        pygame.quit()
                        sys.exit()

            # DISEGNO MENU
            larghezza_btn, altezza_btn = 350, 80
            cx = larghezza_attuale // 2 - larghezza_btn // 2

            rect_gioca = pygame.Rect(cx, altezza_attuale // 2 + 50, larghezza_btn, altezza_btn)
            rect_impostazioni = pygame.Rect(cx, altezza_attuale // 2 + 160, larghezza_btn, altezza_btn)
            rect_uscita = pygame.Rect(cx, altezza_attuale // 2 + 270, larghezza_btn, altezza_btn)

            pulsanti = [rect_gioca, rect_impostazioni, rect_uscita]

            screen.blit(img_menu, (0, 0))

            # TESTO DESCRIZIONE
            scrivi_testo_descrizione(stato_gioco)


            for i, rect in enumerate(pulsanti):

                # Colori normali
                if i == 0:
                    colore = (0, 130, 0)
                elif i == 1:
                    colore = (70, 70, 70)
                else:
                    colore = (130, 0, 0)

                # Evidenzia selezione
                if i == indice_menu:
                    colore = (100, 200, 255)

                pygame.draw.rect(screen, colore, rect, border_radius=15)

                txt = font.render(voci_menu[i], True, (255, 255, 255))
                screen.blit(txt, (
                    rect.centerx - txt.get_width() // 2,
                    rect.centery - txt.get_height() // 2
                ))
 
        # --- SELEZIONA PERSONAGGIO ---
        elif stato_gioco == "SELEZIONE_PERSONAGGIO":
            # AGGIORNAMENTO GIROSCOPIO
            gyro.update()
            gyro_value = gyro.get_xyz()


            if cooldown_gyro > 0:
                cooldown_gyro -= 1

            # CONTROLLO TESTA
            if cooldown_gyro == 0:

                # Cambio personaggio
                if gyro_value["z"] > sogliaGYRO:
                    indice_personaggio = (indice_personaggio - 1) % len(personaggi)
                    indice_frame_personaggio = 0
                    cooldown_gyro = 15
                elif gyro_value["z"] < -sogliaGYRO:
                    indice_personaggio = (indice_personaggio + 1) % len(personaggi)
                    indice_frame_personaggio = 0
                    cooldown_gyro = 15

                # Conferma selezione con su/giu
                elif gyro_value["y"] < -sogliaGYRO or gyro_value["y"] > sogliaGYRO:
                    personaggio_corrente = personaggi[indice_personaggio]
                    personaggio_scelto = personaggio_corrente["codice"]

                    if personaggio_scelto == "M":
                        anims_corrente = anims_M
                        frames_animati = anim_M_forward
                    elif personaggio_scelto == "F":
                        anims_corrente = anims_F
                        frames_animati = anim_F_forward

                    stato_gioco = "SELEZIONE_LIVELLO"
                    cooldown_gyro = 40

            # DISEGNO PERSONAGGIO
            screen.blit(img_seleziona_personaggio, (0, 0))

            # TESTO DESCRIZIONE
            scrivi_testo_descrizione(stato_gioco)

            # Rettangoli frecce sinistra/destra (solo estetica)
            btn_sx = pygame.Rect(LARGHEZZA // 2 - 250, ALTEZZA // 2 - 60, 80, 80)
            btn_dx = pygame.Rect(LARGHEZZA // 2 + 170, ALTEZZA // 2 - 60, 80, 80)

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

            # Nome con sfondo e ombra
            txt_nome = font.render(personaggio_corrente["nome"], True, (0, 0, 0))
            rect_nome = txt_nome.get_rect(center=(LARGHEZZA // 2, 160))

            padding_x = 20
            padding_y = 10
            ombra_offset = 6

            rect_sfondo = pygame.Rect(
                rect_nome.x - padding_x,
                rect_nome.y - padding_y,
                rect_nome.width + padding_x * 2,
                rect_nome.height + padding_y * 2
            )
            rect_ombra = rect_sfondo.copy()
            rect_ombra.x += ombra_offset
            rect_ombra.y += ombra_offset

            ombra_surface = pygame.Surface((rect_ombra.width, rect_ombra.height), pygame.SRCALPHA)
            ombra_surface.fill((0, 0, 0, 100))
            screen.blit(ombra_surface, (rect_ombra.x, rect_ombra.y))

            pygame.draw.rect(screen, (255, 255, 255), rect_sfondo, border_radius=12)
            screen.blit(txt_nome, rect_nome)

            # Disegno frecce SX/DX (solo estetica)
            txt_sx = font.render("<", True, (0, 0, 0))
            txt_dx = font.render(">", True, (0, 0, 0))
            pygame.draw.rect(screen, (220,220,220), btn_sx, border_radius=15)
            pygame.draw.rect(screen, (220,220,220), btn_dx, border_radius=15)
            screen.blit(txt_sx, (btn_sx.centerx - txt_sx.get_width() // 2,
                                btn_sx.centery - txt_sx.get_height() // 2))
            screen.blit(txt_dx, (btn_dx.centerx - txt_dx.get_width() // 2,
                                btn_dx.centery - txt_dx.get_height() // 2))

        # --- SELEZIONA LIVELLO ---
        elif stato_gioco == "SELEZIONE_LIVELLO":
            # AGGIORNAMENTO GIROSCOPIO
            gyro.update()
            gyro_value = gyro.get_xyz()

            if cooldown_gyro > 0:
                cooldown_gyro -= 1

            # CONTROLLO TESTA
            if cooldown_gyro == 0:

                # Cambio livello con destra/sinistra (asse Z)
                if gyro_value["z"] < -sogliaGYRO:
                    indice_livello = (indice_livello + 1) % 3
                    cooldown_gyro = 15

                elif gyro_value["z"] > sogliaGYRO:
                    indice_livello = (indice_livello - 1) % 3
                    cooldown_gyro = 15

                # Conferma con su/giu (asse Y come nel personaggio)
                elif gyro_value["y"] < -sogliaGYRO or gyro_value["y"] > sogliaGYRO:
                    livello_scelto = livelli_possibili[mappa_livelli[indice_livello]]
                    stato_gioco = "INIZIALIZZA"
                    cooldown_gyro = 40

            # DISEGNO LIVELLI
            screen.blit(img_seleziona_livello, (0, 0))

            # TESTO DESCRIZIONE
            scrivi_testo_descrizione("SELEZIONE_LIVELLO")

            pv_w, pv_h = 340, 210
            spacing = 70
            total_w = pv_w * 3 + spacing * 2
            start_x = LARGHEZZA // 2 - total_w // 2
            y = ALTEZZA // 2 - pv_h // 2 + 80

            previews = [preview1, preview3, preview2]
            mappa_livelli = [0, 2, 1]

            for i, pv in enumerate(previews):

                x = start_x + i * (pv_w + spacing)
                pv_scaled = pygame.transform.smoothscale(pv, (pv_w, pv_h))
                rect_preview = pygame.Rect(x, y, pv_w, pv_h)

                screen.blit(pv_scaled, rect_preview)

                # Evidenzia livello selezionato
                if i == indice_livello:
                    pygame.draw.rect(screen, (0, 255, 0),
                                    rect_preview.inflate(20, 20),
                                    6, border_radius=20)
                else:
                    pygame.draw.rect(screen, (0, 0, 0),
                                    rect_preview.inflate(10, 10),
                                    3, border_radius=18)

                # TESTO SOPRA IMMAGINE
                txt = font.render(f"MAPPA {i+1}", True, (0, 0, 0))
                rect_txt = txt.get_rect(center=(x + pv_w // 2, y - 50))

                padding_x = 20
                padding_y = 10
                ombra_offset = 6

                rect_bg = pygame.Rect(
                    rect_txt.x - padding_x,
                    rect_txt.y - padding_y,
                    rect_txt.width + padding_x * 2,
                    rect_txt.height + padding_y * 2
                )

                rect_shadow = rect_bg.copy()
                rect_shadow.x += ombra_offset
                rect_shadow.y += ombra_offset

                shadow_surface = pygame.Surface((rect_shadow.width, rect_shadow.height), pygame.SRCALPHA)
                shadow_surface.fill((0, 0, 0, 110))
                screen.blit(shadow_surface, (rect_shadow.x, rect_shadow.y))

                pygame.draw.rect(screen, (255, 255, 255), rect_bg, border_radius=14)
                screen.blit(txt, rect_txt)

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
            #MUSICA
            if livello_scelto == 1:
                play_music(MUSIC_FILES["LIVELLO1"])
            elif livello_scelto == 2:
                play_music(MUSIC_FILES["LIVELLO2"])
            else:
                play_music(MUSIC_FILES["LIVELLO3"])
            gyro.update()
            gyro_value = gyro.get_xyz()
           
            # Gestione animazioni in base alla direzione
            if anims_corrente:
                if gyro_value["y"] < -sogliaGYRO:
                    player.frames = anims_corrente["up"]
                elif gyro_value["y"] > sogliaGYRO:
                    player.frames = anims_corrente["down"]
                elif gyro_value["z"] > sogliaGYRO:
                    player.frames = anims_corrente["left"]
                elif gyro_value["z"] < -sogliaGYRO:
                    player.frames = anims_corrente["right"]

            player.eeg.update()
            eeg = player.eeg.get_band_powers()
            beta_value = eeg.get('Beta', 0)

            raggio_luce = raggio_luce_min + beta_value * (raggio_luce_max - raggio_luce_min)
           
            # Calcola movimento in base a come muovi la testa
            player.muovi(gyro_value, muri)
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

            # TESTO DESCRIZIONE
            scrivi_testo_descrizione(stato_gioco)

            # --- INTERFACCIA (UI) ---
            # Disegno finale
            screen.blit(pygame.transform.scale(v_screen, (LARGHEZZA, ALTEZZA)), (0, 0))
       
        elif stato_gioco == "DOMANDA_RISPOSTA":
            # AGGIORNAMENTO GIROSCOPIO
            gyro.update()
            gyro_value = gyro.get_xyz()

            if cooldown_gyro > 0:
                cooldown_gyro -= 1

            # CONTROLLO TRAMITE TESTA
            if not mostra_feedback and cooldown_gyro == 0:

                if gyro_value["y"] < -sogliaGYRO:
                    indice_selezionato -= 1
                    if indice_selezionato < 0:
                        indice_selezionato = len(domanda_attiva["opzioni"]) - 1
                    cooldown_gyro = 15

                elif gyro_value["y"] > sogliaGYRO:
                    indice_selezionato += 1
                    if indice_selezionato >= len(domanda_attiva["opzioni"]):
                        indice_selezionato = 0
                    cooldown_gyro = 15

                elif gyro_value["z"] < -sogliaGYRO or gyro_value["z"] > sogliaGYRO:

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

            # DISEGNO SFONDO
            screen.blit(pygame.transform.scale(v_screen, (LARGHEZZA, ALTEZZA)), (0, 0))

            # TESTO DESCRIZIONE
            scrivi_testo_descrizione(stato_gioco)

            overlay = pygame.Surface((LARGHEZZA, ALTEZZA))
            overlay.set_alpha(80)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))

            # FINESTRA DOMANDA
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

            # OPZIONI
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

            # TIMER FEEDBACK
            if mostra_feedback:
                timer_feedback -= 1
                if timer_feedback <= 0:
                    stato_gioco = "IN_GIOCO"
                    mostra_feedback = False
                    timer_feedback = 0


        
        # --- IMPOSTAZIONI ---
        elif stato_gioco == "IMPOSTAZIONI":
            # AGGIORNAMENTO GIROSCOPIO
            gyro.update()
            gyro_value = gyro.get_xyz()

            if cooldown_gyro > 0:
                cooldown_gyro -= 1

            # CONTROLLO TESTA
            if cooldown_gyro == 0:

                # CAMBIO VOCE con SU/GIU (asse Y)
                if gyro_value["y"] > sogliaGYRO:
                    indice_impostazioni = (indice_impostazioni + 1) % 3
                    cooldown_gyro = 15
                elif gyro_value["y"] < -sogliaGYRO:
                    indice_impostazioni = (indice_impostazioni - 1) % 3
                    cooldown_gyro = 15

                # SELEZIONE con DESTRA/SINISTRA (asse Z)
                elif gyro_value["z"] > sogliaGYRO:
                    if indice_impostazioni == 0:
                        volume_audio = max(0.0, volume_audio - 0.05)
                        pygame.mixer.music.set_volume(volume_audio)
                    elif indice_impostazioni == 1:
                        stato_gioco = "ISTRUZIONI"
                    elif indice_impostazioni == 2:
                        stato_gioco = "MENU_PRINCIPALE"
                    cooldown_gyro = 20

                elif gyro_value["z"] < -sogliaGYRO:
                    if indice_impostazioni == 0:
                        volume_audio = min(1.0, volume_audio + 0.05)
                        pygame.mixer.music.set_volume(volume_audio)
                    elif indice_impostazioni == 1:
                        stato_gioco = "ISTRUZIONI"
                    elif indice_impostazioni == 2:
                        stato_gioco = "MENU_PRINCIPALE"
                    cooldown_gyro = 20

            # DISEGNO GRAFICA
            screen.fill((40, 40, 40))

            # TESTO DESCRIZIONE
            scrivi_testo_descrizione(stato_gioco)

            font_titolo = pygame.font.SysFont("Arial", 60, bold=True)
            font_normale = pygame.font.SysFont("Arial", 30)
            font_piccolo = pygame.font.SysFont("Arial", 24)

            txt_titolo = font_titolo.render("IMPOSTAZIONI", True, (255, 255, 255))
            screen.blit(txt_titolo, (larghezza_attuale // 2 - txt_titolo.get_width() // 2, 180))

            y_start = 350
            spacing = 120

            # AUDIO
            txt_audio = font_normale.render("Audio:", True, (255, 255, 255))
            rect_audio = txt_audio.get_rect(center=(larghezza_attuale // 2, y_start))

            # Rettangolo verde / azzurro se selezionato
            colore_audio_rect = (173, 216, 230) if indice_impostazioni == 0 else (0, 150, 0)  # azzurro chiaro se selezionato
            rect_sfondo_audio = pygame.Rect(
                rect_audio.x - 20,
                rect_audio.y - 10,
                rect_audio.width + 40,
                rect_audio.height + 20
            )
            pygame.draw.rect(screen, colore_audio_rect, rect_sfondo_audio, border_radius=12)
            screen.blit(txt_audio, rect_audio)

            # Slider volume
            slider_x = larghezza_attuale // 2 - 200
            slider_y = y_start + 50
            slider_w = 400
            slider_h = 30
            slider_rect = pygame.Rect(slider_x, slider_y, slider_w, slider_h)

            pygame.draw.rect(screen, (100, 100, 100), slider_rect)
            pygame.draw.rect(screen, (255, 255, 255), slider_rect, 2)

            indicator_x = slider_x + int(volume_audio * slider_w)
            pygame.draw.circle(screen, (255, 255, 255), (indicator_x, slider_y + slider_h // 2), 15)
            pygame.draw.line(screen, (0, 200, 0), (slider_x, slider_y + slider_h // 2), (indicator_x, slider_y + slider_h // 2), 4)

            txt_volume_val = font_piccolo.render(f"{int(volume_audio * 100)}%", True, (255, 255, 255))
            screen.blit(txt_volume_val, (larghezza_attuale // 2 - txt_volume_val.get_width() // 2, slider_y + slider_h + 10))

            # ISTRUZIONI
            txt_istruzioni = font_normale.render("COME FUNZIONA", True, (255, 255, 255))
            rect_istruzioni = txt_istruzioni.get_rect(center=(larghezza_attuale // 2, y_start + spacing + 50))

            colore_istruzioni_rect = (173, 216, 230) if indice_impostazioni == 1 else (150, 150, 150)  # azzurro chiaro se selezionato
            rect_sfondo_istruzioni = pygame.Rect(
                rect_istruzioni.x - 20,
                rect_istruzioni.y - 10,
                rect_istruzioni.width + 40,
                rect_istruzioni.height + 20
            )
            pygame.draw.rect(screen, colore_istruzioni_rect, rect_sfondo_istruzioni, border_radius=12)
            screen.blit(txt_istruzioni, rect_istruzioni)

            # INDIETRO
            txt_indietro = font_normale.render("INDIETRO", True, (255, 255, 255))
            rect_indietro = txt_indietro.get_rect(center=(larghezza_attuale // 2, altezza_attuale // 2 + 200))

            colore_indietro_rect = (173, 216, 230) if indice_impostazioni == 2 else (200, 0, 0)  # azzurro chiaro se selezionato
            rect_sfondo_indietro = pygame.Rect(
                rect_indietro.x - 20,
                rect_indietro.y - 10,
                rect_indietro.width + 40,
                rect_indietro.height + 20
            )
            pygame.draw.rect(screen, colore_indietro_rect, rect_sfondo_indietro, border_radius=12)
            screen.blit(txt_indietro, rect_indietro)

        
        # --- ISTRUZIONI ---
        elif stato_gioco == "ISTRUZIONI":
            screen.fill((40, 40, 40))  # Sfondo grigio scuro

            # TESTO DESCRIZIONE
            scrivi_testo_descrizione(stato_gioco)

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
                "- Raggiungi l'uscita del labirinto evitando i nemici.",
                "",
                "CONTROLLI:",
                "- Muovi la testa nella direzione in cui desideri far andare il personaggio",
                "- Concentrati per muovere il personaggio in quella direzione",
                "",
                "NEMICI:",
                "- Se un nemico ti cattura, dovrai rispondere a una domanda.",
                "- Rispondi correttamente per eliminare il nemico.",
                "- Rispondi sbagliato e tornerai all'inizio del livello.",
                "",
                "DOMANDA:",
                "- Muovi la testa su e giù per scegliere la risposta",
                "- Muovi la testa a destra o a sinistra per confermare la risposta",
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

            # GESTIONE GIROSCOPIO
            gyro.update()
            gyro_value = gyro.get_xyz()

            if cooldown_gyro > 0:
                cooldown_gyro -= 1

            if cooldown_gyro == 0:
                # Se la testa si muove in qualsiasi direzione → esci dallo stato ISTRUZIONI
                if (abs(gyro_value["x"]) > sogliaGYRO or 
                    abs(gyro_value["y"]) > sogliaGYRO or 
                    abs(gyro_value["z"]) > sogliaGYRO):
                    stato_gioco = "IMPOSTAZIONI"
                    cooldown_gyro = 20

       
        # --- VITTORIA ---
        elif stato_gioco == "VITTORIA":
            screen.blit(img_vittoria, (0, 0))

            # TESTO DESCRIZIONE
            scrivi_testo_descrizione(stato_gioco)

            txt = font.render("SEI FUGGITO!!!!!", True, (0, 0, 0))  # Testo vittoria bianco
            screen.blit(txt, (LARGHEZZA//2 - txt.get_width()//2, ALTEZZA//2 - 50))  # Disegna testo centrato
            player.gyro.update()
            gyro_value = player.gyro.get_xyz()

            if gyro_value["y"] > player.soglia or gyro_value["y"] < -player.soglia or gyro_value["z"] > player.soglia or gyro_value["y"] < -player.soglia:
                stato_gioco = "MENU_PRINCIPALE"
                cooldown_gyro = 0
                # SVUOTO IL BUFFER DEL MUSE
                gyro.clear_buffer()
            
        # Aggiorna la finestra e limita FPS
        pygame.display.flip()  # Aggiorna il display
        clock.tick(FPS)  # Limita a 60 FPS


# Punto di ingresso del programma
if __name__ == "__main__":
    main()  # Avvia il gioco
