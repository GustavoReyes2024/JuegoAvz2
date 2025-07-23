import pygame
import sys
from game_scene import GameScene
from constants import *
from enemy import Boss2 # <-- Importamos la clase del jefe desde enemy.py
from ui import BossHealthBar

class MazmorraBoss2Scene(GameScene):
    # El __init__ de una escena solo debe recibir 'screen'
    def __init__(self, screen):
        self.map_width = 1920
        self.map_height = 1080
        ground_y = 900
        platforms = [pygame.Rect(0, ground_y, self.map_width, 50)]
        player_start = (200, ground_y - PLAYER_HEIGHT)
        
        # Primero se inicializa la escena base con el mapa vacío
        super().__init__(
            screen, MAP_MAZMORRA_BOSS2_PATH, platforms,
            [], [], player_start, [], 
            self.map_width, self.map_height, 
            next_scene_name=None # Termina el juego o vuelve al menú
        )
        self.name = "mazmorra_boss2"
        self.music_path = BOSS_MUSIC_PATH

        # --- AHORA, DENTRO DE LA ESCENA, CREAMOS AL JEFE ---
        boss_start_x = self.map_width - 400
        boss_start_y = ground_y
        self.boss = Boss2(boss_start_x, boss_start_y, "nightborne")
        self.enemigos.append(self.boss)
        
        # Y creamos su barra de vida
        self.boss_health_bar = BossHealthBar(screen, self.boss, "NightBorne")

    def update(self):
        super().update()
        # Actualizar la barra de vida del jefe en cada frame
        if self.boss in self.enemigos:
            self.boss_health_bar.update(self.boss)
        elif not self.enemigos and self.boss.salud <= 0: # Se activa solo si el jefe fue derrotado
            print("¡Jefe derrotado!")
            self.running = False # Vuelve al menú principal

# En enemy.py, dentro de la clase Boss2

    def dibujar(self, superficie, offset_x, offset_y, zoom):
        # Llama al método de la clase base para dibujar el sprite del jefe y su hitbox
        super().dibujar(superficie, offset_x, offset_y, zoom)
        
        # --- BUCLE AÑADIDO PARA DIBUJAR LOS PROYECTILES DEL JEFE ---
        for proyectil in self.proyectiles:
            proyectil.dibujar(superficie, offset_x, offset_y, zoom)