import pygame
from game_scene import GameScene
from constants import *
from interactables import *

class MazmorraP3Scene(GameScene):
    def __init__(self, screen):
        self.map_width = 3000
        self.map_height = 830
        
        ground_y = 780
        dungeon_platforms = [ pygame.Rect(0, ground_y, self.map_width, 50) ]
        dungeon_checkpoints = []
        dungeon_interactables = []
        
        player_start = (100, ground_y - PLAYER_HEIGHT)
        
        # --- LISTA SIMPLIFICADA ---
        dungeon_enemies = [
            (400, ground_y, 200, "esqueleto"),
            (800, ground_y, 300, "golem"),
            (1200, ground_y, 250, "lobo"),
            (1600, ground_y, 200, "esqueleto"),
            (2000, ground_y, 300, "golem"),
            (2400, ground_y, 150, "lobo"),
        ]
        
        super().__init__(
            screen, MAP_MAZMORRA_P3_PATH, dungeon_platforms, dungeon_checkpoints,
            dungeon_interactables, player_start, dungeon_enemies,
            self.map_width, self.map_height, next_scene_name="mazmorra_jefe"
        )
        
        self.music_path = "Soundtracks/soundtrack2.mp3"
        self.name = "mazmorra_p3"