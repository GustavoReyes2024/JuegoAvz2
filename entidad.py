import pygame
import sys
import random
import math
from biblioteca import * # Asegúrate de que 'biblioteca' contiene constantes o funciones que aún necesites.
import abilities  # Todavía necesitamos esto para los proyectiles de los jefes
from biblioteca import ENEMY_INFO, ENEMY_WIDTH, ENEMY_HEIGHT, DETECTION_RADIUS, BLACK, RED_HEALTH # Importa las constantes necesarias

# spritesheet.py YA NO ES NECESARIO si no hay animaciones
# from spritesheet import SpriteSheet # <--- ELIMINADO

class Enemigo:
    def __init__(self, x, y, enemy_name):
        self.enemy_info = ENEMY_INFO.get(enemy_name)
        if not self.enemy_info:
            print(f"ERROR: No se encontró la información para el enemigo '{enemy_name}' en constants.py")
            sys.exit()

        self.name = enemy_name
        
        self.width = self.enemy_info.get("width", ENEMY_WIDTH)
        self.height = self.enemy_info.get("height", ENEMY_HEIGHT)
        self.scale = self.enemy_info.get("scale", 1.0)
        
        self.rect = pygame.Rect(x - (self.width * self.scale / 2), y - (self.height * self.scale), self.width * self.scale, self.height * self.scale)
        
        hitbox_scale = self.enemy_info.get("hitbox_scale", (1.0, 1.0))
        hitbox_width = self.rect.width * hitbox_scale[0]
        hitbox_height = self.rect.height * hitbox_scale[1]
        self.hitbox = pygame.Rect(0, 0, hitbox_width, hitbox_height)
        
        # Carga de imagen estática
        self.image = self._load_static_sprite(self.enemy_info.get("sprite_path"))
        # No hay 'action', 'frame_index', 'animations' en este nivel para enemigos estáticos
        
        self.proyectiles = []

        self.salud = self.enemy_info.get("health", 100)
        self.salud_maxima = self.salud
        self.speed = self.enemy_info.get("speed", 2)
        self.detection_radius = self.enemy_info.get("detection_radius", DETECTION_RADIUS)
        self.attack_range = self.enemy_info.get("attack_range", 80)
        self.attack_damage = self.enemy_info.get("attack_damage", 10)
        self.attack_cooldown = self.enemy_info.get("attack_cooldown", 2000)
        # self.attack_damage_frame = self.enemy_info.get("attack_damage_frame", 3) # ELIMINADO, no hay frames de ataque
        self.contact_damage = self.enemy_info.get("contact_damage", 0)
        self.facing_right = True
        self.is_dying = False
        self.is_dead = False
        self.last_attack_time = pygame.time.get_ticks()
        # self.damage_dealt_this_attack = False # ELIMINADO, no hay frames de ataque
        # self.update_time = pygame.time.get_ticks() # ELIMINADO, no hay animación
        
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        self.death_sound = self._load_sound(self.enemy_info.get("death_sound"))

        self.vel_x = 0
        self.vel_y = 0

    def _load_static_sprite(self, path):
        if path:
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
            except pygame.error:
                print(f"⚠️ No se pudo cargar el sprite estático: {path}. Usando cuadrado negro.")
        
        # Fallback: cuadrado negro si no se encuentra la imagen
        surf = pygame.Surface((int(self.width * self.scale), int(self.height * self.scale)), pygame.SRCALPHA)
        surf.fill(BLACK)
        return surf

    def _load_sound(self, path):
        if not path: return None
        try:
            return pygame.mixer.Sound(path)
        except pygame.error as e:
            print(f"⚠️ No se pudo cargar el sonido '{path}': {e}")
            return None

    # update_animation() ELIMINADO completamente

    def actualizar(self, jugador):
        for p in self.proyectiles[:]:
            p.actualizar()
            if not p.activo:
                self.proyectiles.remove(p)

        if self.is_dying: # Si está muriendo, no hay más lógica de movimiento/ataque
            # Solo se mantiene en pantalla hasta que is_dead sea True (si hay lógica externa que lo remueva)
            # Como no hay animación de muerte, is_dead podría volverse True inmediatamente aquí
            # O se puede agregar un temporizador para simular una "duración" de la muerte.
            # Por ahora, simplemente se queda inerte.
            self.is_dead = True # Asumiendo que muere instantáneamente al llegar a 0 salud y no tiene animación.
            return

        if self.salud > 0:
            dist_x = jugador.hitbox.centerx - self.hitbox.centerx
            distancia_al_jugador = abs(dist_x)
            
            # Lógica de ataque (basada en cooldown, no en frames de animación)
            if distancia_al_jugador < self.attack_range and pygame.time.get_ticks() > self.last_attack_time + self.attack_cooldown:
                self.vel_x = 0 # Detener movimiento para atacar
                jugador.tomar_danio(self.attack_damage) # Daño directo por contacto/ataque simple
                self.last_attack_time = pygame.time.get_ticks()
            elif distancia_al_jugador < self.detection_radius:
                # Mover hacia el jugador
                if dist_x > 0:
                    self.vel_x = self.speed
                else:
                    self.vel_x = -self.speed
            else:
                self.vel_x = 0 # No está en rango de detección, no se mueve
            
            self.rect.x += self.vel_x
            
            # Actualizar dirección de la cara
            if self.vel_x > 0: self.facing_right = True
            elif self.vel_x < 0: self.facing_right = False

        hitbox_offset = self.enemy_info.get("hitbox_offset", (0, 0))
        self.hitbox.centerx = self.rect.centerx + hitbox_offset[0]
        self.hitbox.centery = self.rect.centery + hitbox_offset[1]
        
    def tomar_danio(self, cantidad):
        if self.salud > 0 and not self.is_dying:
            self.salud -= abs(cantidad)
            if self.salud <= 0:
                self.salud = 0
                self.is_dying = True # Marcar para remover/inactivar
                if self.death_sound:
                    self.death_sound.play()
                # self.is_dead se establece en actualizar() para enemigos simples
                # o cuando la "animación" de muerte (si existiera) termina.
                # Como no hay animación, se podría marcar is_dead aquí directamente.

    def dibujar(self, superficie, offset_x, offset_y, zoom):
        imagen_a_dibujar = self.image
        if not self.facing_right:
            imagen_a_dibujar = pygame.transform.flip(self.image, True, False)
        
        y_offset_sprite = self.enemy_info.get("y_offset", 0) * self.scale
        
        render_pos_x = (self.rect.x - offset_x) * zoom
        render_pos_y = (self.rect.y - offset_y + y_offset_sprite) * zoom
        
        # Escalar la imagen justo antes de dibujar si self.image no está ya escalada
        # Si self.image ya está escalada en _load_static_sprite, entonces no se reescala aquí.
        # Asumiendo que self.image ya está escalada:
        superficie.blit(imagen_a_dibujar, (render_pos_x, render_pos_y))

        for proyectil in self.proyectiles:
            proyectil.dibujar(superficie, offset_x, offset_y, zoom)

        if not self.is_dying and not self.enemy_info.get("is_boss"):
            render_width = self.rect.width * zoom
            bar_width = render_width * 0.8
            bar_height = 6 * zoom if zoom > 0.5 else 3
            health_percentage = self.salud / self.salud_maxima
            current_health_width = int(bar_width * health_percentage)
            
            bar_pos_x = ((self.rect.centerx - offset_x) * zoom) - (bar_width / 2)
            bar_pos_y = ((self.rect.top - offset_y) * zoom) - bar_height - (5 * zoom)
            
            pygame.draw.rect(superficie, (50,0,0), (bar_pos_x, bar_pos_y, bar_width, bar_height))
            if current_health_width > 0:
                pygame.draw.rect(superficie, RED_HEALTH, (bar_pos_x, bar_pos_y, current_health_width, bar_height))

        # Dibujar hitbox de depuración (opcional)
        # debug_rect = pygame.Rect((self.hitbox.x - offset_x) * zoom, (self.hitbox.y - offset_y) * zoom, self.hitbox.width * zoom, self.hitbox.height * zoom)
        # pygame.draw.rect(superficie, (255, 0, 0), debug_rect, 2)
            
