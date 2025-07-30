import pygame
import random
import math
from proyectiles import Proyectil
from biblioteca import * # Importa SCREEN_WIDTH, SKILL_ICON_PATHS, etc.

class StaticProyectil(Proyectil):
    def __init__(self, x, y, direccion, skill_key, default_size=(30, 30), damage=0, speed=0, elemental_type="none"):
        super().__init__(x, y, direccion)
        
        self.default_size = default_size

        self.image = self._load_scaled_image(SKILL_ICON_PATHS.get(skill_key), self.default_size)
        
        if self.image:
            self.rect = self.image.get_rect(center=(x, y))
        else:
            self.rect = pygame.Rect(x, y, self.default_size[0], self.default_size[1])
            if skill_key is not None: 
                print(f"ADVERTENCIA: Proyectil {type(self).__name__} sin imagen para '{skill_key}', usando rect básico.")
            
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
        if self.activo:
            if self.image is None:
                super().dibujar(s, ox, oy, z)
                return

            render_width = self.image.get_width() * z
            render_height = self.image.get_height() * z
            
            render_pos_x = (self.rect.x - ox) * z
            render_pos_y = (self.rect.y - oy) * z
            
            if render_width > 0 and render_height > 0:
                scaled_image = pygame.transform.scale(self.image, (int(render_width), int(render_height)))
                s.blit(scaled_image, (render_pos_x, render_pos_y))
            else:
                pygame.draw.circle(s, (255, 0, 255), (render_pos_x, render_pos_y), int(20 * z))


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
        else:
             self.rect = pygame.Rect(x, y, 20, 70)

        self.vel_x = 0
        self.vel_y = self.velocidad

    def actualizar(self, camera_offset_x=0):
        super().actualizar(camera_offset_x)

class BossDiagonalProjectile(StaticProyectil):
    def __init__(self, start_x, start_y, target_x, target_y):
        super().__init__(start_x, start_y, 0, "boss_fireball", default_size=(40, 40), damage=3)
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
        # Usamos el sprite "boss_groundwave"
        super().__init__(x, y, direccion, "boss_groundwave", default_size=(60, 30), damage=5, speed=8, elemental_type="fisico")
        
        # Ajustamos la posición para que aparezca sobre el suelo
        if self.image:
            self.rect = self.image.get_rect(midbottom=(x, y))
        
        self.vel_y = 0 # Nos aseguramos de que no tenga movimiento vertical

    def actualizar(self, camera_offset_x=0):
        super().actualizar(camera_offset_x) # Llama para movimiento y desactivación de pantalla

# Proyectiles específicos de Jefe2
class NightBorneHomingOrb(StaticProyectil):
    def __init__(self, start_x, start_y, jugador):
        super().__init__(start_x, start_y, 0, None, default_size=(25, 25), damage=20) 
        
        self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (180, 0, 255), (12, 12), 12)
        pygame.draw.circle(self.image, (50, 0, 80), (12, 12), 8)
        self.rect = self.image.get_rect(center=(start_x, start_y))
        self.velocidad = 8.0
        self.lifetime = 2000

        if jugador and hasattr(jugador, 'hitbox'):
            dist_x = jugador.hitbox.centerx - self.rect.centerx
            dist_y = jugador.hitbox.centery - self.rect.centery
            distancia = math.hypot(dist_x, dist_y)
            
            if distancia > 0:
                self.vel_x = (dist_x / distancia) * self.velocidad
                self.vel_y = (dist_y / distancia) * self.velocidad
            else:
                self.vel_x = 0
                self.vel_y = self.velocidad
        else:
            self.vel_x = self.velocidad * self.direccion
            self.vel_y = 0
        
        self.creation_time = pygame.time.get_ticks()

    def actualizar(self, camera_offset_x=0):
        if pygame.time.get_ticks() - self.creation_time > self.lifetime:
            self.activo = False
            return
            
        super().actualizar(camera_offset_x)


