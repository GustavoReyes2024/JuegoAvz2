# proyectiles.py (completo, la versión más reciente que te di)

import pygame
from biblioteca import * # Importa SCREEN_WIDTH, WHITE

class Proyectil:
    def __init__(self, x, y, direccion):
        self.initial_x = x
        self.initial_y = y
        
        self.rect = pygame.Rect(x, y, 10, 10)
        self.direccion = direccion
        self.velocidad = 10
        self.danio = 5
        self.activo = True
        self.rango = 2500 # <--- AUMENTADO RANGO: ¡CRÍTICO! Puede que desaparezcan muy pronto.
        self.distancia_recorrida = 0

    def actualizar(self, camera_offset_x=0):
        self.rect.x += self.velocidad * self.direccion
        
        self.distancia_recorrida = pygame.math.Vector2(self.rect.centerx, self.rect.centery).distance_to(
            (self.initial_x, self.initial_y)
        )
        
        if self.distancia_recorrida > self.rango:
            self.activo = False

        # Lógica de desactivación si el proyectil sale de la vista de la cámara
        # Aumenta el margen si los proyectiles desaparecen demasiado pronto
        screen_visible_left = camera_offset_x - 300 # <--- AUMENTADO MARGEN
        screen_visible_right = camera_offset_x + SCREEN_WIDTH + 300 # <--- AUMENTADO MARGEN

        if self.rect.right < screen_visible_left or self.rect.left > screen_visible_right:
            self.activo = False
        
        if self.rect.bottom < 0 or self.rect.top > pygame.display.get_surface().get_height():
            self.activo = False

    def dibujar(self, superficie, offset_x, offset_y, zoom):
        # Esta función es para DEBUG si no hay sprite. En abilities.py se sobrescribe.
        if self.activo:
            pos_x = int((self.rect.x - offset_x) * zoom)
            pos_y = int((self.rect.y - offset_y) * zoom)
            pygame.draw.circle(superficie, WHITE, (pos_x, pos_y), int(5 * zoom))