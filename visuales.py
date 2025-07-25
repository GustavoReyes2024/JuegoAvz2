import pygame
import random
# Importar constantes necesarias, como colores si se definen allí, aunque en este caso
# los colores se pasan como argumentos o están hardcodeados, lo cual es aceptable.
# from constants import SOME_COLOR_CONSTANT # Ejemplo: Si tuvieras RED = (255,0,0) en constants

# biblioteca ELIMINADA si su contenido se ha movido a constants

class Particle:
    # Constructor de la partícula
    def __init__(self, x, y, color):
        self.x = x # Posición X
        self.y = y # Posición Y
        self.vel_x = random.uniform(-2, 2) # Velocidad horizontal aleatoria
        self.vel_y = random.uniform(-4, -1) # Velocidad vertical aleatoria (hacia arriba)
        self.lifetime = random.randint(15, 30) # Duración de vida de la partícula
        self.color = color # Color de la partícula
        self.size = random.randint(2, 5) # Tamaño de la partícula

    def update(self):
        """
        Actualiza la posición y el tiempo de vida de la partícula.
        Aplica una pequeña gravedad para que las partículas caigan.
        """
        self.vel_y += 0.2 # Aplicar gravedad (hacia abajo)
        self.x += self.vel_x
        self.y += self.vel_y
        self.lifetime -= 1 # Reducir el tiempo de vida

    def draw(self, surface, offset_x, offset_y, zoom):
        """
        Dibuja la partícula en la superficie, aplicando el offset de la cámara y el zoom.
        """
        # Calcular la posición en pantalla con el offset y el zoom
        pos_x = (self.x - offset_x) * zoom
        pos_y = (self.y - offset_y) * zoom
        # Dibujar la partícula como un pequeño rectángulo
        pygame.draw.rect(surface, self.color, (pos_x, pos_y, self.size * zoom, self.size * zoom))

class HitSplat:
    # Constructor del efecto de impacto (HitSplat)
    def __init__(self, x, y, color=(200, 20, 20)): # Color por defecto para el splat (rojo oscuro)
        # Crea una lista de partículas que componen el splat
        self.particles = [Particle(x, y, color) for _ in range(15)] # 15 partículas por splat

    def update(self):
        """
        Actualiza todas las partículas dentro del HitSplat y las elimina si su tiempo de vida termina.
        """
        for particle in self.particles[:]: # Iterar sobre una copia para poder modificar la lista
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)

    @property
    def is_active(self):
        """
        Propiedad que indica si el HitSplat aún tiene partículas activas.
        """
        return len(self.particles) > 0

    def draw(self, surface, offset_x, offset_y, zoom):
        """
        Dibuja todas las partículas del HitSplat en la superficie.
        """
        for particle in self.particles:
            particle.draw(surface, offset_x, offset_y, zoom)