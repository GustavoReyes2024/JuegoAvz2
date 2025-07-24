import pygame
import random
import math
from proyectiles import Proyectil
# Asegúrate de que biblioteca.py contenga lo que necesites, si no, puedes eliminarlo
from biblioteca import *
# Importa SKILL_ICON_PATHS y otras constantes necesarias de constants.py
from biblioteca import SKILL_ICON_PATHS, SCREEN_HEIGHT 

# Clase base de proyectil para manejar la carga de imagen estática
class StaticProyectil(Proyectil):
    def __init__(self, x, y, direccion, skill_key, default_size=(30, 30), damage=0, speed=0, elemental_type="none"):
        super().__init__(x, y, direccion)
        self.image = self._load_scaled_image(SKILL_ICON_PATHS.get(skill_key), default_size)
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidad = speed
        self.danio = damage
        self.tipo_elemental = elemental_type

    def _load_scaled_image(self, path, default_size):
        if path:
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, default_size)
            except pygame.error:
                print(f"⚠️ No se pudo cargar el ícono de habilidad '{path}'. Usando cuadrado negro.")
        
        # Fallback a un cuadrado negro si la imagen no se carga
        surf = pygame.Surface(default_size, pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0)) # Completamente transparente por defecto
        # pygame.draw.rect(surf, (255, 0, 255), surf.get_rect(), 1) # Descomentar para ver el placeholder
        return surf

    def dibujar(self, s, ox, oy, z):
        if self.activo:
            s.blit(self.image, ((self.rect.x - ox) * z, (self.rect.y - oy) * z))

# Habilidades del jugador
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
        # Direccion 0 porque es un ataque estático/posicional
        super().__init__(x, y, 0, "earth_spike", default_size=(80, 110), damage=35, speed=0, elemental_type="tierra")
        self.rect = self.image.get_rect(midbottom=(x, y)) # Ajuste de posición
        self.creation_time = pygame.time.get_ticks()
        self.lifetime = 600 # Duración del ataque
        self.hits_multiple = True # Puede golpear a múltiples enemigos

    def actualizar(self): # No necesita offset_x
        if pygame.time.get_ticks() - self.creation_time > self.lifetime:
            self.activo = False

class LightningBoltProjectile(StaticProyectil):
    def __init__(self, x, y, direccion):
        super().__init__(x, y, direccion, "lightning_bolt", default_size=(50, 15), damage=18, speed=20, elemental_type="rayo")

class DescendingLightningBolt(StaticProyectil):
    def __init__(self, x, y):
        # La dirección no importa mucho para proyectiles que caen
        super().__init__(x, y, 0, "lightning_strike", default_size=(20, 70), damage=15, speed=random.uniform(20, 28), elemental_type="rayo")
        # El tamaño se puede variar aquí si se quiere cada rayo diferente
        width = random.randint(15, 25)
        height = random.randint(50, 80)
        original_image = pygame.image.load(SKILL_ICON_PATHS["lightning_strike"]).convert_alpha()
        self.image = pygame.transform.scale(original_image, (width, height))
        self.rect = self.image.get_rect(center=(x, y)) # Ajusta el centro después de escalar

    def actualizar(self): # No necesita offset_x
        self.rect.y += self.velocidad
        if self.rect.top > SCREEN_HEIGHT: # Si sale de la pantalla por abajo
            self.activo = False

# Proyectiles de los Jefes (ahora para Jefe1, Jefe2, Jefe3)
class BossDiagonalProjectile(StaticProyectil):
    def __init__(self, start_x, start_y, target_x, target_y):
        super().__init__(start_x, start_y, 0, "boss_fireball", default_size=(40, 40), damage=5) # Direccion 0 es irrelevante
        
        distancia_x = target_x - start_x
        distancia_y = target_y - start_y
        distancia = math.hypot(distancia_x, distancia_y)
        velocidad_total = 9
        
        if distancia > 0:
            self.vel_x = (distancia_x / distancia) * velocidad_total
            self.vel_y = (distancia_y / distancia) * velocidad_total
        else: # Si está justo encima, disparar hacia abajo
            self.vel_x = 0
            self.vel_y = velocidad_total
            
        self.rango = 1200 # Distancia máxima que el proyectil recorrerá
        self.initial_x = start_x # Guardar posición inicial para calcular distancia
        self.initial_y = start_y

    def actualizar(self): # No necesita offset_x
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        
        self.distancia_recorrida = math.hypot(self.rect.centerx - self.initial_x, self.rect.centery - self.initial_y)
        if self.distancia_recorrida > self.rango:
            self.activo = False

class BossGroundProjectile(StaticProyectil):
    def __init__(self, x, y, direccion):
        super().__init__(x, y, direccion, "boss_groundwave", default_size=(60, 30), damage=5, speed=6)
        self.rect = self.image.get_rect(midbottom=(x, y)) # Ajuste para que "nazca" del suelo

