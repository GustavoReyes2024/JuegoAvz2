# En levels_mazmorra/mazmorrap6.py
import pygame
from game_scene import GameScene
from constants import *
from interactables import *

class MazmorraP6Scene(GameScene):
    def __init__(self, screen):
        self.map_width = 2500
        self.map_height = 830
        ground_y = 780
        platforms = [pygame.Rect(0, ground_y, self.map_width, 50)]
        player_start = (100, ground_y - PLAYER_HEIGHT)
        enemies = [
            (800, ground_y, 300, "golem_2"), # <-- Usando el nuevo enemigo
            (1600, ground_y, 200, "golem_2"),
        ]

        super().__init__(
            screen, MAP_MAZMORRA_P6_PATH, platforms, # <-- CAMBIO AQUÍ
            [], [], player_start, enemies, 
            self.map_width, self.map_height, 
            next_scene_name="mazmorra_boss2"
        )
        self.name = "mazmorra_p6"