import pygame
from game_scene import GameScene
from constants import *
from aldea_scene import global_selected_character_g
from interactables import * 
class MazmorraP5Scene(GameScene):
    def __init__(self, screen):
        self.map_width = 3000
        self.map_height = 830
        
        ground_y = 780
        platforms = [
            # Suelo principal
            pygame.Rect(0, ground_y, self.map_width, 50),
            # Serie de plataformas ascendentes
            pygame.Rect(500, ground_y - 100, 150, 20),
            pygame.Rect(800, ground_y - 200, 150, 20),
            pygame.Rect(1100, ground_y - 300, 150, 20),
            # Plataforma larga en el medio
            pygame.Rect(1500, ground_y - 250, 400, 20),
        ]
        
        checkpoints = [
             pygame.Rect(1600, ground_y - 350, 100, 100)
        ]
        
        # Este nivel no tendrá puzles, así que pasamos una lista vacía
        interactables = []

        player_start = (100, ground_y - PLAYER_HEIGHT)

        enemies_data = [
            (850, ground_y - 200 - ENEMY_HEIGHT, 0, "jades"),
            (1600, ground_y - 250 - ENEMY_HEIGHT, 300, "wizzardblue"),
            (2200, ground_y - ENEMY_HEIGHT, 400, "depredator"),
            (2600, ground_y - ENEMY_HEIGHT, 200, "fire"),
        ]
        
        super().__init__(
            screen, MAP_MAZMORRA_P5_PATH, platforms,
            checkpoints, interactables, player_start, 
            enemies_data, self.map_width, self.map_height, 
            next_scene_name="mazmorrap6"
        )
        
        self.music_path = "Soundtracks/soundtrack2.mp3"
        self.name = "mazmorra_p5"