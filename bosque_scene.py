import pygame
from game_scene import GameScene
from constants import *
from interactables import *

class BosqueScene(GameScene):
    def __init__(self, screen):
        self.map_width = 2500
        self.map_height = 830
        
        ground_y = 780
        bosque_platforms = [
            pygame.Rect(0, ground_y, self.map_width, 50),
        ]
        
        bosque_checkpoints = []
        bosque_interactables = []

        player_start = (100, ground_y - PLAYER_HEIGHT+10)
        
        # --- LISTA SIMPLIFICADA ---
        bosque_enemies = [
            (400, ground_y-50, 200, "lobo"),
            (1000, ground_y-50, 600, "lobo"),
            (600, ground_y, 600, "esqueleto"),
        ]

        super().__init__(
            screen, MAP_BOSQUE_PATH, bosque_platforms, 
            bosque_checkpoints,
            bosque_interactables,
            player_start, 
            bosque_enemies, 
            self.map_width, 
            self.map_height, 
            next_scene_name="aldea"
        )
        
        self.name = "bosque"