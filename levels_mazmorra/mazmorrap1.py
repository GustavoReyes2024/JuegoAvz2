import pygame
from game_scene import GameScene
from constants import *
from interactables import *

class MazmorraP1Scene(GameScene):
    def __init__(self, screen):
        self.map_width = 3000
        self.map_height = 830
        
        ground_y = 780
        dungeon_platforms = [ pygame.Rect(0, ground_y, self.map_width, 50) ]
        dungeon_checkpoints = [ pygame.Rect(1500, 700, 100, 100) ]
        dungeon_interactables = []
        
        player_start = (100, ground_y - PLAYER_HEIGHT)
        
        # --- LISTA SIMPLIFICADA ---
        dungeon_enemies = [
            (600, ground_y, 200, "esqueleto"),
            (1200, ground_y, 250, "golem"),
            (1800, ground_y, 200, "esqueleto"),
            (2400, ground_y, 150, "lobo"),
        ]
        
        super().__init__(
            screen, MAP_MAZMORRA_P1_PATH, dungeon_platforms, dungeon_checkpoints,
            dungeon_interactables, player_start, dungeon_enemies,
            self.map_width, self.map_height, next_scene_name="mazmorra_p2"
        )
        
        self.music_path = "Soundtracks/soundtrack2.mp3"
        self.name = "mazmorra_p1"