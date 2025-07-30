import pygame
import sys
import os

# Importar constantes generales desde biblioteca.py
from biblioteca import ( # <-- CAMBIADO DE 'constants' a 'biblioteca'
    SCREEN_WIDTH, SCREEN_HEIGHT, FONT_LARGE, MAGIC_BLUE, WHITE, DARK_GREY,
    MENU_BACKGROUND_PATH, MENU_MUSIC_PATH
)

from guardar import save_game, load_game, get_saved_games
from interfaz import LoadGameScreen

# Importar las clases de cada escena.
# ¡NOMBRES DE ARCHIVO ORIGINALES MANTENIDOS!
from aldea import AldeaScene, global_selected_character_g # ARCHIVO 'aldea.py'
from escenario_mazmorra import MazmorraScene # ARCHIVO 'escenario_mazmorra.py'

# Importar las escenas que están dentro de la carpeta 'levels'
# ¡NOMBRES DE ARCHIVO ORIGINALES MANTENIDOS!
from levels.p1_mazmorra import P1MazmorraScene
from levels.jefe_1 import Jefe1Scene
from levels.p2_mazmorra import P2MazmorraScene
from levels.jefe_2 import Jefe2Scene
from levels.p3_mazmorra import P3MazmorraScene
from levels.jefe_3 import Jefe3Scene


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Elemental Trinity")

# --- MAPA DE ESCENAS COMPLETO Y ACTUALIZADO ---
# Las claves deben coincidir con los `next_scene_name` en tus clases de escena.
# Los valores son las clases de las escenas.
# ¡CLAVES DE ESCENA AHORA COINCIDEN CON LA NOMENCLATURA QUE HAS ESTADO USANDO!
# Y los valores son las clases importadas de los ARCHIVOS ORIGINALES.
scene_map = {
    "aldea_scene": AldeaScene,        # La clase AldeaScene está en aldea.py
    "mazmorra_scene": MazmorraScene,  # La clase MazmorraScene está en escenario_mazmorra.py
    "mazmorrap1": P1MazmorraScene,    # La clase P1MazmorraScene está en levels/p1_mazmorra.py
    "mazmorrajefe1": Jefe1Scene,      # La clase Jefe1Scene está en levels/jefe_1.py
    "mazmorrap2": P2MazmorraScene,    # La clase P2MazmorraScene está en levels/p2_mazmorra.py
    "mazmorrajefe2": Jefe2Scene,      # La clase Jefe2Scene está en levels/jefe_2.py
    "mazmorrap3": P3MazmorraScene,    # La clase P3MazmorraScene está en levels/p3_mazmorra.py
    "mazmorrajefe3": Jefe3Scene,      # La clase Jefe3Scene está en levels/jefe_3.py
}

# Variables globales que se pueden pasar entre escenas o cargar
progreso_llave = [False, False, False]

def run_game_loop(start_scene_name, character, key_progress, loaded_game_data=None):
    """
    Gestiona el bucle principal del juego y las transiciones entre escenas.
    """
    global progreso_llave, global_selected_character_g
    
    progreso_llave = key_progress
    selected_character_for_next_scene = character
    global_selected_character_g = character
    
    stop_menu_music()
    next_scene_name = start_scene_name

    while next_scene_name:
        current_scene_class = scene_map.get(next_scene_name)
        
        if not current_scene_class:
            print(f"ADVERTENCIA: Escena '{next_scene_name}' no encontrada en scene_map. Volviendo al menú principal.")
            break
        
        current_scene = current_scene_class(screen)
        current_scene.set_key_progress(progreso_llave)
        current_scene.name = next_scene_name
        
        if loaded_game_data and next_scene_name == start_scene_name:
            next_scene_name, returned_character = current_scene.run(
                selected_character_for_this_scene=selected_character_for_next_scene,
                loaded_game_data=loaded_game_data
            )
            loaded_game_data = None 
        else:
            next_scene_name, returned_character = current_scene.run(
                selected_character_for_this_scene=selected_character_for_next_scene
            )
        
        progreso_llave = current_scene.progreso_llave
        if returned_character:
            selected_character_for_next_scene = returned_character
            global_selected_character_g = returned_character

    play_menu_music()

def start_new_game():
    """Inicia una nueva partida desde el principio."""
    run_game_loop("aldea_scene", "Prota", [False, False, False])

def load_and_start_game():
    """Muestra la pantalla de carga y, si se selecciona una partida, la inicia."""
    load_screen = LoadGameScreen(screen)
    selected_file = load_screen.run()
    
    if selected_file:
        saved_data = load_game(selected_file)
        if saved_data:
            start_scene = saved_data.get("last_scene", "aldea_scene")
            character = saved_data.get("personaje", "Prota")
            keys = saved_data.get("progreso_llave", [False, False, False])
            
            run_game_loop(start_scene, character, keys, loaded_game_data=saved_data)

def stop_menu_music():
    """Detiene la música de fondo del menú."""
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()

def play_menu_music():
    """Reproduce la música de fondo del menú."""
    try:
        if not hasattr(play_menu_music, 'current_song') or play_menu_music.current_song != MENU_MUSIC_PATH:
            pygame.mixer.music.load(MENU_MUSIC_PATH)
            pygame.mixer.music.play(-1)
            play_menu_music.current_song = MENU_MUSIC_PATH
    except pygame.error as e:
        print(f"Error al reproducir música del menú: {e}")

def quit_game():
    """Termina el juego."""
    stop_menu_music()
    pygame.quit()
    sys.exit()

def main_menu():
    """Muestra y gestiona el me nú principal del juego."""
    try:
        fondo_menu = pygame.image.load(MENU_BACKGROUND_PATH).convert()
        fondo_menu = pygame.transform.scale(fondo_menu, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error:
        print(f"⚠️ No se pudo cargar el fondo del menú: {MENU_BACKGROUND_PATH}. Usando color sólido.")
        fondo_menu = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fondo_menu.fill(DARK_GREY)

    botones = {
        "Nueva Partida": {"accion": start_new_game},
        "Cargar Partida": {"accion": load_and_start_game},
        "Salir": {"accion": quit_game}
    }
    
    y_pos = SCREEN_HEIGHT // 2
    for nombre, data in botones.items():
        texto_surf = FONT_LARGE.render(nombre, True, WHITE)
        data["rect"] = texto_surf.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
        y_pos += 80

    while True:
        screen.blit(fondo_menu, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        for nombre, data in botones.items():
            color = WHITE
            if data["rect"].collidepoint(mouse_pos):
                color = MAGIC_BLUE
            
            if nombre == "Cargar Partida" and not get_saved_games():
                color = (100, 100, 100)
            
            texto_surf = FONT_LARGE.render(nombre, True, color)
            screen.blit(texto_surf, data["rect"])
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                quit_game()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if botones["Nueva Partida"]["rect"].collidepoint(evento.pos):
                    start_new_game()
                if botones["Cargar Partida"]["rect"].collidepoint(evento.pos):
                    if get_saved_games():
                        load_and_start_game()
                if botones["Salir"]["rect"].collidepoint(evento.pos):
                    quit_game()
        
        pygame.display.flip()

if __name__ == "__main__":
    play_menu_music()
    main_menu()