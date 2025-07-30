import pygame
from escenas import GameScene
# from biblioteca import * # ELIMINADO: Asumimos que todas las constantes están en constants.py
# from interactables import * # ELIMINADO: Si no hay interactables específicos aquí que lo justifiquen

# Importar constantes necesarias
from biblioteca import (
    PLAYER_HEIGHT, MAP_MAZMORRA_P1_PATH # Asegúrate de que estas constantes estén en constants.py
)
# No necesitas importar las clases de enemigos aquí, GameScene ya se encarga de eso.

class P1MazmorraScene(GameScene): # Nombre de la clase corregido para coincidir con main.py
    def __init__(self, screen):
        self.map_width = 3000
        self.map_height = 830
        
        ground_y = 780 # Altura del suelo principal
        
        # Plataformas: Puedes añadir más plataformas aquí si tu diseño de nivel lo requiere.
        dungeon_platforms = [
            pygame.Rect(0, ground_y, self.map_width, 50) # Suelo principal
            # Ejemplo de plataforma flotante:
            # pygame.Rect(500, ground_y - 150, 200, 30),
            # pygame.Rect(1000, ground_y - 250, 150, 30)
        ]
        
        # Checkpoints: Se mantiene el checkpoint si lo necesitas.
        dungeon_checkpoints = [
            pygame.Rect(1500, ground_y - 100, 100, 100) # Checkpoint en la mitad del mapa
        ]
        
        dungeon_interactables = [] # Lista de objetos interactuables (vacía por defecto)
        
        player_start = (100, ground_y - PLAYER_HEIGHT) # Posición de inicio del jugador
        
        # --- LISTA DE ENEMIGOS PARA MAZMORRA P1 ---
        # ¡CORREGIDO: Eliminado el 3er parámetro (patrol_width)!
        dungeon_enemies = [
            (600, ground_y - 5, "esqueleto"),
            (1200, ground_y - 10, "goblins"),
            (1800, ground_y, "gole"),
            (2400, ground_y - 10, "goblins"),
        ]
        
        super().__init__(
            screen, MAP_MAZMORRA_P1_PATH, dungeon_platforms, dungeon_checkpoints,
            dungeon_interactables, player_start, dungeon_enemies,
            self.map_width, self.map_height, next_scene_name="mazmorrajefe1" # ¡CORREGIDO A MAZMORRAJEFE1!
        )
        
        self.music_path = "Soundtracks/soundtrack2.mp3" # Música específica para esta sección
        self.name = "mazmorrap1" # Nombre de la escena para la lógica del juego

        # Lógica de transición específica para esta escena, si es necesaria.
        # Por defecto, la transición ocurre cuando el jugador llega al borde derecho del mapa
        # Y cuando todos los enemigos son derrotados (definido en GameScene.update)