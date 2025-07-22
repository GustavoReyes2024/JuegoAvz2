import pygame
import sys
import random
from constants import *
import abilities 
import spritesheet

class Enemigo:
    def __init__(self, x, y, patrol_range_width, enemy_info):
        self.enemy_info = enemy_info
        self.anim_data = self.enemy_info.get("anim_data")
        self.animations = {}
        self.scale = self.enemy_info.get("scale", 1.5)
        self._load_animations()

        if 'idle' in self.animations: self.action = 'idle'
        elif 'walk' in self.animations: self.action = 'walk'
        elif self.animations: self.action = list(self.animations.keys())[0]
        else: self.action = 'static'

        self.frame_index = 0
        if self.action in self.animations and self.animations[self.action]:
            self.image = self.animations[self.action][0]
        else: 
            self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT)); self.image.fill(BLACK)
        
        self.rect = self.image.get_rect(midbottom=(x, y))
        
        self.salud = self.enemy_info.get("health", 50)
        self.salud_maxima = self.salud
        self.speed = self.enemy_info.get("speed", ENEMY_SPEED)
        self.detection_radius = self.enemy_info.get("detection_radius", DETECTION_RADIUS)
        self.attack_range = self.enemy_info.get("attack_range", 80)
        self.attack_damage = self.enemy_info.get("attack_damage", 10)
        self.attack_cooldown = self.enemy_info.get("attack_cooldown", 2000)
        self.attack_damage_frame = self.enemy_info.get("attack_damage_frame", 3)
        self.contact_damage = self.enemy_info.get("contact_damage", 0)

        self.puntos_patrulla_izquierda = self.rect.centerx - patrol_range_width / 2
        self.puntos_patrulla_derecha = self.rect.centerx + patrol_range_width / 2
        self.vel_x = self.speed
        
        self.facing_right = True
        self.is_dying = False; self.is_dead = False
        self.last_attack_time = 0
        self.damage_dealt_this_attack = False
        self.update_time = pygame.time.get_ticks()
        

        # --- APLICACIÓN AUTOMÁTICA DEL AJUSTE DE ALTURA ---
        y_offset = self.enemy_info.get("y_offset", 0)
        self.rect.y -= y_offset
        
        if not pygame.mixer.get_init(): pygame.mixer.init()
        self.death_sound = self._load_sound(self.enemy_info.get("death_sound"))

    def _load_animations(self):
        if not self.anim_data:
            if "sprite_path" in self.enemy_info:
                path = self.enemy_info["sprite_path"]
                try:
                    img = pygame.image.load(path).convert_alpha()
                    scaled_img = pygame.transform.scale(img, (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
                    self.animations['static'] = [scaled_img]
                except pygame.error:
                    self.animations['static'] = [pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))]
            return

        if 'path' in list(self.anim_data.values())[0]:
            for anim_name, data in self.anim_data.items():
                try:
                    sprite_sheet_image = pygame.image.load(data["path"]).convert_alpha()
                    sheet = spritesheet.SpriteSheet(sprite_sheet_image)
                    temp_img_list = []
                    frame_width = sprite_sheet_image.get_width() // data['frames']
                    frame_height = sprite_sheet_image.get_height()
                    for i in range(data['frames']):
                        img = sheet.get_image(0, i, frame_width, frame_height, self.scale, BLACK)
                        temp_img_list.append(img)
                    self.animations[anim_name] = temp_img_list
                except (pygame.error, FileNotFoundError):
                    print(f"⚠️ No se pudo cargar la hoja de sprites: {data['path']}")
                    self.animations[anim_name] = [pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))]

        if 'attack' in self.animations and 'idle' not in self.animations:
            self.animations['idle'] = [self.animations['attack'][0]]
        if 'attack' in self.animations and 'walk' not in self.animations:
            self.animations['walk'] = [self.animations['attack'][0]]
    
    def _load_sound(self, path):
        if not path: return None
        try: return pygame.mixer.Sound(path)
        except pygame.error as e: print(f"⚠️ No se pudo cargar el sonido '{path}': {e}"); return None

    def update_animation(self):
        if self.action == 'static' or not self.animations.get(self.action): return
        
        # --- LÓGICA CORREGIDA PARA EVITAR EL INDEXERROR ---
        # 1. Se comprueba si es tiempo de cambiar de frame
        animation_cooldown = 120
        if self.action == 'attack':
            num_frames = len(self.animations[self.action])
            animation_cooldown = self.attack_cooldown / (num_frames + 1) if num_frames > 0 else self.attack_cooldown
        if self.action == 'die': animation_cooldown = 100
        
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        
        # 2. Se comprueba si el índice es válido ANTES de usarlo
        if self.frame_index >= len(self.animations[self.action]):
            if self.action == 'die':
                self.frame_index = len(self.animations[self.action]) - 1
                self.is_dead = True
            else:
                if self.action == 'attack':
                    self.damage_dealt_this_attack = False
                self.action = 'idle'
                self.frame_index = 0
        
        # 3. Se asigna la imagen de forma segura
        self.image = self.animations[self.action][self.frame_index]

    def actualizar(self, jugador):
        if self.is_dying or self.enemy_info.get("is_boss"):
            self.update_animation()
            return

        if self.salud > 0:
            dist_x = jugador.rect.centerx - self.rect.centerx
            distancia_al_jugador = abs(dist_x)
            
            if self.action != 'attack':
                if distancia_al_jugador < self.attack_range and pygame.time.get_ticks() > self.last_attack_time + self.attack_cooldown:
                    self.vel_x = 0
                    self.action = 'attack'
                    self.frame_index = 0
                    self.last_attack_time = pygame.time.get_ticks()
                elif distancia_al_jugador < self.detection_radius and distancia_al_jugador > self.attack_range:
                    if dist_x > 0: self.vel_x = self.speed
                    else: self.vel_x = -self.speed
                    self.action = 'walk' if 'walk' in self.animations else 'idle'
                else:
                    self.action = 'idle'
                    self.vel_x = 0
            
            if self.action == 'attack':
                if self.frame_index == self.attack_damage_frame and not self.damage_dealt_this_attack:
                    if abs(jugador.rect.centerx - self.rect.centerx) < self.attack_range + 20:
                        jugador.tomar_danio(self.attack_damage)
                        self.damage_dealt_this_attack = True
        
        self.rect.x += self.vel_x
        if self.vel_x > 0: self.facing_right = True
        elif self.vel_x < 0: self.facing_right = False
        
        self.update_animation()

    def tomar_danio(self, cantidad):
        if self.salud > 0:
            self.salud -= cantidad
            if self.salud <= 0:
                self.salud = 0
                self.action = 'die' if 'die' in self.animations else 'idle'
                if self.action not in self.animations or not self.animations[self.action]:
                    self.is_dead = True
                self.frame_index = 0
                self.is_dying = True
                if self.death_sound: self.death_sound.play()

    def dibujar(self, superficie, offset_x, offset_y, zoom):
        imagen_a_dibujar = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)
        pos_x = (self.rect.x - offset_x)
        pos_y = (self.rect.y - offset_y)
        superficie.blit(imagen_a_dibujar, (pos_x, pos_y))
        
        if not self.is_dying and not self.enemy_info.get("is_boss"):
            bar_width = self.image.get_width() * 0.8; bar_height = 6
            health_percentage = self.salud / self.salud_maxima
            current_health_width = int(bar_width * health_percentage)
            bar_pos_x = (self.rect.centerx - offset_x) - (bar_width / 2)
            bar_pos_y = (self.rect.y - offset_y) - bar_height - 10
            pygame.draw.rect(superficie, (50,0,0), (bar_pos_x, bar_pos_y, bar_width, bar_height))
            pygame.draw.rect(superficie, RED_HEALTH, (bar_pos_x, bar_pos_y, current_health_width, bar_height))