# --- CLASES DE JEFES ---
# Los jefes también serán estáticos, pero mantendrán su lógica de ataque compleja.

# entidad.py (fragmento de JefeBase y Jefe1)

class JefeBase(Enemigo):
    def __init__(self, x, y, enemy_name):
        super().__init__(x, y, enemy_name)
        self.is_boss = True

    def actualizar(self, jugador):
        super().actualizar(jugador) # Esto actualiza los proyectiles del jefe también

        if self.salud <= 0 and not self.is_dying:
             self.is_dying = True # Marca que el jefe está muriendo
             return # No permitir que el jefe ataque si está muriendo

        # Lógica de facing del jefe
        if jugador.rect.centerx < self.rect.centerx:
            self.facing_right = False
        elif jugador.rect.centerx > self.rect.centerx:
            self.facing_right = True
        
        # Lógica de ataque de jefe
        ahora = pygame.time.get_ticks()
        if ahora - self.last_attack_time > self.attack_cooldown and not self.is_dying: # Solo ataca si no está muriendo
            self.atacar(jugador)
            self.last_attack_time = ahora

    def atacar(self, jugador):
        pass # Debe ser sobrescrito por subclases

class Jefe1(JefeBase):
    def __init__(self, x, y):
        super().__init__(x, y, "jefe1")
        self.attack_cooldown = 1800 # Asegúrate de que este cooldown no sea demasiado alto
        self.ataques_disponibles = ["diagonal", "suelo", "multiple"]

    def atacar(self, jugador):
        ataque_elegido = random.choice(self.ataques_disponibles)
        if ataque_elegido == "diagonal":
            nuevo_proyectil = abilities.BossDiagonalProjectile(self.rect.centerx, self.rect.centery, jugador.rect.centerx, jugador.rect.centery)
            self.proyectiles.append(nuevo_proyectil)
        elif ataque_elegido == "suelo":
            direccion = 1 if jugador.rect.centerx > self.rect.centerx else -1
            nuevo_proyectil = abilities.BossGroundProjectile(self.rect.centerx, self.rect.bottom - 20, direccion)
            self.proyectiles.append(nuevo_proyectil)
        elif ataque_elegido == "multiple":
            for i in range(-2, 3):
                offset_x = i * 40
                nuevo_proyectil = abilities.BossDiagonalProjectile(self.rect.centerx, self.rect.centery, jugador.rect.centerx + offset_x, jugador.rect.centery - 50)
                self.proyectiles.append(nuevo_proyectil)
        
        # Como no hay animaciones, no establecemos self.action = 'attack'
        # El proyectil se crea directamente.
        
