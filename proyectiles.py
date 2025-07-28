import pygame
from biblioteca import * # Importa SCREEN_WIDTH, WHITE

class Proyectil:
    def __init__(self, x, y, direccion):
        self.initial_x = x
        self.initial_y = y
        
        self.rect = pygame.Rect(x, y, 10, 10)
        self.direccion = direccion # Dirección del sprite (1 para derecha, -1 para izquierda)
        self.velocidad = 10 # Velocidad base del proyectil
        self.danio = 5 # Daño base
        self.activo = True # Si el proyectil está activo en el juego
        
        # Atributos para el cálculo de rango y movimiento.
        # ¡ASEGURADO QUE SE INICIALIZAN AQUÍ!
        self.rango = 2500 # Rango por defecto para que se desactive por distancia (valor generoso)
        self.distancia_recorrida = 0.0 # Inicializado como float
        
        self.vel_x = self.velocidad * self.direccion # Velocidad horizontal inicial
        self.vel_y = 0.0 # Velocidad vertical inicial (por defecto no se mueve verticalmente)

    def actualizar(self, camera_offset_x=0):
        # Mueve el proyectil usando sus velocidades X e Y.
        # Esta es la lógica de movimiento BASE. Las subclases pueden añadir más.
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        
        # Calcula la distancia recorrida desde el punto de origen
        self.distancia_recorrida = pygame.math.Vector2(self.rect.centerx, self.rect.centery).distance_to(
            (self.initial_x, self.initial_y)
        )
        
        # Desactivar el proyectil si ha excedido su rango definido
        if self.distancia_recorrida > self.rango:
            self.activo = False
            # print(f"DEBUG: Proyectil {type(self).__name__} desactivado por rango ({self.distancia_recorrida}/{self.rango})") # Debug
            return # Salir si ya está inactivo

        # Lógica de desactivación si el proyectil sale de la VISTA DE LA CÁMARA (con margen extra)
        margin_x = 500 # Margen horizontal fuera de la pantalla
        margin_y = 500 # Margen vertical fuera de la pantalla

        screen_visible_left = camera_offset_x - margin_x
        screen_visible_right = camera_offset_x + SCREEN_WIDTH + margin_x
        screen_visible_top = -margin_y 
        screen_visible_bottom = pygame.display.get_surface().get_height() + margin_y

        if (self.rect.right < screen_visible_left or 
            self.rect.left > screen_visible_right or
            self.rect.bottom < screen_visible_top or 
            self.rect.top > screen_visible_bottom):
            self.activo = False
            # print(f"DEBUG: Proyectil {type(self).__name__} desactivado por fuera de vista. Pos: ({self.rect.x},{self.rect.y})") # Debug

    def dibujar(self, superficie, offset_x, offset_y, zoom):
        # Este es un método de dibujo de RESPALDO (si las subclases no tienen sprite o falla).
        # Dibuja un círculo blanco si una habilidad específica no tiene su propia imagen.
        if self.activo:
            pos_x = int((self.rect.x - offset_x) * zoom)
            pos_y = int((self.rect.y - offset_y) * zoom)
            pygame.draw.circle(superficie, WHITE, (pos_x, pos_y), int(5 * zoom))