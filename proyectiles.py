import pygame
from biblioteca import *

class Proyectil:
    def __init__(self, x, y, direccion):
        self.initial_x = x
        self.initial_y = y
        
        self.rect = pygame.Rect(x, y, 10, 10)
        self.direccion = direccion
        self.velocidad = 10
        self.danio = 5
        self.activo = True
        self.rango = 5000
        
        # --- LÓGICA DE MOVIMIENTO CORREGIDA ---
        # Ahora todos los proyectiles tienen velocidad en X y Y.
        self.vel_x = self.velocidad * self.direccion
        self.vel_y = 0 # Por defecto, no se mueve verticalmente.

    def actualizar(self, camera_offset_x=0):
        # Mueve el proyectil usando sus velocidades X e Y.
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        
        # Comprueba si el proyectil ha viajado más allá de su rango.
        distancia_recorrida = pygame.math.Vector2(self.rect.centerx, self.rect.centery).distance_to(
            (self.initial_x, self.initial_y)
        )
        if distancia_recorrida > self.rango:
            self.activo = False

        # Comprueba si el proyectil está fuera de la pantalla.
        screen_visible_left = camera_offset_x - 300
        screen_visible_right = camera_offset_x + SCREEN_WIDTH + 300
        if self.rect.right < screen_visible_left or self.rect.left > screen_visible_right:
            self.activo = False
        if self.rect.bottom < 0 or self.rect.top > pygame.display.get_surface().get_height():
            self.activo = False

    def dibujar(self, superficie, offset_x, offset_y, zoom):
        if self.activo:
            pos_x = int((self.rect.x - offset_x) * zoom)
            pos_y = int((self.rect.y - offset_y) * zoom)
            pygame.draw.circle(superficie, WHITE, (pos_x, pos_y), int(5 * zoom))