class Jefe2(JefeBase):
    def __init__(self, x, y):
        super().__init__(x, y, "jefe2")
        self.attack_cooldown = 2200
        self.ataques_disponibles = ["homing_orb", "ground_eruption", "melee_attack"]

    def atacar(self, jugador):
        ataque_elegido = random.choice(self.ataques_disponibles)
        
        if ataque_elegido == "homing_orb":
            nuevo_proyectil = abilities.NightBorneHomingOrb(self.hitbox.centerx, self.hitbox.centery, jugador)
            self.proyectiles.append(nuevo_proyectil)
        
        elif ataque_elegido == "ground_eruption":
            nuevo_proyectil = abilities.NightBorneEruption(jugador.hitbox.centerx, jugador.rect.bottom)
            self.proyectiles.append(nuevo_proyectil)
            
        elif ataque_elegido == "melee_attack":
            # Aquí, si es un ataque melee y no hay animación, es daño directo por cercanía
            if abs(jugador.hitbox.centerx - self.hitbox.centerx) < self.attack_range + 50:
                jugador.tomar_danio(self.attack_damage)

class Jefe3(JefeBase):
    def __init__(self, x, y):
        super().__init__(x, y, "jefe3")
        self.attack_cooldown = 2500
        self.ataques_disponibles = ["mega_impacto", "lluvia_de_fuego"]

    def atacar(self, jugador):
        ataque_elegido = random.choice(self.ataques_disponibles)

        if ataque_elegido == "mega_impacto":
            nuevo_proyectil = abilities.MegaImpactoProjectile(self.hitbox.centerx, self.rect.bottom - 20, jugador.hitbox.centerx)
            self.proyectiles.append(nuevo_proyectil)
            
        elif ataque_elegido == "lluvia_de_fuego":
            for _ in range(5):
                spawn_x = random.randint(int(jugador.hitbox.centerx - 200), int(jugador.hitbox.centerx + 200))
                nuevo_proyectil = abilities.FallingFireProjectile(spawn_x, jugador.hitbox.top - 300)
                self.proyectiles.append(nuevo_proyectil)