# Proyectiles específicos de Jefe2 (antes NightBorne)
class NightBorneHomingOrb(StaticProyectil):
    def __init__(self, start_x, start_y, jugador):
        # Como no hay imagen específica en SKILL_ICON_PATHS, creamos una simple
        super().__init__(start_x, start_y, 0, None, default_size=(25, 25), damage=20) 
        self.jugador = jugador
        # Override del image cargado por StaticProyectil para dibujar un círculo
        self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (180, 0, 255), (12, 12), 12) # Círculo morado
        pygame.draw.circle(self.image, (50, 0, 80), (12, 12), 8) # Círculo interior
        self.rect = self.image.get_rect(center=(start_x, start_y)) # Reposicionar centro después de crear la imagen
        self.velocidad = 2.5
        self.lifetime = 8000
        self.creation_time = pygame.time.get_ticks()

    def actualizar(self): # No necesita offset_x
        if pygame.time.get_ticks() - self.creation_time > self.lifetime:
            self.activo = False
            return
            
        dist_x = self.jugador.hitbox.centerx - self.rect.centerx
        dist_y = self.jugador.hitbox.centery - self.rect.centery
        distancia = math.hypot(dist_x, dist_y)
        
        if distancia > 0:
            self.rect.x += (dist_x / distancia) * self.velocidad
            self.rect.y += (dist_y / distancia) * self.velocidad

class NightBorneEruption(StaticProyectil):
    def __init__(self, x, y):
        super().__init__(x, y, 0, None, default_size=(80, 110), damage=35)
        self.image = pygame.Surface((80, 110), pygame.SRCALPHA)
        self.image.fill((100, 0, 150, 100)) # Rectángulo morado semitransparente
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.creation_time = pygame.time.get_ticks()
        self.lifetime = 700
        self.hits_multiple = True

    def actualizar(self): # No necesita offset_x
        if pygame.time.get_ticks() - self.creation_time > self.lifetime:
            self.activo = False

# Nuevos proyectiles para Jefe3
class MegaImpactoProjectile(StaticProyectil):
    def __init__(self, start_x, start_y, target_x):
        # Un gran impacto que golpea un área en el suelo
        super().__init__(start_x, start_y, 0, "storm", default_size=(150, 80), damage=50) # Usamos "storm" como placeholder
        self.target_x = target_x
        self.initial_y = start_y
        self.vel_y = -10 # Sube primero un poco para luego caer
        self.gravity = 0.8 # Más fuerte que la gravedad normal para una caída rápida
        self.lifetime = 1500 # Duración total del impacto
        self.creation_time = pygame.time.get_ticks()
        self.state = "rising" # rising, falling, impacting (si tuvieran animaciones)
        self.rect = self.image.get_rect(center=(start_x, start_y))
        self.hits_multiple = True # Puede golpear a varios en el área

    def actualizar(self):
        elapsed_time = pygame.time.get_ticks() - self.creation_time
        if elapsed_time > self.lifetime:
            self.activo = False
            return

        # Simula un pequeño salto y luego cae en el objetivo
        if self.state == "rising":
            self.rect.y += self.vel_y
            self.vel_y += self.gravity
            if self.vel_y >= 0: # Cuando empieza a caer
                self.state = "falling"
                self.vel_y = 0 # Reset de velocidad vertical para empezar la caída real
                self.vel_x = (self.target_x - self.rect.centerx) / ((self.lifetime - elapsed_time) / 1000 * 60) # Calcular velocidad X para llegar al objetivo

        elif self.state == "falling":
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y
            self.vel_y += self.gravity # Aceleración hacia abajo

            # Si llega al suelo (o cerca del initial_y), podría "impactar"
            if self.rect.bottom >= self.initial_y + 20: # Un poco por debajo del punto inicial
                self.state = "impacted"
                self.vel_x = 0
                self.vel_y = 0
                # Podrías agregar un efecto visual de impacto aquí (flash, onda expansiva)
        
        # En el estado "impacted", simplemente permanece para aplicar daño si se queda el jugador
        # La duración total está controlada por self.lifetime

class FallingFireProjectile(StaticProyectil):
    def __init__(self, x, y):
        # Este proyectil caerá desde la parte superior de la pantalla
        super().__init__(x, y, 0, "fire", default_size=(30, 40), damage=15, speed=random.uniform(5, 10)) # Reutilizamos "fire"
        self.rect = self.image.get_rect(center=(x, y)) # Posición inicial
        self.lifetime = 2000 # Duración máxima en caso de no impactar
        self.creation_time = pygame.time.get_ticks()

    def actualizar(self):
        elapsed_time = pygame.time.get_ticks() - self.creation_time
        if elapsed_time > self.lifetime:
            self.activo = False
            return
            
        self.rect.y += self.velocidad # Cae
        
        # Si llega muy abajo en la pantalla o a una posición definida de "suelo"
        if self.rect.top > SCREEN_HEIGHT + 50: # Se sale por abajo de la pantalla
            self.activo = False
            # Aquí podrías generar una pequeña explosión o efecto al "impactar" el suelo