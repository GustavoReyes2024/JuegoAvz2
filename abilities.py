import pygame
import random
import math
from proyectiles import Proyectil
from biblioteca import *

class StaticProyectil(Proyectil):
    def __init__(self, x, y, direccion, skill_key, default_size=(30, 30), damage=0, speed=0, elemental_type="none"):
        super().__init__(x, y, direccion) 
        
        self.image = self._load_scaled_image(SKILL_ICON_PATHS.get(skill_key), default_size)
        
        if self.image:
            self.rect = self.image.get_rect(center=(x, y))
        
        self.velocidad = speed
        self.danio = damage
        self.tipo_elemental = elemental_type

        self.vel_x = self.velocidad * self.direccion
        self.vel_y = 0.0

    def _load_scaled_image(self, path, default_size):
        if path:
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, default_size)
            except pygame.error:
                print(f"⚠️ No se pudo cargar el ícono de habilidad '{path}'. Se usará un círculo de respaldo.")
                return None
        return None

    def dibujar(self, s, ox, oy, z):
        if self.activo and self.image:
            render_width = self.image.get_width() * z
            render_height = self.image.get_height() * z
            if render_width > 0 and render_height > 0:
                scaled_image = pygame.transform.scale(self.image, (int(render_width), int(render_height)))
                s.blit(scaled_image, ((self.rect.x - ox) * z, (self.rect.y - oy) * z))
        elif self.activo:
            super().dibujar(s, ox, oy, z)


class FireProjectile(StaticProyectil):
    def __init__(self, x, y, direccion):
        super().__init__(x, y, direccion, "fire", default_size=(35, 25), damage=10, speed=15, elemental_type="fuego")

class IceProjectile(StaticProyectil):
    def __init__(self, x, y, direccion):
        super().__init__(x, y, direccion, "ice", default_size=(35, 25), damage=10, speed=10, elemental_type="hielo")

class MixedProjectile(StaticProyectil):
    def __init__(self, x, y, direccion):
        super().__init__(x, y, direccion, "mixed", default_size=(50, 35), damage=60, speed=20, elemental_type="mixto")

class RockProjectile(StaticProyectil):
    def __init__(self, x, y, direccion):
        super().__init__(x, y, direccion, "rock", default_size=(30, 30), damage=15, speed=12, elemental_type="tierra")

class SartenProjectile(StaticProyectil):
    def __init__(self, x, y, direccion):
        super().__init__(x, y, direccion, "sarten", default_size=(50, 40), damage=25, speed=8, elemental_type="fisico")

class RootProjectile(StaticProyectil):
    def __init__(self, x, y, direccion):
        super().__init__(x, y, direccion, "root", default_size=(40, 20), damage=12, speed=9, elemental_type="tierra")

class EarthSpikeAttack(StaticProyectil):
    def __init__(self, x, y):
        super().__init__(x, y, 0, "earth_spike", default_size=(80, 110), damage=35, speed=0, elemental_type="tierra")
        if self.image:
            self.rect = self.image.get_rect(midbottom=(x, y))
        self.creation_time = pygame.time.get_ticks()
        self.lifetime = 600
        self.hits_multiple = True
        self.vel_x = 0
        self.vel_y = 0

    def actualizar(self, camera_offset_x=0):
        if pygame.time.get_ticks() - self.creation_time > self.lifetime:
            self.activo = False
            return
        super().actualizar(camera_offset_x)

class LightningBoltProjectile(StaticProyectil):
    def __init__(self, x, y, direccion):
        super().__init__(x, y, direccion, "lightning_bolt", default_size=(50, 15), damage=18, speed=20, elemental_type="rayo")

class DescendingLightningBolt(StaticProyectil):
    def __init__(self, x, y):
        super().__init__(x, y, 0, "lightning_strike", default_size=(20, 70), damage=15, speed=random.uniform(20, 28), elemental_type="rayo")
        if self.image:
            width = random.randint(15, 25)
            height = random.randint(50, 80)
            self.image = pygame.transform.scale(self.image, (width, height))
            self.rect = self.image.get_rect(center=(x, y))
        self.vel_x = 0
        self.vel_y = self.velocidad

    def actualizar(self, camera_offset_x=0):
        super().actualizar(camera_offset_x)

class BossDiagonalProjectile(StaticProyectil):
    def __init__(self, start_x, start_y, target_x, target_y):
        super().__init__(start_x, start_y, 0, "boss_fireball", default_size=(40, 40), damage=5)
        distancia_x = target_x - start_x
        distancia_y = target_y - start_y
        distancia = math.hypot(distancia_x, distancia_y)
        velocidad_total = 9
        if distancia > 0:
            self.vel_x = (distancia_x / distancia) * velocidad_total
            self.vel_y = (distancia_y / distancia) * velocidad_total
        else:
            self.vel_x = 0
            self.vel_y = velocidad_total
        self.rango = 1200

    def actualizar(self, camera_offset_x=0):
        super().actualizar(camera_offset_x)