class NightBorneEruption(StaticProyectil):
    def __init__(self, x, y):
        super().__init__(x, y, 0, None, default_size=(200, 100), damage=0) 
        
        self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.image.fill((255, 0, 0, 255))
        
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.creation_time = pygame.time.get_ticks()
        self.lifetime = 1500
        self.hits_multiple = True
        
        self.vel_x = 0
        self.vel_y = 0

        self.dot_damage = 5
        self.damage_interval = 500
        self.last_damage_tick = pygame.time.get_ticks()
        self.active_for_damage = False

    def actualizar(self, camera_offset_x=0):
        current_time = pygame.time.get_ticks()

        if current_time - self.creation_time > self.lifetime:
            self.activo = False
            return
        
        self.active_for_damage = True

        super().actualizar(camera_offset_x)

# --- NUEVA CLASE PARA JEFE 2: Proyectil que cae ---
class BossFallingProjectile(StaticProyectil):
    def __init__(self, x, y):
        # Usamos el sprite "boss_fireball" como base. Puedes cambiarlo si tienes otro.
        # Ajustamos el daño y tamaño para que sea un ataque de jefe.
        super().__init__(x, y, 0, "boss_fireball", default_size=(50, 50), damage=15, speed=random.uniform(7, 10), elemental_type="fuego")
        
        # Hacemos que el proyectil empiece desde arriba de la pantalla, no desde el jefe
        self.rect.centerx = x
        self.rect.bottom = 0  # Inicia justo en el borde superior de la pantalla
        
        self.lifetime = 5000  # 5 segundos de vida para cruzar la pantalla
        self.creation_time = pygame.time.get_ticks()

        # Aseguramos que solo se mueva hacia abajo
        self.vel_x = 0
        self.vel_y = self.velocidad

    def actualizar(self, camera_offset_x=0):
        # Desactivamos el proyectil si su tiempo de vida expira
        if pygame.time.get_ticks() - self.creation_time > self.lifetime:
            self.activo = False
            return
        
        # Desactivamos si sale por la parte inferior de la pantalla
        if self.rect.top > pygame.display.get_surface().get_height():
            self.activo = False
            return
        
        # Llamamos al método de la clase padre para que aplique el movimiento
        super().actualizar(camera_offset_x)


class MegaImpactoProjectile(StaticProyectil):
    def __init__(self, start_x, start_y, target_x):
        super().__init__(start_x, start_y, 0, "storm", default_size=(200, 150), damage=10)
        self.target_x = target_x
        self.initial_y = start_y
        self.vel_y_current = -15
        self.gravity = 1.0
        self.lifetime = 4000
        self.creation_time = pygame.time.get_ticks()
        self.state = "rising"
        if self.image:
            self.rect = self.image.get_rect(center=(start_x, start_y))
        self.hits_multiple = True

        self.vel_x = 0
        self.vel_y = 0

        self.dot_damage = 10
        self.damage_interval = 200
        self.last_damage_tick = pygame.time.get_ticks()
        self.active_for_damage = False

    def actualizar(self, camera_offset_x=0):
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.creation_time
        
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
                self.active_for_damage = True
                self.lifetime = current_time + 1000
            
            self.vel_y = self.vel_y_current

        elif self.state == "impacted":
            pass

        super().actualizar(camera_offset_x)


# --- Reintroducido: FallingFireProjectile (para el ataque de lluvia de fuego) ---
class FallingFireProjectile(StaticProyectil):
    def __init__(self, x, y):
        # Aseguramos que sea hits_multiple y con daño directo al impactar
        super().__init__(x, y, 0, "fire", default_size=(60, 80), damage=5, speed=random.uniform(8, 12), elemental_type="fire")
        if self.image:
            self.rect = self.image.get_rect(center=(x, y))
        self.lifetime = 4000
        self.creation_time = pygame.time.get_ticks()
        self.vel_x = 0
        self.vel_y = self.velocidad
        self.hits_multiple = True # <-- ¡IMPORTANTE! Para que no desaparezca al primer golpe.

    def actualizar(self, camera_offset_x=0):
        elapsed_time = pygame.time.get_ticks() - self.creation_time

        if elapsed_time > self.lifetime:
            self.activo = False
            return

        if self.rect.top > pygame.display.get_surface().get_height() + 50:
            self.activo = False

        super().actualizar(camera_offset_x)


