import pygame
import sys
import os
from constants import *
from game_state import save_game, load_game, get_saved_games
from bosque_scene import BosqueScene
from aldea_scene import AldeaScene
from mazmorra_scene import MazmorraScene
from levels_mazmorra.mazmorrap1 import MazmorraP1Scene
from levels_mazmorra.mazmorrap2 import MazmorraP2Scene
from levels_mazmorra.mazmorrap3 import MazmorraP3Scene
from levels_mazmorra.mazmorrap4 import MazmorraP4Scene
# --- CORRECCIÓN: SE ASEGURA DE QUE TODOS LOS NIVELES ESTÉN IMPORTADOS ---
from levels_mazmorra.mazmorrap5 import MazmorraP5Scene
from levels_mazmorra.mazmorra_jefe import MazmorraJefeScene
from levels_mazmorra.mazmorrap6 import MazmorraP6Scene
from levels_mazmorra.mazmorra_boss2 import MazmorraBoss2Scene
from ui import LoadGameScreen

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Elemental Trinity")

# --- CORRECCIÓN: MAPA DE ESCENAS COMPLETO Y ACTUALIZADO ---
scene_map = {
    "bosque": BosqueScene,
    "aldea": AldeaScene,
    "mazmorra": MazmorraScene,
    "mazmorra_p1": MazmorraP1Scene,
    "mazmorra_p2": MazmorraP2Scene,
    "mazmorra_p3": MazmorraP3Scene,
    "mazmorra_p4": MazmorraP4Scene,
    "mazmorrap5": MazmorraP5Scene, # <-- Ahora sí está registrada
    "mazmorra_p6": MazmorraP6Scene,
    "mazmorra_jefe": MazmorraJefeScene,
    "mazmorra_boss2": MazmorraBoss2Scene,
}

progreso_llave = [False, False, False]
global_selected_character_g = "Prota"

def run_game_loop(start_scene_name, character, key_progress):
    global progreso_llave, global_selected_character_g
    
    progreso_llave = key_progress
    selected_character_for_next_scene = character
    global_selected_character_g = character
    
    stop_menu_music()
    next_scene_name = start_scene_name

    while next_scene_name:

        
        current_scene_class = scene_map.get(next_scene_name)
        
        if not current_scene_class:
            print(f"ADVERTENCIA: Escena '{next_scene_name}' no encontrada en scene_map. Volviendo al menú.")
            break
        
        current_scene = current_scene_class(screen)
        current_scene.set_key_progress(progreso_llave)
        current_scene.name = next_scene_name
        
        next_scene_name, returned_character = current_scene.run(
            selected_character_for_this_scene=selected_character_for_next_scene
        )
        
        progreso_llave = current_scene.progreso_llave
        if returned_character:
            selected_character_for_next_scene = returned_character
            global_selected_character_g = returned_character

    play_menu_music()

def start_new_game():
    run_game_loop("bosque", "Prota", [False, False, False])

def load_and_start_game():
    load_screen = LoadGameScreen(screen)
    selected_file = load_screen.run()
    
    if selected_file:
        saved_data = load_game(selected_file)
        if saved_data:
            start_scene = saved_data.get("last_scene", "bosque")
            character = saved_data.get("personaje", "Prota")
            keys = saved_data.get("progreso_llave", [False, False, False])
            run_game_loop(start_scene, character, keys)

def stop_menu_music():
    if pygame.mixer.music.get_busy(): pygame.mixer.music.stop()

def play_menu_music():
    try:
        if getattr(play_menu_music, 'current_song', None) != MENU_MUSIC_PATH:
            pygame.mixer.music.load(MENU_MUSIC_PATH)
            pygame.mixer.music.play(-1)
            play_menu_music.current_song = MENU_MUSIC_PATH
    except pygame.error as e: print(f"Error al reproducir música del menú: {e}")

def quit_game():
    stop_menu_music(); pygame.quit(); sys.exit()

def main_menu():
    fondo_menu = pygame.image.load(MENU_BACKGROUND_PATH).convert()
    fondo_menu = pygame.transform.scale(fondo_menu, (SCREEN_WIDTH, SCREEN_HEIGHT))
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
            color = MAGIC_BLUE if data["rect"].collidepoint(mouse_pos) else WHITE
            if nombre == "Cargar Partida" and not get_saved_games():
                color = (100, 100, 100)
            texto_surf = FONT_LARGE.render(nombre, True, color)
            screen.blit(texto_surf, data["rect"])
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                quit_game()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if botones["Nueva Partida"]["rect"].collidepoint(evento.pos): start_new_game()
                if botones["Cargar Partida"]["rect"].collidepoint(evento.pos):
                    if get_saved_games(): load_and_start_game()
                if botones["Salir"]["rect"].collidepoint(evento.pos): quit_game()
        pygame.display.flip()

if __name__ == "__main__":
    play_menu_music()
    main_menu()