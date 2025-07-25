import pygame
import random
import math
from proyectiles import Proyectil # Clase base de proyectil
from biblioteca import * # Importa todas las constantes (SCREEN_WIDTH, SKILL_ICON_PATHS, etc.)

# Clase base de proyectil estático que carga la imagen y la escala
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
                print(f"⚠️ No se pudo cargar el ícono de habilidad '{path}'. Usando cuadrado transparente.")
        
        # Fallback a un cuadrado transparente si la imagen no se carga
        surf = pygame.Surface(default_size, pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0)) # Completamente transparente
        return surf

    def dibujar(self, s, ox, oy, z):
        if self.activo:
            # Asegurarse de que la imagen se escala al tamaño de renderizado final para el zoom
            render_width = self.image.get_width() * z
            render_height = self.image.get_height() * z
            if render_width > 0 and render_height > 0:
                scaled_image = pygame.transform.scale(self.image, (int(render_width), int(render_height)))
                s.blit(scaled_image, ((self.rect.x - ox) * z, (self.rect.y - oy) * z))
            else:
                # Fallback para depuración si la imagen es 0 o invisible (dibuja un círculo blanco)
                pygame.draw.circle(s, WHITE, ((self.rect.x - ox) * z, (self.rect.y - oy) * z), int(5 * z))


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
        super().__init__(x, y, 0, "earth_spike", default_size=(80, 110), damage=35, speed=0, elemental_type="tierra")
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.creation_time = pygame.time.get_ticks()
        self.lifetime = 600
        self.hits_multiple = True

    def actualizar(self, camera_offset_x=0):
        if pygame.time.get_ticks() - self.creation_time > self.lifetime:
            self.activo = False
            return
        # La lógica de desactivación de la clase base también se aplica aquí
        super().actualizar(camera_offset_x)

class LightningBoltProjectile(StaticProyectil):
    def __init__(self, x, y, direccion):
        super().__init__(x, y, direccion, "lightning_bolt", default_size=(50, 15), damage=18, speed=20, elemental_type="rayo")

class DescendingLightningBolt(StaticProyectil):
    def __init__(self, x, y):
        # NOTA: Aunque StaticProyectil carga la imagen por defecto,
        # este proyectil sobrescribe para tener un tamaño y orientación aleatorios.
        super().__init__(x, y, 0, "lightning_strike", default_size=(20, 70), damage=15, speed=random.uniform(20, 28), elemental_type="rayo")
        width = random.randint(15, 25)
        height = random.randint(50, 80)
        # Asegúrate de que SKILL_ICON_PATHS["lightning_strike"] existe y la imagen es adecuada.
        original_image = pygame.image.load(SKILL_ICON_PATHS["lightning_strike"]).convert_alpha()
        self.image = pygame.transform.scale(original_image, (width, height))
        self.rect = self.image.get_rect(center=(x, y))

    def actualizar(self, camera_offset_x=0):
        self.rect.y += self.velocidad
        # Llama a la lógica de desactivación de la clase base
        super().actualizar(camera_offset_x)


# Proyectiles de los Jefes
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
        else: # Si está justo encima, disparar hacia abajo
            self.vel_x = 0
            self.vel_y = velocidad_total
            
        self.rango = 1200 # Rango de vida del proyectil
        self.initial_x = start_x
        self.initial_y = start_y

    def actualizar(self, camera_offset_x=0):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        # Llama a la lógica de desactivación de la clase base
        super().actualizar(camera_offset_x)

class BossGroundProjectile(StaticProyectil):
    def __init__(self, x, y, direccion):
        super().__init__(x, y, direccion, "boss_groundwave", default_size=(60, 30), damage=5, speed=6)
        self.rect = self.image.get_rect(midbottom=(x, y))

    def actualizar(self, camera_offset_x=0):
        # Los proyectiles de suelo generalmente solo se mueven horizontalmente y tienen un rango/vida
        # Es necesario moverlos aquí si su velocidad no es 0
        self.rect.x += self.velocidad * self.direccion # Mover el proyectil horizontalmente
        super().actualizar(camera_offset_x) # Llama a la lógica de desactivación de la clase base

# Proyectiles específicos de Jefe2
class NightBorneHomingOrb(StaticProyectil):
    def __init__(self, start_x, start_y, jugador):
        super().__init__(start_x, start_y, 0, None, default_size=(25, 25), damage=20) 
        self.jugador = jugador
        # Override del image cargado por StaticProyectil para dibujar un círculo
        self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (180, 0, 255), (12, 12), 12) # Círculo morado
        pygame.draw.circle(self.image, (50, 0, 80), (12, 12), 8) # Círculo interior
        self.rect = self.image.get_rect(center=(start_x, start_y))
        self.velocidad = 2.5 # Velocidad de seguimiento
        self.lifetime = 8000 # Duración de vida del orbe
        self.creation_time = pygame.time.get_ticks()

    def actualizar(self, camera_offset_x=0):
        if pygame.time.get_ticks() - self.creation_time > self.lifetime:
            self.activo = False
            return
            
        # Lógica para perseguir al jugador
        if self.jugador and self.jugador.hitbox: # Asegurarse de que el jugador exista
            dist_x = self.jugador.hitbox.centerx - self.rect.centerx
            dist_y = self.jugador.hitbox.centery - self.rect.centery
            distancia = math.hypot(dist_x, dist_y)
            
            if distancia > 0:
                self.rect.x += (dist_x / distancia) * self.velocidad
                self.rect.y += (dist_y / distancia) * self.velocidad
        
        # Llama a la lógica de desactivación de la clase base
        super().actualizar(camera_offset_x)


