import pygame
import random
from constants import *

class Particle:
    # CORRECCIÓN: Se añaden los guiones bajos a __init__
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vel_x = random.uniform(-2, 2)
        self.vel_y = random.uniform(-4, -1)
        self.lifetime = random.randint(15, 30)
        self.color = color
        self.size = random.randint(2, 5)

    def update(self):
        self.vel_y += 0.2
        self.x += self.vel_x
        self.y += self.vel_y
        self.lifetime -= 1

    def draw(self, surface, offset_x, offset_y, zoom):
        pos_x = (self.x - offset_x) * zoom
        pos_y = (self.y - offset_y) * zoom
        pygame.draw.rect(surface, self.color, (pos_x, pos_y, self.size * zoom, self.size * zoom))

class HitSplat:
    # CORRECCIÓN: Se añaden los guiones bajos a __init__
    def __init__(self, x, y, color=(200, 20, 20)):
        self.particles = [Particle(x, y, color) for _ in range(15)]

    def update(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)

    @property
    def is_active(self):
        return len(self.particles) > 0

    def draw(self, surface, offset_x, offset_y, zoom):
        for particle in self.particles:
            particle.draw(surface, offset_x, offset_y, zoom)