import pygame
import sys
import os

# Importar constantes generales desde biblioteca.py
from biblioteca import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FONT_LARGE, MAGIC_BLUE, WHITE, DARK_GREY,
    MENU_BACKGROUND_PATH, MENU_MUSIC_PATH
)

from guardar import save_game, load_game, get_saved_games
from interfaz import LoadGameScreen

# Importar las clases de cada escena.
from aldea import AldeaScene, global_selected_character_g
from escenario_mazmorra import MazmorraScene
from levels.p1_mazmorra import P1MazmorraScene
from levels.jefe_1 import Jefe1Scene
from levels.p2_mazmorra import P2MazmorraScene
from levels.jefe_2 import Jefe2Scene
from levels.p3_mazmorra import P3MazmorraScene
from levels.jefe_3 import Jefe3Scene
from creditos import CreditosScene


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Elemental Trinity")

# --- MAPA DE ESCENAS COMPLETO Y ACTUALIZADO ---
scene_map = {
    "aldea_scene": AldeaScene,
    "mazmorra_scene": MazmorraScene,
    "mazmorrap1": P1MazmorraScene,
    "mazmorrajefe1": Jefe1Scene,
    "mazmorrap2": P2MazmorraScene,
    "mazmorrajefe2": Jefe2Scene,
    "mazmorrap3": P3MazmorraScene,
    "mazmorrajefe3": Jefe3Scene,
    "creditos_scene": CreditosScene,
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
        
        # --- CORRECCIÓN 1: Comprobar si los métodos existen antes de llamarlos ---
        if hasattr(current_scene, 'set_key_progress'):
            current_scene.set_key_progress(progreso_llave)
        
        if hasattr(current_scene, 'name'):
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
        
        # --- CORRECCIÓN 2: Comprobar si el atributo existe antes de acceder a él ---
        if hasattr(current_scene, 'progreso_llave'):
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
    """Muestra y gestiona el menú principal del juego."""
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