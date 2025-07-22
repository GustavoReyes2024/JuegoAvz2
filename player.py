import pygame
import sys
import random
from constants import *
from abilities import *

class Jugador:
    def __init__(self, x, y, personaje="Prota"):
        self.width = PLAYER_WIDTH; self.height = PLAYER_HEIGHT
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.personaje = personaje
        
        self.animation_frames = {}; self.action = 'idle'; self.current_frame_index = 0
        self.last_animation_update = pygame.time.get_ticks()
        self.run_animation_cooldown = 150; self.idle_animation_cooldown = 300

        self._load_animation_sprites()
        self.image = self.animation_frames.get(self.personaje, {}).get('idle', [pygame.Surface((self.width, self.height))])[0]
        
        self.hud_icons = {}; self._load_hud_icons()
        self.skill_icons = {}; self._load_skill_icons()
        
        self.e_skill_icon = None; self.q_skill_icon = None
        self.facing_right = True; self.last_checkpoint = (x, y)
        self.cambiar_personaje(personaje)
        
        self.vel_x = 0; self.vel_y = 0; self.en_suelo = False
        self.salud = 100; self.salud_maxima = 100; self.proyectiles = []
        self.last_attack_time_elemental = 0; self.last_attack_time_special = 0
        
        if not pygame.mixer.get_init(): pygame.mixer.init()
        self.sonidos_habilidad = {
            "Prota_E": self._load_sound("sounds/lanzar_roca.wav"), "Prota_Q": self._load_sound("sounds/lanzar_sarten.wav"),
            "Lia_E_Fuego": self._load_sound("sounds/lanzar_fuego.wav"), "Lia_E_Hielo": self._load_sound("sounds/lanzar_hielo.wav"),
            "Lia_Q": self._load_sound("sounds/lanzar_mixto.wav"), "Kael_E": self._load_sound("sounds/lanzar_raiz.wav"),
            "Kael_Q": self._load_sound("sounds/pua_tierra.wav"), "Aria_E": self._load_sound("sounds/lanzar_rayo.wav"),
            "Aria_Q": self._load_sound("sounds/tormenta_rayos.wav")
        }
        self.sound_male_hit = self._load_sound("sounds/male_hit.wav")
        self.sound_female_hit = self._load_sound("sounds/female_hit.wav")

    def _load_animation_sprites(self):
        for char_name, anim_info in PLAYER_ANIMATION_DATA.items():
            self.animation_frames[char_name] = {}
            for anim_name, anim_data in anim_info.items():
                path = f"Characters/{char_name.lower()}_{anim_name}.png"
                try:
                    sprite_sheet = pygame.image.load(path).convert_alpha()
                    num_frames = anim_data['frames']
                    frame_width = sprite_sheet.get_width() // num_frames
                    frame_height = sprite_sheet.get_height()
                    frames = []
                    for i in range(num_frames):
                        frame_surface = sprite_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
                        frames.append(pygame.transform.scale(frame_surface, (self.width, self.height)))
                    self.animation_frames[char_name][anim_name] = frames
                except (pygame.error, FileNotFoundError):
                    print(f"⚠️ No se pudo cargar hoja de sprites: {path}.")
                    try:
                        fallback_img_path = PLAYER_SPRITE_PATHS[char_name]
                        fallback_img = pygame.transform.scale(pygame.image.load(fallback_img_path).convert_alpha(), (self.width, self.height))
                        self.animation_frames[char_name][anim_name] = [fallback_img]
                    except (pygame.error, FileNotFoundError):
                        surface_negra = pygame.Surface((self.width, self.height)); surface_negra.fill(BLACK)
                        self.animation_frames[char_name][anim_name] = [surface_negra]

    def _load_hud_icons(self):
        for name, path in PLAYER_SPRITE_PATHS.items():
            try:
                img = pygame.image.load(path).convert_alpha()
                self.hud_icons.setdefault(name, pygame.transform.scale(img, (60, 60)))
            except pygame.error: print(f"⚠️ No se pudo cargar icono de HUD: {path}")
    
    def _load_skill_icons(self):
        for name, path in SKILL_ICON_PATHS.items():
            try:
                img = pygame.image.load(path).convert_alpha()
                self.skill_icons.setdefault(name, pygame.transform.scale(img, (32, 32)))
            except pygame.error: print(f"⚠️ No se pudo cargar icono de habilidad: {path}")

    def _load_sound(self, path):
        try: return pygame.mixer.Sound(path)
        except pygame.error as e: print(f"⚠️ No se pudo cargar el sonido '{path}': {e}"); return None
    
    def cambiar_personaje(self, nuevo):
        if nuevo in self.animation_frames:
            self.personaje = nuevo; self.action = 'idle'; self.current_frame_index = 0
            self.image = self.animation_frames[self.personaje][self.action][self.current_frame_index]
            self.hud_icon = self.hud_icons.get(nuevo)
            if nuevo == "Prota": self.e_skill_icon = self.skill_icons.get("rock"); self.q_skill_icon = self.skill_icons.get("sarten")
            elif nuevo == "Lia": self.e_skill_icon = self.skill_icons.get("fire"); self.q_skill_icon = self.skill_icons.get("mixed")
            elif nuevo == "Kael": self.e_skill_icon = self.skill_icons.get("root"); self.q_skill_icon = self.skill_icons.get("earth_spike")
            elif nuevo == "Aria": self.e_skill_icon = self.skill_icons.get("lightning_bolt"); self.q_skill_icon = self.skill_icons.get("storm")

    def _handle_animation(self):
        new_action = 'run' if self.vel_x != 0 else 'idle'
        if self.action != new_action:
            self.action = new_action; self.current_frame_index = 0
        cooldown = self.run_animation_cooldown if self.action == 'run' else self.idle_animation_cooldown
        current_time = pygame.time.get_ticks()
        if current_time - self.last_animation_update > cooldown:
            self.last_animation_update = current_time
            anim_list = self.animation_frames[self.personaje][self.action]
            if anim_list:
                self.current_frame_index = (self.current_frame_index + 1) % len(anim_list)
                self.image = anim_list[self.current_frame_index]

    def actualizar(self, teclas, plataformas, map_width, map_height):
        self.vel_x = 0
        if teclas[pygame.K_a]: self.vel_x = -PLAYER_SPEED
        if teclas[pygame.K_d]: self.vel_x = PLAYER_SPEED
        if teclas[pygame.K_SPACE] and self.en_suelo: self.vel_y = JUMP_STRENGTH
        if self.vel_x > 0: self.facing_right = True
        elif self.vel_x < 0: self.facing_right = False
        
        self.rect.y += self.vel_y
        self.vel_y += GRAVITY
        self.en_suelo = False
        for plataforma in plataformas:
            if self.rect.colliderect(plataforma):
                if self.vel_y > 0: self.rect.bottom = plataforma.top; self.en_suelo = True; self.vel_y = 0
                elif self.vel_y < 0: self.rect.top = plataforma.bottom; self.vel_y = 0
        
        self.rect.x += self.vel_x
        for plataforma in plataformas:
            if self.rect.colliderect(plataforma):
                if self.vel_x > 0: self.rect.right = plataforma.left
                elif self.vel_x < 0: self.rect.left = plataforma.right

        self.rect.clamp_ip(pygame.Rect(0, 0, map_width, map_height))
        self._handle_animation()

    def atacar(self, tipo):
        tiempo_actual = pygame.time.get_ticks()
        direccion_facing = 1 if self.facing_right else -1
        if self.personaje == "Lia":
            if tipo == "elemental" and tiempo_actual - self.last_attack_time_elemental > ELEMENTAL_COOLDOWN:
                if random.choice([True, False]):
                    self.proyectiles.append(FireProjectile(self.rect.centerx, self.rect.centery, direccion_facing))
                    if self.sonidos_habilidad["Lia_E_Fuego"]: self.sonidos_habilidad["Lia_E_Fuego"].play()
                else:
                    self.proyectiles.append(IceProjectile(self.rect.centerx, self.rect.centery, direccion_facing))
                    if self.sonidos_habilidad["Lia_E_Hielo"]: self.sonidos_habilidad["Lia_E_Hielo"].play()
                self.last_attack_time_elemental = tiempo_actual
            elif tipo == "special" and tiempo_actual - self.last_attack_time_special > SPECIAL_COOLDOWN:
                self.proyectiles.append(MixedProjectile(self.rect.centerx, self.rect.centery, direccion_facing))
                self.last_attack_time_special = tiempo_actual
                if self.sonidos_habilidad["Lia_Q"]: self.sonidos_habilidad["Lia_Q"].play()
        elif self.personaje == "Prota":
            if tipo == "elemental" and tiempo_actual - self.last_attack_time_elemental > ELEMENTAL_COOLDOWN:
                self.proyectiles.append(RockProjectile(self.rect.centerx, self.rect.centery, direccion_facing))
                self.last_attack_time_elemental = tiempo_actual
                if self.sonidos_habilidad["Prota_E"]: self.sonidos_habilidad["Prota_E"].play()
            elif tipo == "special" and tiempo_actual - self.last_attack_time_special > SPECIAL_COOLDOWN:
                self.proyectiles.append(SartenProjectile(self.rect.centerx, self.rect.centery, direccion_facing))
                self.last_attack_time_special = tiempo_actual
                if self.sonidos_habilidad["Prota_Q"]: self.sonidos_habilidad["Prota_Q"].play()
        elif self.personaje == "Kael":
            if tipo == "elemental" and tiempo_actual - self.last_attack_time_elemental > ELEMENTAL_COOLDOWN:
                self.proyectiles.append(RootProjectile(self.rect.centerx, self.rect.centery, direccion_facing))
                self.last_attack_time_elemental = tiempo_actual
                if self.sonidos_habilidad["Kael_E"]: self.sonidos_habilidad["Kael_E"].play()
            elif tipo == "special" and tiempo_actual - self.last_attack_time_special > SPECIAL_COOLDOWN:
                pos_x = self.rect.centerx + (150 * direccion_facing); pos_y = self.rect.bottom
                self.proyectiles.append(EarthSpikeAttack(pos_x, pos_y))
                self.last_attack_time_special = tiempo_actual
                if self.sonidos_habilidad["Kael_Q"]: self.sonidos_habilidad["Kael_Q"].play()
        elif self.personaje == "Aria":
            if tipo == "elemental" and tiempo_actual - self.last_attack_time_elemental > ELEMENTAL_COOLDOWN:
                self.proyectiles.append(LightningBoltProjectile(self.rect.centerx, self.rect.centery, direccion_facing))
                self.last_attack_time_elemental = tiempo_actual
                if self.sonidos_habilidad["Aria_E"]: self.sonidos_habilidad["Aria_E"].play()
            elif tipo == "special" and tiempo_actual - self.last_attack_time_special > SPECIAL_COOLDOWN:
                storm_area_width = 400; storm_center_x = self.rect.centerx + (200 * direccion_facing)
                for _ in range(15):
                    rand_x = random.randint(storm_center_x - storm_area_width // 2, storm_center_x + storm_area_width // 2)
                    self.proyectiles.append(DescendingLightningBolt(rand_x, -50))
                self.last_attack_time_special = tiempo_actual
                if self.sonidos_habilidad["Aria_Q"]: self.sonidos_habilidad["Aria_Q"].play()

    def tomar_danio(self, cantidad):
        self.salud -= cantidad
        male_characters = ["Prota", "Kael"]
        if self.personaje in male_characters:
            if self.sound_male_hit: self.sound_male_hit.play()
        else: 
            if self.sound_female_hit: self.sound_female_hit.play()
        if self.salud < 0: self.salud = 0

    def dibujar(self, superficie, offset_x, offset_y, zoom):
        destino = self.rect.copy();
        destino.x = (self.rect.x - offset_x) * zoom;
        destino.y = (self.rect.y - offset_y) * zoom;
        destino.width = int(self.width * zoom);
        destino.height = int(self.height * zoom)
        
        if self.image:
            imagen_a_dibujar = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)
            superficie.blit(imagen_a_dibujar, destino)
        
        for proyectil in self.proyectiles:
            if hasattr(proyectil, 'dibujar'):
                proyectil.dibujar(superficie, offset_x, offset_y, zoom)