# El resto de las clases (FlyingEnemy, Boss1) se mantienen igual
# ...
# Las clases FlyingEnemy y Boss1 se mantienen igual
class FlyingEnemy(Enemigo):
    def actualizar(self, jugador):
        if self.is_dying:
            self.update_animation(); return
            
        dist_x = jugador.rect.centerx - self.rect.centerx
        dist_y = jugador.rect.centery - self.rect.centery

        if abs(dist_x) < 400 and abs(dist_y) < 250:
            self.action = 'attack' if 'attack' in self.animations else 'idle'
            self.vel_x = 2.5 * (1 if dist_x > 0 else -1)
            self.vel_y = 1.5 * (1 if dist_y > 0 else -1)
        else:
            self.action = 'idle'; self.vel_x = 0; self.vel_y = 0
        self.rect.x += self.vel_x; self.rect.y += self.vel_y
        if self.vel_x > 0: self.facing_right = False
        elif self.vel_x < 0: self.facing_right = True
        self.update_animation()

class Boss1(Enemigo):
    # Asegúrate de que el constructor de Boss1 esté corregido como te indiqué
    # para usar el nombre del enemigo ("boss1") en lugar de rutas de archivos.
    def __init__(self, x, y, enemy_name):
        enemy_info = ENEMY_INFO.get(enemy_name)
        if not enemy_info:
            print(f"ERROR: No se encontró la información para el jefe '{enemy_name}'")
            sys.exit()
        super().__init__(x, y, 0, enemy_info)
        
        self.image = pygame.transform.scale(self.image, (BOSS_WIDTH, BOSS_HEIGHT))
        self.rect.size = (BOSS_WIDTH, BOSS_HEIGHT)
        self.rect.midbottom = (x, y)
        self.salud = BOSS_HEALTH
        self.salud_maxima = BOSS_HEALTH
        self.vel_x = 0
        self.proyectiles = []
        self.attack_cooldown = 1800
        self.last_attack_time = pygame.time.get_ticks()
        self.ataques_disponibles = ["diagonal", "suelo", "multiple"]
        self.facing_right = False

    def actualizar(self, jugador):
        if jugador.rect.centerx < self.rect.centerx: self.facing_right = False
        elif jugador.rect.centerx > self.rect.centerx: self.facing_right = True
        
        for proyectil in self.proyectiles:
            proyectil.actualizar(0)
            if not proyectil.activo: self.proyectiles.remove(proyectil)
            
        ahora = pygame.time.get_ticks()
        if ahora - self.last_attack_time > self.attack_cooldown:
            self.atacar(jugador); self.last_attack_time = ahora

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

    def dibujar(self, superficie, offset_x, offset_y, zoom):
        imagen_a_dibujar = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)
        destino = self.rect.copy(); destino.x = (self.rect.x - offset_x) * zoom; destino.y = (self.rect.y - offset_y) * zoom
        destino.width = int(self.rect.width * zoom); destino.height = int(self.rect.height * zoom)
        superficie.blit(pygame.transform.scale(imagen_a_dibujar, destino.size), destino)
        
        for proyectil in self.proyectiles:
            proyectil.dibujar(superficie, offset_x, offset_y, zoom)