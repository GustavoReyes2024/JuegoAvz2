import pygame
from constants import *

class Proyectil:
    def __init__(self, x, y, direccion):
        # Coordenadas iniciales para el cálculo de rango
        self.initial_x = x
        self.initial_y = y
        
        # Atributos base que las habilidades hijas pueden sobreescribir
        self.rect = pygame.Rect(x, y, 10, 10)
        self.direccion = direccion
        self.velocidad = 10
        self.danio = 5
        self.activo = True

    def actualizar(self, offset_x):
        # Mueve el proyectil
        self.rect.x += self.velocidad * self.direccion
        
        # Lógica para desactivar el proyectil si se aleja demasiado de la cámara
        limite_izquierdo = offset_x - 200
        limite_derecho = offset_x + SCREEN_WIDTH + 200
        if self.rect.right < limite_izquierdo or self.rect.left > limite_derecho:
            self.activo = False

    def dibujar(self, superficie, offset_x, offset_y, zoom):
        # Este es un método de dibujo de RESPALDO.
        # Dibuja un círculo blanco si una habilidad específica no tiene su propia imagen.
        if self.activo:
            pos_x = int((self.rect.x - offset_x) * zoom)
            pos_y = int((self.rect.y - offset_y) * zoom)
            pygame.draw.circle(superficie, WHITE, (pos_x, pos_y), 5 * zoom)