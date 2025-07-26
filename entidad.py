import pygame
import sys
import random
import math
from biblioteca import *
import abilities
from biblioteca import ENEMY_INFO, ENEMY_WIDTH, ENEMY_HEIGHT, DETECTION_RADIUS, BLACK, RED_HEALTH

class Enemigo:
    def __init__(self, x, y, enemy_name):
        self.enemy_info = ENEMY_INFO.get(enemy_name)
        if not self.enemy_info:
            print(f"ERROR: No se encontró la información para el enemigo '{enemy_name}'")
            sys.exit()

        self.name = enemy_name
        self.width = self.enemy_info.get("width", ENEMY_WIDTH)
        self.height = self.enemy_info.get("height", ENEMY_HEIGHT)
        self.scale = self.enemy_info.get("scale", 1.0)
        
        self.rect = pygame.Rect(0, 0, self.width * self.scale, self.height * self.scale)
        self.rect.midbottom = (x, y)
        
        y_offset = self.enemy_info.get("y_offset", 0)
        self.rect.y += y_offset
        
        # El hitbox se inicializa aquí, pero se actualizará cada frame para ser exacto.
        self.hitbox = self.rect.copy()
        
        self.image = self._load_static_sprite(self.enemy_info.get("sprite_path"))
        self.proyectiles = []
        self.salud = self.enemy_info.get("health", 100)
        self.salud_maxima = self.salud
        self.speed = self.enemy_info.get("speed", 2)
        self.detection_radius = self.enemy_info.get("detection_radius", DETECTION_RADIUS)
        self.attack_range = self.enemy_info.get("attack_range", 80)
        self.attack_damage = self.enemy_info.get("attack_damage", 10)
        self.attack_cooldown = self.enemy_info.get("attack_cooldown", 2000)
        self.contact_damage = self.enemy_info.get("contact_damage", 0)
        self.facing_right = True
        self.is_dying = False
        self.is_dead = False
        self.last_attack_time = pygame.time.get_ticks()
        
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

    def actualizar(self, jugador):
        # --- SOLUCIÓN DEFINITIVA PARA EL HITBOX ---
        # Forzamos a que el hitbox sea una copia exacta del rectángulo principal en cada frame.
        # Esto garantiza que el área de daño siempre coincida con el cuerpo del enemigo.
        self.hitbox = self.rect.copy()

        for p in self.proyectiles[:]:
            p.actualizar()
            if not p.activo:
                self.proyectiles.remove(p)

        if self.is_dying:
            self.is_dead = True
            return

        if self.salud > 0:
            dist_x = jugador.hitbox.centerx - self.hitbox.centerx
            distancia_al_jugador = abs(dist_x)
            
            if distancia_al_jugador < self.attack_range and pygame.time.get_ticks() > self.last_attack_time + self.attack_cooldown:
                self.vel_x = 0
                jugador.tomar_danio(self.attack_damage)
                self.last_attack_time = pygame.time.get_ticks()
            elif distancia_al_jugador < self.detection_radius:
                if dist_x > 0:
                    self.vel_x = self.speed
                else:
                    self.vel_x = -self.speed
            else:
                self.vel_x = 0
            
            self.rect.x += self.vel_x
            
            if self.vel_x > 0: self.facing_right = True
            elif self.vel_x < 0: self.facing_right = False
        
    def tomar_danio(self, cantidad):
        if self.salud > 0 and not self.is_dying:
            self.salud -= abs(cantidad)
            if self.salud <= 0:
                self.salud = 0
                self.is_dying = True
                if self.death_sound:
                    self.death_sound.play()

    def dibujar(self, superficie, offset_x, offset_y, zoom):
        imagen_a_dibujar = self.image
        if not self.facing_right:
            imagen_a_dibujar = pygame.transform.flip(self.image, True, False)
        
        render_pos_x = (self.rect.x - offset_x) * zoom
        render_pos_y = (self.rect.y - offset_y) * zoom
        
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

class JefeBase(Enemigo):
    def __init__(self, x, y, enemy_name):
        super().__init__(x, y, enemy_name)
        self.is_boss = True

    def actualizar(self, jugador):
        super().actualizar(jugador)
        if self.salud <= 0 and not self.is_dying:
             self.is_dying = True
             return
        if jugador.rect.centerx < self.rect.centerx:
            self.facing_right = False
        elif jugador.rect.centerx > self.rect.centerx:
            self.facing_right = True
        ahora = pygame.time.get_ticks()
        if ahora - self.last_attack_time > self.attack_cooldown and not self.is_dying:
            self.atacar(jugador)
            self.last_attack_time = ahora

    def atacar(self, jugador):
        pass

class Jefe1(JefeBase):
    def __init__(self, x, y):
        super().__init__(x, y, "jefe1")
        self.attack_cooldown = 1800
        self.ataques_disponibles = ["diagonal", "suelo", "multiple"]

    def atacar(self, jugador):
        ataque_elegido = random.choice(self.ataques_disponibles)
        if ataque_elegido == "diagonal":
            self.proyectiles.append(abilities.BossDiagonalProjectile(self.rect.centerx, self.rect.centery, jugador.rect.centerx, jugador.rect.centery))
        elif ataque_elegido == "suelo":
            direccion = 1 if jugador.rect.centerx > self.rect.centerx else -1
            self.proyectiles.append(abilities.BossGroundProjectile(self.rect.centerx, self.rect.bottom - 20, direccion))
        elif ataque_elegido == "multiple":
            for i in range(-2, 3):
                offset_x = i * 40
                self.proyectiles.append(abilities.BossDiagonalProjectile(self.rect.centerx, self.rect.centery, jugador.rect.centerx + offset_x, jugador.rect.centery - 50))

class Jefe2(JefeBase):
    def __init__(self, x, y):
        super().__init__(x, y, "jefe2")
        self.attack_cooldown = 2200
        self.ataques_disponibles = ["homing_orb", "ground_eruption", "melee_attack"]

    def atacar(self, jugador):
        ataque_elegido = random.choice(self.ataques_disponibles)
        if ataque_elegido == "homing_orb":
            self.proyectiles.append(abilities.NightBorneHomingOrb(self.hitbox.centerx, self.hitbox.centery, jugador))
        elif ataque_elegido == "ground_eruption":
            self.proyectiles.append(abilities.NightBorneEruption(jugador.hitbox.centerx, jugador.rect.bottom))
        elif ataque_elegido == "melee_attack":
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
            self.proyectiles.append(abilities.MegaImpactoProjectile(self.hitbox.centerx, self.rect.bottom - 20, jugador.hitbox.centerx))
        elif ataque_elegido == "lluvia_de_fuego":
            for _ in range(5):
                spawn_x = random.randint(int(jugador.hitbox.centerx - 200), int(jugador.hitbox.centerx + 200))
                self.proyectiles.append(abilities.FallingFireProjectile(spawn_x, jugador.hitbox.top - 300))