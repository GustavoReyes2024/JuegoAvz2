import pygame
import random
import math
from projectile import Proyectil
from constants import *

class FireProjectile(Proyectil):
    def __init__(self, x, y, direccion):
        super().__init__(x, y, direccion)
        self.image = pygame.transform.scale(pygame.image.load(SKILL_ICON_PATHS["fire"]).convert_alpha(), (35, 25))
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidad = 15; self.danio = 10; self.tipo_elemental = "fuego"
    def dibujar(self, s, ox, oy, z):
        if self.activo: s.blit(self.image, ((self.rect.x - ox) * z, (self.rect.y - oy) * z))

class IceProjectile(Proyectil):
    def __init__(self, x, y, direccion):
        super().__init__(x, y, direccion)
        self.image = pygame.transform.scale(pygame.image.load(SKILL_ICON_PATHS["ice"]).convert_alpha(), (35, 25))
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidad = 10; self.danio = 10; self.tipo_elemental = "hielo"
    def dibujar(self, s, ox, oy, z):
        if self.activo: s.blit(self.image, ((self.rect.x - ox) * z, (self.rect.y - oy) * z))

class MixedProjectile(Proyectil):
    def __init__(self, x, y, direccion):
        super().__init__(x, y, direccion)
        self.image = pygame.transform.scale(pygame.image.load(SKILL_ICON_PATHS["mixed"]).convert_alpha(), (50, 35))
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidad = 20; self.danio = 60; self.tipo_elemental = "mixto"
    def dibujar(self, s, ox, oy, z):
        if self.activo: s.blit(self.image, ((self.rect.x - ox) * z, (self.rect.y - oy) * z))

class RockProjectile(Proyectil):
    def __init__(self, x, y, direccion):
        super().__init__(x, y, direccion)
        self.image = pygame.transform.scale(pygame.image.load(SKILL_ICON_PATHS["rock"]).convert_alpha(), (30, 30))
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidad = 12; self.danio = 15; self.tipo_elemental = "tierra"
    def dibujar(self, s, ox, oy, z):
        if self.activo: s.blit(self.image, ((self.rect.x - ox) * z, (self.rect.y - oy) * z))

class SartenProjectile(Proyectil):
    def __init__(self, x, y, direccion):
        super().__init__(x, y, direccion)
        self.image = pygame.transform.scale(pygame.image.load(SKILL_ICON_PATHS["sarten"]).convert_alpha(), (50, 40))
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidad = 8; self.danio = 25; self.tipo_elemental = "fisico"
    def dibujar(self, s, ox, oy, z):
        if self.activo: s.blit(self.image, ((self.rect.x - ox) * z, (self.rect.y - oy) * z))

class RootProjectile(Proyectil):
    def __init__(self, x, y, direccion):
        super().__init__(x, y, direccion)
        self.image = pygame.transform.scale(pygame.image.load(SKILL_ICON_PATHS["root"]).convert_alpha(), (40, 20))
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidad = 9; self.danio = 12; self.tipo_elemental = "tierra"
    def dibujar(self, s, ox, oy, z):
        if self.activo: s.blit(self.image, ((self.rect.x - ox) * z, (self.rect.y - oy) * z))

class EarthSpikeAttack(Proyectil):
    def __init__(self, x, y):
        super().__init__(x, y, 0)
        self.image = pygame.transform.scale(pygame.image.load(SKILL_ICON_PATHS["earth_spike"]).convert_alpha(), (80, 110))
        self.rect = self.image.get_rect(midbottom=(x, y)); self.danio = 35; self.tipo_elemental = "tierra"
        self.creation_time = pygame.time.get_ticks(); self.lifetime = 600; self.hits_multiple = True
    def actualizar(self, offset_x=None):
        if pygame.time.get_ticks() - self.creation_time > self.lifetime: self.activo = False
    def dibujar(self, s, ox, oy, z):
        if self.activo: s.blit(self.image, ((self.rect.x - ox) * z, (self.rect.y - oy) * z))

class LightningBoltProjectile(Proyectil):
    def __init__(self, x, y, direccion):
        super().__init__(x, y, direccion)
        self.image = pygame.transform.scale(pygame.image.load(SKILL_ICON_PATHS["lightning_bolt"]).convert_alpha(), (50, 15))
        self.rect = self.image.get_rect(center=(x, y)); self.velocidad = 20; self.danio = 18; self.tipo_elemental = "rayo"
    def dibujar(self, s, ox, oy, z):
        if self.activo: s.blit(self.image, ((self.rect.x - ox) * z, (self.rect.y - oy) * z))

class DescendingLightningBolt(Proyectil):
    def __init__(self, x, y):
        super().__init__(x, y, 0)
        original_image = pygame.image.load(SKILL_ICON_PATHS["lightning_strike"]).convert_alpha()
        width = random.randint(15, 25); height = random.randint(50, 80)
        self.image = pygame.transform.scale(original_image, (width, height))
        self.velocidad = random.uniform(20, 28); self.rect = self.image.get_rect(center=(x, y)); self.danio = 15; self.tipo_elemental = "rayo"
    def actualizar(self, offset_x=None):
        self.rect.y += self.velocidad
        if self.rect.top > SCREEN_HEIGHT: self.activo = False
    def dibujar(self, s, ox, oy, z):
        if self.activo: s.blit(self.image, ((self.rect.x - ox) * z, (self.rect.y - oy) * z))

class BossDiagonalProjectile(Proyectil):
    def __init__(self, start_x, start_y, target_x, target_y):
        super().__init__(start_x, start_y, 0)
        self.image = pygame.transform.scale(pygame.image.load(SKILL_ICON_PATHS["boss_fireball"]).convert_alpha(), (40, 40))
        self.rect = self.image.get_rect(center=(start_x, start_y)); self.danio = 5
        distancia_x = target_x - start_x; distancia_y = target_y - start_y
        distancia = math.hypot(distancia_x, distancia_y); velocidad_total = 9
        if distancia > 0: self.vel_x = (distancia_x / distancia) * velocidad_total; self.vel_y = (distancia_y / distancia) * velocidad_total
        else: self.vel_x = 0; self.vel_y = velocidad_total
        self.rango = 1200; self.distancia_recorrida = 0
    def actualizar(self, offset_x=None):
        self.rect.x += self.vel_x; self.rect.y += self.vel_y
        self.distancia_recorrida = math.hypot(self.rect.centerx - self.initial_x, self.rect.centery - self.initial_y)
        if self.distancia_recorrida > self.rango: self.activo = False
    def dibujar(self, s, ox, oy, z):
        if self.activo: s.blit(self.image, ((self.rect.x - ox) * z, (self.rect.y - oy) * z))

class BossGroundProjectile(Proyectil):
    def __init__(self, x, y, direccion):
        super().__init__(x, y, direccion)
        self.image = pygame.transform.scale(pygame.image.load(SKILL_ICON_PATHS["boss_groundwave"]).convert_alpha(), (60, 30))
        self.rect = self.image.get_rect(midbottom=(x, y)); self.velocidad = 6; self.danio = 5
    def dibujar(self, s, ox, oy, z):
        if self.activo: s.blit(self.image, ((self.rect.x - ox) * z, (self.rect.y - oy) * z))