class BossGroundProjectile(StaticProyectil):
    def __init__(self, x, y, direccion):
        super().__init__(x, y, direccion, "boss_groundwave", default_size=(60, 30), damage=5, speed=6)
        if self.image:
            self.rect = self.image.get_rect(midbottom=(x, y))

    def actualizar(self, camera_offset_x=0):
        super().actualizar(camera_offset_x)

class NightBorneHomingOrb(StaticProyectil):
    def __init__(self, start_x, start_y, jugador):
        super().__init__(start_x, start_y, 0, None, default_size=(25, 25), damage=20) 
        self.jugador = jugador
        self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (180, 0, 255), (12, 12), 12)
        pygame.draw.circle(self.image, (50, 0, 80), (12, 12), 8)
        self.rect = self.image.get_rect(center=(start_x, start_y))
        
        # --- PUEDES CAMBIAR ESTE VALOR PARA HACER EL ATAQUE MÁS RÁPIDO ---
        self.velocidad = 2.5 # Aumenta este número (ej. a 4.0) para más velocidad
        
        self.lifetime = 8000
        self.creation_time = pygame.time.get_ticks()
        self.vel_x = 0
        self.vel_y = 0

    def actualizar(self, camera_offset_x=0):
        if pygame.time.get_ticks() - self.creation_time > self.lifetime:
            self.activo = False
            return
        if self.jugador and self.jugador.hitbox:
            dist_x = self.jugador.hitbox.centerx - self.rect.centerx
            dist_y = self.jugador.hitbox.centery - self.rect.centery
            distancia = math.hypot(dist_x, dist_y)
            if distancia > 0:
                self.vel_x = (dist_x / distancia) * self.velocidad
                self.vel_y = (dist_y / distancia) * self.velocidad
            else:
                self.vel_x = 0
                self.vel_y = 0
        super().actualizar(camera_offset_x)

class NightBorneEruption(StaticProyectil):
    def __init__(self, x, y):
        super().__init__(x, y, 0, None, default_size=(80, 110), damage=35)
        self.image = pygame.Surface((80, 110), pygame.SRCALPHA)
        self.image.fill((100, 0, 150, 100))
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.creation_time = pygame.time.get_ticks()
        self.lifetime = 700
        self.hits_multiple = True
        self.vel_x = 0
        self.vel_y = 0

    def actualizar(self, camera_offset_x=0):
        if pygame.time.get_ticks() - self.creation_time > self.lifetime:
            self.activo = False
            return
        super().actualizar(camera_offset_x)

class MegaImpactoProjectile(StaticProyectil):
    def __init__(self, start_x, start_y, target_x):
        super().__init__(start_x, start_y, 0, "storm", default_size=(150, 80), damage=50)
        self.target_x = target_x
        self.initial_y = start_y
        self.vel_y_current = -10
        self.gravity = 0.8
        self.lifetime = 1500
        self.creation_time = pygame.time.get_ticks()
        self.state = "rising"
        if self.image:
            self.rect = self.image.get_rect(center=(start_x, start_y))
        self.hits_multiple = True
        self.vel_x = 0
        self.vel_y = 0

    def actualizar(self, camera_offset_x=0):
        elapsed_time = pygame.time.get_ticks() - self.creation_time
        if elapsed_time > self.lifetime:
            self.activo = False
            return
        if self.state == "rising":
            self.rect.y += self.vel_y_current
            self.vel_y_current += self.gravity
            if self.vel_y_current >= 0:
                self.state = "falling"
                self.vel_y_current = 0
                time_remaining_ms = self.lifetime - elapsed_time
                if time_remaining_ms > 0:
                    self.vel_x = (self.target_x - self.rect.centerx) / (time_remaining_ms / (1000 / 60))
                else:
                    self.vel_x = 0
        elif self.state == "falling":
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y_current
            self.vel_y_current += self.gravity
            if self.rect.bottom >= self.initial_y + 20:
                self.state = "impacted"
                self.vel_x = 0
                self.vel_y_current = 0
            self.vel_y = self.vel_y_current
        super().actualizar(camera_offset_x)

class FallingFireProjectile(StaticProyectil):
    def __init__(self, x, y):
        super().__init__(x, y, 0, "fire", default_size=(30, 40), damage=15, speed=random.uniform(5, 10))
        if self.image:
            self.rect = self.image.get_rect(center=(x, y))
        self.lifetime = 2000
        self.creation_time = pygame.time.get_ticks()
        self.vel_x = 0
        self.vel_y = self.velocidad

    def actualizar(self, camera_offset_x=0):
        elapsed_time = pygame.time.get_ticks() - self.creation_time
        if elapsed_time > self.lifetime:
            self.activo = False
            return
        if self.rect.top > SCREEN_HEIGHT + 50:
            self.activo = False
        super().actualizar(camera_offset_x)