import pygame
from game_scene import GameScene
from constants import *
from aldea_scene import global_selected_character_g
from interactables import *

class MazmorraP4Scene(GameScene):
    def __init__(self, screen):
        self.map_width = 2500
        self.map_height = 830

        ground_y = 750
        platforms = [
            pygame.Rect(0, ground_y, self.map_width, 50),
            pygame.Rect(600, ground_y - 150, 200, 30),
            pygame.Rect(1100, ground_y - 250, 200, 30),
            pygame.Rect(1600, ground_y - 150, 200, 30),
        ]
        
        checkpoints = [
             pygame.Rect(1200, ground_y - 350, 100, 100)
        ]

        # Por ahora, no añadiremos puzles a este nivel
        interactables = []

        player_start = (100, ground_y - PLAYER_HEIGHT)

        enemies_data = [
            (500, ground_y - ENEMY_HEIGHT, 300, "depredator"),
            (1150, ground_y - 250 - ENEMY_HEIGHT, 100, "wizzardblue"),
            (1700, ground_y - ENEMY_HEIGHT, 200, "fire"),
            (1950, ground_y - ENEMY_HEIGHT, 200, "wind"),
            (2300, ground_y - ENEMY_HEIGHT, 0, "jades"),
        ]
        
        # --- LLAMADA AL CONSTRUCTOR CORREGIDA ---
        # Añadimos la lista de puzles vacía en la posición correcta
        super().__init__(
            screen, MAP_MAZMORRA_P4_PATH, platforms,
            checkpoints, 
            interactables, # <-- Argumento añadido
            player_start, 
            enemies_data,
            self.map_width, self.map_height, 
            next_scene_name="mazmorrap5"
        )
        
        self.name = "mazmorra_p4"
        self.jugador.cambiar_personaje(global_selected_character_g)