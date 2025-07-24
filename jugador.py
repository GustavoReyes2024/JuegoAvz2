import pygame
import sys # Aunque no se usa directamente aquí, a menudo es útil en módulos de entidad.
import random # Necesario para la habilidad elemental de Lia

# Importar constantes y clases necesarias desde los módulos correctos
from biblioteca import (
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED, GRAVITY, JUMP_STRENGTH,
    ELEMENTAL_COOLDOWN, SPECIAL_COOLDOWN, SKILL_ICON_PATHS, PLAYER_SPRITE_PATHS,
    BLACK
)
from abilities import (
    FireProjectile, IceProjectile, MixedProjectile,
    RockProjectile, SartenProjectile, RootProjectile,
    EarthSpikeAttack, LightningBoltProjectile, DescendingLightningBolt
)
# Eliminar 'biblioteca' si su contenido se ha movido a 'constants' o ya no es necesario.
# from biblioteca import * # ELIMINADO

class Jugador:
    def __init__(self, x, y, personaje="Prota"):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.personaje = personaje

        # --- CREACIÓN DE LA HITBOX DEL JUGADOR ---
        # Creamos una hitbox 10 píxeles más estrecha y 5 más baja que el rect principal
        self.hitbox = self.rect.inflate(-10, -5)
        
        # NO HAY ANIMACIONES, solo una imagen estática
        self.static_images = {} # Almacenará la imagen estática de cada personaje
        self._load_static_sprites() # Nuevo método para cargar imágenes estáticas
        
        # La imagen actual del jugador
        self.image = self.static_images.get(self.personaje, pygame.Surface((self.width, self.height)))
        
        self.hud_icons = {}; self._load_hud_icons() # Iconos para el HUD del personaje
        self.skill_icons = {}; self._load_skill_icons() # Iconos para las habilidades
        
        self.e_skill_icon = None # Icono de habilidad E para el HUD
        self.q_skill_icon = None # Icono de habilidad Q para el HUD
        self.facing_right = True # Dirección en la que mira el jugador
        self.last_checkpoint = (x, y) # Último punto de guardado / respawn
        
        # Llamar a cambiar_personaje para inicializar la imagen y los iconos de habilidad correctos
        self.cambiar_personaje(personaje)
        
        self.vel_x = 0 # Velocidad horizontal
        self.vel_y = 0 # Velocidad vertical
        self.en_suelo = False # Booleano para saber si el jugador está en el suelo
        
        self.salud = 100 # Salud actual
        self.salud_maxima = 100 # Salud máxima
        self.proyectiles = [] # Lista de proyectiles activos del jugador
        
        self.last_attack_time_elemental = 0 # Último tiempo de ataque elemental para cooldown
        self.last_attack_time_special = 0 # Último tiempo de ataque especial para cooldown
        
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        # Sonidos de habilidad
        self.sonidos_habilidad = {
            "Prota_E": self._load_sound("sounds/lanzar_roca.wav"),
            "Prota_Q": self._load_sound("sounds/lanzar_sarten.wav"),
            "Lia_E_Fuego": self._load_sound("sounds/lanzar_fuego.wav"),
            "Lia_E_Hielo": self._load_sound("sounds/lanzar_hielo.wav"),
            "Lia_Q": self._load_sound("sounds/lanzar_mixto.wav"),
            "Kael_E": self._load_sound("sounds/lanzar_raiz.wav"),
            "Kael_Q": self._load_sound("sounds/pua_tierra.wav"),
            "Aria_E": self._load_sound("sounds/lanzar_rayo.wav"),
            "Aria_Q": self._load_sound("sounds/tormenta_rayos.wav")
        }
        # Sonidos de daño del jugador
        self.sound_male_hit = self._load_sound("sounds/male_hit.wav")
        self.sound_female_hit = self._load_sound("sounds/female_hit.wav")

    def _load_static_sprites(self):
        """Carga las imágenes estáticas para cada personaje."""
        for char_name, path in PLAYER_SPRITE_PATHS.items():
            try:
                # Cargar y escalar la imagen del personaje a su tamaño definido
                img = pygame.image.load(path).convert_alpha()
                self.static_images[char_name] = pygame.transform.scale(img, (self.width, self.height))
            except pygame.error:
                print(f"⚠️ No se pudo cargar el sprite estático para {char_name}: {path}.")
                # Fallback a una superficie negra si la imagen no se carga
                surface_negra = pygame.Surface((self.width, self.height))
                surface_negra.fill(BLACK)
                self.static_images[char_name] = surface_negra

    def _load_hud_icons(self):
        """Carga los iconos de los personajes para el HUD."""
        for name, path in PLAYER_SPRITE_PATHS.items():
            try:
                img = pygame.image.load(path).convert_alpha()
                self.hud_icons.setdefault(name, pygame.transform.scale(img, (60, 60)))
            except pygame.error:
                print(f"⚠️ No se pudo cargar icono de HUD: {path}")
    
    def _load_skill_icons(self):
        """Carga los iconos de las habilidades para el HUD."""
        for name, path in SKILL_ICON_PATHS.items():
            try:
                img = pygame.image.load(path).convert_alpha()
                self.skill_icons.setdefault(name, pygame.transform.scale(img, (32, 32)))
            except pygame.error:
                print(f"⚠️ No se pudo cargar icono de habilidad: {path}")

    def _load_sound(self, path):
        """Carga un archivo de sonido."""
        try:
            return pygame.mixer.Sound(path)
        except pygame.error as e:
            print(f"⚠️ No se pudo cargar el sonido '{path}': {e}")
            return None
            
    def cambiar_personaje(self, nuevo):
        """
        Cambia el personaje activo del jugador, actualizando su sprite y habilidades.
        """
        # Asegurarse de que el nuevo personaje tenga una imagen estática cargada
        if nuevo in self.static_images:
            self.personaje = nuevo
            self.image = self.static_images[self.personaje] # Establecer la imagen estática
            self.hud_icon = self.hud_icons.get(nuevo) # Actualizar icono del HUD
            
            # Asignar iconos de habilidad según el personaje
            if nuevo == "Prota":
                self.e_skill_icon = self.skill_icons.get("rock")
                self.q_skill_icon = self.skill_icons.get("sarten")
            elif nuevo == "Lia":
                self.e_skill_icon = self.skill_icons.get("fire") # O "ice" si quieres una elección
                self.q_skill_icon = self.skill_icons.get("mixed")
            elif nuevo == "Kael":
                self.e_skill_icon = self.skill_icons.get("root")
                self.q_skill_icon = self.skill_icons.get("earth_spike")
            elif nuevo == "Aria":
                self.e_skill_icon = self.skill_icons.get("lightning_bolt")
                self.q_skill_icon = self.skill_icons.get("storm") # "storm" puede ser DescendingLightningBolt

    # _handle_animation() ELIMINADO completamente al no haber animaciones

    def actualizar(self, teclas, plataformas, map_width, map_height):
        """
        Actualiza el estado del jugador (movimiento, gravedad, colisiones).
        """
        self.vel_x = 0
        
        # Movimiento horizontal
        if teclas[pygame.K_a]:
            self.vel_x = -PLAYER_SPEED
        if teclas[pygame.K_d]:
            self.vel_x = PLAYER_SPEED
        
        # Salto
        if teclas[pygame.K_SPACE] and self.en_suelo:
            self.vel_y = JUMP_STRENGTH
        
        # Actualizar dirección de la cara
        if self.vel_x > 0:
            self.facing_right = True
        elif self.vel_x < 0:
            self.facing_right = False
            
        # Aplicar gravedad
        self.rect.y += self.vel_y
        self.vel_y += GRAVITY
        
        # Restablecer en_suelo antes de la comprobación de colisiones
        self.en_suelo = False
        
        # Colisiones en Y con plataformas
        for plataforma in plataformas:
            if self.rect.colliderect(plataforma):
                if self.vel_y > 0: # Cayendo y golpea la parte superior de la plataforma
                    self.rect.bottom = plataforma.top
                    self.en_suelo = True
                    self.vel_y = 0
                elif self.vel_y < 0: # Saltando y golpea la parte inferior de la plataforma
                    self.rect.top = plataforma.bottom
                    self.vel_y = 0
        
        # Colisiones en X con plataformas
        self.rect.x += self.vel_x
        for plataforma in plataformas:
            if self.rect.colliderect(plataforma):
                if self.vel_x > 0: # Moviéndose a la derecha y golpea el lado izquierdo de la plataforma
                    self.rect.right = plataforma.left
                elif self.vel_x < 0: # Moviéndose a la izquierda y golpea el lado derecho de la plataforma
                    self.rect.left = plataforma.right

        # Limitar al jugador dentro de los límites del mapa
        self.rect.clamp_ip(pygame.Rect(0, 0, map_width, map_height))
        
        # --- ACTUALIZACIÓN DE LA HITBOX ---
        self.hitbox.center = self.rect.center # Mover la hitbox para que siga al jugador

    def atacar(self, tipo):
        """
        Activa una habilidad del personaje según el tipo (elemental o especial).
        """
        tiempo_actual = pygame.time.get_ticks()
        direccion_facing = 1 if self.facing_right else -1
        
        if self.personaje == "Lia":
            if tipo == "elemental" and tiempo_actual - self.last_attack_time_elemental > ELEMENTAL_COOLDOWN:
                # Lia puede lanzar fuego o hielo aleatoriamente
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
                # El ataque de EarthSpike es posicional, no se mueve en una dirección.
                # Ajustamos la posición de spawn según la dirección del jugador.
                pos_x = self.rect.centerx + (150 * direccion_facing) # Aparece delante del jugador
                pos_y = self.rect.bottom # Aparece en el suelo
                self.proyectiles.append(EarthSpikeAttack(pos_x, pos_y))
                self.last_attack_time_special = tiempo_actual
                if self.sonidos_habilidad["Kael_Q"]: self.sonidos_habilidad["Kael_Q"].play()
        
        elif self.personaje == "Aria":
            if tipo == "elemental" and tiempo_actual - self.last_attack_time_elemental > ELEMENTAL_COOLDOWN:
                self.proyectiles.append(LightningBoltProjectile(self.rect.centerx, self.rect.centery, direccion_facing))
                self.last_attack_time_elemental = tiempo_actual
                if self.sonidos_habilidad["Aria_E"]: self.sonidos_habilidad["Aria_E"].play()
            elif tipo == "special" and tiempo_actual - self.last_attack_time_special > SPECIAL_COOLDOWN:
                # La tormenta de rayos es un ataque de área
                storm_area_width = 400
                storm_center_x = self.rect.centerx + (200 * direccion_facing) # El centro de la tormenta se desplaza delante del jugador
                for _ in range(15): # Lanza 15 rayos
                    # Los rayos caen en un rango aleatorio dentro del área de la tormenta
                    rand_x = random.randint(storm_center_x - storm_area_width // 2, storm_center_x + storm_area_width // 2)
                    self.proyectiles.append(DescendingLightningBolt(rand_x, -50)) # Aparecen por encima de la pantalla
                self.last_attack_time_special = tiempo_actual
                if self.sonidos_habilidad["Aria_Q"]: self.sonidos_habilidad["Aria_Q"].play()

    def tomar_danio(self, cantidad):
        """
        Reduce la salud del jugador y reproduce un sonido de impacto.
        """
        cantidad_real = abs(cantidad) # Asegura que la cantidad de daño sea positiva
        self.salud -= cantidad_real

        # Reproducir sonido de impacto según el género del personaje
        male_characters = ["Prota", "Kael"]
        if self.personaje in male_characters:
            if self.sound_male_hit: self.sound_male_hit.play()
        else:
            if self.sound_female_hit: self.sound_female_hit.play()

        # Asegurar que la salud no baje de cero
        if self.salud < 0:
            self.salud = 0

    def dibujar(self, superficie, offset_x, offset_y, zoom):
        """
        Dibuja al jugador y sus proyectiles en la pantalla, aplicando offsets de cámara y zoom.
        """
        if self.image:
            imagen_a_dibujar = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)
            
            # Calcula la posición y el tamaño final en pantalla aplicando el zoom
            # (self.rect.x - offset_x) es la posición del personaje relativa a la esquina superior izquierda de la vista de la cámara
            render_pos_x = (self.rect.x - offset_x) * zoom
            render_pos_y = (self.rect.y - offset_y) * zoom
            render_width = self.width * zoom
            render_height = self.height * zoom
            
            # Dibuja el sprite escalado correctamente
            # Se verifica que el tamaño no sea cero para evitar errores de escalado con pygame.transform.scale
            if render_width > 0 and render_height > 0:
                # Escalamos la imagen justo antes de dibujarla, ya que la imagen en self.image
                # se cargó y escaló al tamaño original del personaje (self.width, self.height)
                superficie.blit(pygame.transform.scale(imagen_a_dibujar, (int(render_width), int(render_height))), (render_pos_x, render_pos_y))
            else:
                # Fallback para debug si el tamaño es 0
                print(f"Advertencia: Tamaño de renderizado del jugador es cero. Render Width: {render_width}, Render Height: {render_height}")

        # --- Dibuja la hitbox de depuración ---
        # Útil para visualizar la hitbox del jugador
        # if hasattr(self, 'hitbox'):
        #     debug_hitbox_rect = self.hitbox.copy()
        #     debug_hitbox_rect.x = (self.hitbox.x - offset_x) * zoom
        #     debug_hitbox_rect.y = (self.hitbox.y - offset_y) * zoom
        #     debug_hitbox_rect.width *= zoom
        #     debug_hitbox_rect.height *= zoom
        #     pygame.draw.rect(superficie, (0, 255, 0), debug_hitbox_rect, 2) # Dibuja un rectángulo verde

        # Dibuja los proyectiles del jugador
        for proyectil in self.proyectiles:
            if hasattr(proyectil, 'dibujar'): # Asegurarse de que el proyectil tiene método dibujar
                proyectil.dibujar(superficie, offset_x, offset_y, zoom)