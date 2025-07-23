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

# En abilities.py (añadir al final)

class WizzardBlueProjectile(Proyectil):
    def __init__(self, start_x, start_y, target_x, target_y):
        super().__init__(start_x, start_y, 0)
        # NOTA: Debes crear una imagen para el proyectil o usar una que ya tengas.
        # Por ahora, usaremos una imagen de placeholder que tienes.
        try:
            self.image = pygame.transform.scale(pygame.image.load(SKILL_ICON_PATHS["ice"]).convert_alpha(), (25, 25))
        except pygame.error: # Si falla, crea un círculo
            self.image = pygame.Surface((15, 15), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (100, 200, 255), (7, 7), 7)
            
        self.rect = self.image.get_rect(center=(start_x, start_y))
        self.danio = 10
        
        # Calcular dirección hacia el jugador
        distancia_x = target_x - start_x
        distancia_y = target_y - start_y
        distancia = math.hypot(distancia_x, distancia_y)
        velocidad_total = 7
        
        if distancia > 0:
            self.vel_x = (distancia_x / distancia) * velocidad_total
            self.vel_y = (distancia_y / distancia) * velocidad_total
        else: # Si está justo encima, dispara hacia abajo
            self.vel_x = 0
            self.vel_y = velocidad_total
            
        self.rango = 1000
        self.distancia_recorrida = 0

    def actualizar(self, offset_x=None):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        
        # Medir la distancia para que el proyectil desaparezca eventualmente
        self.distancia_recorrida = math.hypot(self.rect.centerx - self.initial_x, self.rect.centery - self.initial_y)
        if self.distancia_recorrida > self.rango:
            self.activo = False

    def dibujar(self, s, ox, oy, z):
        if self.activo:
            s.blit(self.image, ((self.rect.x - ox) * z, (self.rect.y - oy) * z))


# En abilities.py (añadir al final)

class NightBorneHomingOrb(Proyectil):
    def __init__(self, start_x, start_y, jugador):
        super().__init__(start_x, start_y, 0)
        self.jugador = jugador # Mantiene una referencia al jugador para seguirlo
        self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (180, 0, 255), (12, 12), 12)
        pygame.draw.circle(self.image, (50, 0, 80), (12, 12), 8)
        self.rect = self.image.get_rect(center=(start_x, start_y))
        self.danio = 20
        self.velocidad = 2.5 # Es lento para que se pueda esquivar
        self.lifetime = 8000 # 8 segundos de vida
        self.creation_time = pygame.time.get_ticks()

    def actualizar(self, offset_x=None):
        if pygame.time.get_ticks() - self.creation_time > self.lifetime:
            self.activo = False
            return
            
        # Lógica para perseguir al jugador
        dist_x = self.jugador.hitbox.centerx - self.rect.centerx
        dist_y = self.jugador.hitbox.centery - self.rect.centery
        distancia = math.hypot(dist_x, dist_y)
        
        if distancia > 0:
            self.rect.x += (dist_x / distancia) * self.velocidad
            self.rect.y += (dist_y / distancia) * self.velocidad

class NightBorneEruption(Proyectil):
    def __init__(self, x, y):
        super().__init__(x, y, 0)
        self.image = pygame.Surface((80, 110), pygame.SRCALPHA) # Placeholder visual
        self.image.fill((100, 0, 150, 100)) # Un rectángulo morado semitransparente
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.danio = 35
        self.creation_time = pygame.time.get_ticks()
        self.lifetime = 700 # Dura 0.7 segundos
        self.hits_multiple = True # Puede golpear varias veces si el jugador se queda encima

    def actualizar(self, offset_x=None):
        if pygame.time.get_ticks() - self.creation_time > self.lifetime:
            self.activo = False