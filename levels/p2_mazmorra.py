import pygame
from escenas import GameScene
# from biblioteca import * # ELIMINADO: Asumimos que todas las constantes están en constants.py
# from interactables import * # ELIMINADO: Si no hay interactables específicos aquí que lo justifiquen

# Importar constantes necesarias
from biblioteca import (
    PLAYER_HEIGHT, MAP_MAZMORRA_P2_PATH # Asegúrate de que estas constantes estén en constants.py
)
# No necesitas importar las clases de enemigos aquí, GameScene ya se encarga de eso.

class P2MazmorraScene(GameScene): # Nombre de la clase corregido para coincidir con main.py
    def __init__(self, screen):
        self.map_width = 3000
        self.map_height = 830
        
        ground_y = 780 # Altura del suelo principal
        
        # Plataformas: Puedes añadir más plataformas aquí si tu diseño de nivel lo requiere.
        dungeon_platforms = [
            pygame.Rect(0, ground_y, self.map_width, 50) # Suelo principal
            # Ejemplo de plataformas flotantes para añadir complejidad:
            # pygame.Rect(400, ground_y - 120, 180, 30),
            # pygame.Rect(900, ground_y - 200, 250, 30),
            # pygame.Rect(1600, ground_y - 150, 200, 30)
        ]
        
        # Checkpoints: Añade checkpoints si los necesitas en esta sección de la mazmorra.
        dungeon_checkpoints = [
             pygame.Rect(800, ground_y - 100, 100, 100),
             pygame.Rect(2200, ground_y - 100, 100, 100)
        ]
        
        dungeon_interactables = [] # Lista de objetos interactuables (vacía por defecto)
        
        player_start = (100, ground_y - PLAYER_HEIGHT) # Posición de inicio del jugador
        
        # --- LISTA DE ENEMIGOS PARA MAZMORRA P2 ---
        # ¡CORREGIDO: Eliminado el 3er parámetro (patrol_width)!
        dungeon_enemies = [
            (500, ground_y - 100, "gole"),
            (1000, ground_y - 60, "goblins"),
            (1500, ground_y - 100, "esqueleto"),
            (2000, ground_y - 100, "gole"),
            (2500, ground_y - 60, "goblins"),
            (2800, ground_y - 100, "esqueleto"),
        ]
        
        super().__init__(
            screen, MAP_MAZMORRA_P2_PATH, dungeon_platforms, dungeon_checkpoints,
            dungeon_interactables, player_start, dungeon_enemies,
            self.map_width, self.map_height, next_scene_name="mazmorrajefe2" # ¡CORREGIDO A MAZMORRAJEFE2!
        )
        
        self.music_path = "Soundtracks/soundtrack2.mp3" # Música específica para esta sección
        self.name = "mazmorrap2" # Nombre de la escena para la lógica del juego

        # Puedes añadir diálogos específicos o triggers aquí si lo deseas para esta escena