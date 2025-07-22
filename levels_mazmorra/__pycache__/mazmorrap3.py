# levels_mazmorra/mazmorrap3.py
import pygame
from game_scene import GameScene
from constants import *
from aldea_scene import global_selected_character_g

class MazmorraP3Scene(GameScene):
    def __init__(self, screen):
        self.map_width = 3000
        self.map_height = 830

        dungeon_platforms = [
            pygame.Rect(0, 780, self.map_width, 50),
        ]

        player_start = (100, 780 - PLAYER_HEIGHT)

        dungeon_enemies = [
            (600, 780 - ENEMY_HEIGHT, 200, "Enemies/esqueleton.png"),
            (950, 780 - ENEMY_HEIGHT, 250, "Enemies/goblins.png"),
            (1400, 780 - ENEMY_HEIGHT, 200, "Enemies/esqueleton.png"),
            (1800, 780 - ENEMY_HEIGHT, 300, "Enemies/goblins.png"),
            (2200, 780 - ENEMY_HEIGHT, 200, "Enemies/esqueleton.png"),
        ]

        super().__init__(
            screen,
            MAP_MAZMORRA_P3_PATH,
            dungeon_platforms,
            player_start,
            dungeon_enemies,
            self.map_width,
            self.map_height,
            next_scene_name="mazmorra_jefe" # <-- Apunta a la escena del jefe
        )
        
        self.music_path = "Soundtracks/soundtrack2.mp3"
        self.name = "mazmorra_p3"
        self.jugador.cambiar_personaje(global_selected_character_g)