# --- Reutilizamos ElectricRayDiagonal (para el rayo diagonal LINEAL) ---
class ElectricRayDiagonal(StaticProyectil):
    def __init__(self, start_x, start_y, target_x, target_y):
        # Aumentar daño para el rayo diagonal inicial.
        # Ajustar default_size para que sea más un "haz" o "bola" si el sprite original no rota bien.
        super().__init__(start_x, start_y, 0, "lightning_bolt", default_size=(50, 20), damage=5, speed=20, elemental_type="rayo")
        
        self.original_image = self._load_scaled_image(SKILL_ICON_PATHS.get("lightning_bolt"), self.default_size)
        if self.original_image:
            angle = math.degrees(math.atan2(target_y - start_y, target_x - start_x))
            self.image = pygame.transform.rotate(self.original_image, -angle) 
            self.rect = self.image.get_rect(center=(start_x, start_y))
        else:
            self.image = None
            self.rect = pygame.Rect(start_x, start_y, self.default_size[0], self.default_size[1])
            print(f"ADVERTENCIA: ElectricRayDiagonal sin imagen, usando rect básico.")

        dist_x = target_x - start_x
        dist_y = target_y - start_y
        distancia = math.hypot(dist_x, dist_y)
        
        if distancia > 0:
            self.vel_x = (dist_x / distancia) * self.velocidad
            self.vel_y = (dist_y / distancia) * self.velocidad
        else:
            self.vel_x = 0
            self.vel_y = self.velocidad
        
        self.lifetime = 1500 # Dura más tiempo para cruzar la pantalla.
        self.creation_time = pygame.time.get_ticks()

    def actualizar(self, camera_offset_x=0):
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.creation_time

        if elapsed_time > self.lifetime:
            self.activo = False
            return
        
        super().actualizar(camera_offset_x)


# --- NUEVA CLASE: BossGroundLightning (Rayo que CAE desde el cielo para Jefe 3) ---
class BossGroundLightning(StaticProyectil):
    def __init__(self, x, y): # x es la posición del jugador, y es el suelo
        # Este ataque es el que aparece bajo el jugador y lo mata de un solo.
        # Ajustamos el tamaño para que se vea, y el daño para que no mate de un solo golpe.
        # También vamos a hacer que CAIGA desde arriba, con un efecto de "warning" o una aparición más lenta.
        super().__init__(x, y, 0, "lightning_strike", default_size=(80, 150), damage=2, speed=random.uniform(5, 8), elemental_type="rayo") # <-- DAÑO y VELOCIDAD DE CAÍDA ajustados
        
        self.initial_ground_y = y # Guardar la Y del suelo donde se debe golpear
        
        # Posición inicial para que CAIGA desde MUY ARRIBA de la pantalla.
        # self.rect.centerx ya está en x del jugador.
        self.rect.y = y - (SCREEN_HEIGHT + self.default_size[1] + random.randint(100, 300)) # Aparece por encima del techo visible
        
        # La imagen ya se escala en super().__init__. Solo necesitamos ajustar su rect si es necesario.
        if self.image:
            self.rect = self.image.get_rect(center=(x, self.rect.centery)) # Re-centrar usando la nueva Y
        else:
            self.rect = pygame.Rect(x, self.rect.y, self.default_size[0], self.default_size[1])
            print(f"ADVERTENCIA: BossGroundLightning sin imagen, usando rect básico.")

        self.lifetime = 2500 # Aumentado a 2.5 segundos para que tenga tiempo de caer y verse. <-- LIFETIME AJUSTADO
        self.creation_time = pygame.time.get_ticks()
        self.hits_multiple = False # Un rayo suele hacer daño una vez (al impactar)
        
        self.vel_x = 0
        self.vel_y = self.velocidad # Usa la velocidad de caída definida en super().__init__

        self.has_damaged_player = False # Bandera para asegurar daño una vez por colisión

    def actualizar(self, camera_offset_x=0):
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.creation_time

        if elapsed_time > self.lifetime:
            self.activo = False
            return
        
        # La lógica de movimiento base (self.rect.y += self.vel_y) ya está en super().actualizar
        
        # Desactivar cuando llegue al suelo o caiga fuera de la pantalla.
        # Usamos initial_ground_y como referencia del suelo.
        if self.rect.bottom >= self.initial_ground_y or self.rect.top > pygame.display.get_surface().get_height() + 50:
            self.activo = False
            # Opcional: Aquí podrías activar un efecto visual de impacto en el suelo si lo deseas.
            
        super().actualizar(camera_offset_x)