class NightBorneEruption(StaticProyectil):
    def __init__(self, x, y):
        super().__init__(x, y, 0, None, default_size=(80, 110), damage=35)
        self.image = pygame.Surface((80, 110), pygame.SRCALPHA)
        self.image.fill((100, 0, 150, 100)) # Rectángulo morado semitransparente
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.creation_time = pygame.time.get_ticks()
        self.lifetime = 700 # Duración del efecto de erupción
        self.hits_multiple = True

    def actualizar(self, camera_offset_x=0):
        if pygame.time.get_ticks() - self.creation_time > self.lifetime:
            self.activo = False
            return
        # Llama a la lógica de desactivación de la clase base
        super().actualizar(camera_offset_x)

# Nuevos proyectiles para Jefe3
class MegaImpactoProjectile(StaticProyectil):
    def __init__(self, start_x, start_y, target_x):
        super().__init__(start_x, start_y, 0, "storm", default_size=(150, 80), damage=50) # Usamos "storm" como placeholder
        self.target_x = target_x # El punto X en el suelo donde impactará
        self.initial_y = start_y # La Y inicial del proyectil (probablemente sobre el jugador)
        self.vel_y = -10 # Sube un poco antes de caer
        self.gravity = 0.8 # Gravedad que lo acelera hacia abajo
        self.lifetime = 1500 # Duración total del impacto (1.5 segundos)
        self.creation_time = pygame.time.get_ticks()
        self.state = "rising" # rising, falling, impacted
        self.rect = self.image.get_rect(center=(start_x, start_y))
        self.hits_multiple = True

    def actualizar(self, camera_offset_x=0):
        elapsed_time = pygame.time.get_ticks() - self.creation_time
        if elapsed_time > self.lifetime:
            self.activo = False
            return

        if self.state == "rising":
            self.rect.y += self.vel_y
            self.vel_y += self.gravity
            if self.vel_y >= 0: # Cuando la velocidad vertical se vuelve no negativa, empieza a caer
                self.state = "falling"
                self.vel_y = 0 # Reset de velocidad vertical para empezar la caída real
                # Calcula la velocidad X para llegar al target_x en el tiempo restante
                time_remaining_ms = self.lifetime - elapsed_time
                if time_remaining_ms > 0:
                    # Convierta ms a ticks para evitar división por cero
                    self.vel_x = (self.target_x - self.rect.centerx) / (time_remaining_ms / (1000 / 60)) # Asumiendo 60 FPS
                else:
                    self.vel_x = 0

        elif self.state == "falling":
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y
            self.vel_y += self.gravity # Sigue acelerando hacia abajo

            # Si llega al suelo (o cerca del initial_y), cambia a estado "impacted"
            if self.rect.bottom >= self.initial_y + 20: # Un poco por debajo del punto inicial
                self.state = "impacted"
                self.vel_x = 0
                self.vel_y = 0
        
        # Llama a la lógica de desactivación de la clase base (para que desaparezca si sale de pantalla)
        super().actualizar(camera_offset_x)


class FallingFireProjectile(StaticProyectil):
    def __init__(self, x, y):
        super().__init__(x, y, 0, "fire", default_size=(30, 40), damage=15, speed=random.uniform(5, 10))
        self.rect = self.image.get_rect(center=(x, y)) # Posición inicial (probablemente por encima de la pantalla)
        self.lifetime = 2000 # Duración máxima en caso de no impactar el suelo
        self.creation_time = pygame.time.get_ticks()

    def actualizar(self, camera_offset_x=0):
        elapsed_time = pygame.time.get_ticks() - self.creation_time
        if elapsed_time > self.lifetime:
            self.activo = False
            return
            
        self.rect.y += self.velocidad # Cae
        
        # Si llega muy abajo en la pantalla (o a una posición definida de "suelo")
        if self.rect.top > SCREEN_HEIGHT + 50: # Se sale por abajo de la pantalla
            self.activo = False
            # Aquí podrías generar una pequeña explosión o efecto al "impactar" el suelo
            
        # Llama a la lógica de desactivación de la clase base para el rango/fuera de pantalla
        super().actualizar(camera_offset_x)