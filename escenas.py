import pygame
import sys
import math
import random

# Importar constantes y clases necesarias desde biblioteca.py
from biblioteca import ( # <-- Importar de biblioteca
    SCREEN_WIDTH, SCREEN_HEIGHT, INITIAL_ZOOM, BLACK, WHITE,
    RED_HEALTH, GREEN_HEALTH, ENEMY_INFO, DEATH_QUOTES,
    FONT_SMALL, FONT_MEDIUM # Asegurarse que FONT_MEDIUM también esté aquí si se usa en _draw_hud
)
from jugador import Jugador
from entidad import Enemigo, Jefe1, Jefe2, Jefe3 # Asegúrate de que las clases de Jefe estén aquí
from visuales import HitSplat
from interfaz import PauseMenu, DeathScreenQuote
from guardar import save_game

class GameScene:
    _current_music_path = None

    def __init__(self, screen, background_path, platforms, checkpoints, interactables, player_start_pos, enemies_data, map_width, map_height, next_scene_name=None):
        self.screen = screen
        self.background_path = background_path
        self.platforms = platforms
        self.checkpoints = checkpoints
        self.interactables = interactables
        self.player_start_pos = player_start_pos
        self.enemies_data = enemies_data # Datos para spawnear enemigos
        self.next_scene_name = next_scene_name
        self.fondo_original = self._load_background()
        self.map_width = map_width
        self.map_height = map_height
        
        self.jugador = Jugador(player_start_pos[0], player_start_pos[1], "Prota")
        
        self.enemigos = []
        self._spawn_enemies()
        
        self.effects = []
        self.zoom = INITIAL_ZOOM
        self.reloj = pygame.time.Clock()
        self.running = True
        
        self.offset_x = 0 # Offset X de la cámara
        self.offset_y = 0 # Offset Y de la cámara
        
        self.music_path = "Soundtracks/soundtrack1.mp3"
        self.cambio_escena_activo = False
        self.is_paused = False
        
        self.shake_timer = 0
        self.shake_intensity = 0
        
        self.name = "" # Nombre de la escena
        
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        self.pause_menu = PauseMenu(self.screen)
        self.can_save = False
        
        # Carga de fragmentos de llave
        self.key_fragments_on = []
        self.key_fragments_off = []
        key_fragment_size = (40, 40)
        for i in range(1, 4):
            try:
                # Las rutas aquí son relativas al directorio principal del juego.
                on_image = pygame.image.load(f"interfaz/key_fragment_{i}_on.png").convert_alpha()
                self.key_fragments_on.append(pygame.transform.scale(on_image, key_fragment_size))
                off_image = pygame.image.load(f"interfaz/key_fragment_{i}_off.png").convert_alpha()
                self.key_fragments_off.append(pygame.transform.scale(off_image, key_fragment_size))
            except pygame.error:
                print(f"⚠️ No se pudo cargar imagen de llave {i}.")
        self.progreso_llave = [False, False, False]

    def set_key_progress(self, progress):
        self.progreso_llave = progress

    def trigger_shake(self, duration, intensity):
        self.shake_timer = duration
        self.shake_intensity = intensity

    def _load_background(self):
        try:
            bg = pygame.image.load(self.background_path).convert_alpha()
            return pygame.transform.scale(bg, (self.map_width, self.map_height))
        except pygame.error:
            print(f"⚠️ No se pudo cargar el fondo '{self.background_path}'. Usando color sólido.")
            temp_surface = pygame.Surface((self.map_width, self.map_height))
            temp_surface.fill((50, 50, 80))
            return temp_surface

    def _load_sound(self, path):
        if not path: return None
        try:
            return pygame.mixer.Sound(path)
        except pygame.error as e:
            print(f"⚠️ No se pudo cargar el sonido '{path}': {e}")
            return None

    def _spawn_enemies(self):
        """Instancia a los enemigos y jefes en la escena según los datos iniciales."""
        self.enemigos = []
        # ¡CORREGIDO: SOLO SE ESPERAN 3 VALORES EN LA TUPLA!
        for x, y, enemy_name in self.enemies_data:
            enemy_info = ENEMY_INFO.get(enemy_name)
            if enemy_info:
                if enemy_name == "jefe1":
                    self.enemigos.append(Jefe1(x, y))
                elif enemy_name == "jefe2":
                    self.enemigos.append(Jefe2(x, y))
                elif enemy_name == "jefe3":
                    self.enemigos.append(Jefe3(x, y))
                else:
                    self.enemigos.append(Enemigo(x, y, enemy_name))
            else:
                print(f"⚠️ Advertencia: Enemigo '{enemy_name}' no encontrado en ENEMY_INFO.")
                
    def _draw_hud(self):
        hud_x, hud_y = 20, 20
        profile_pic_size = 60
        bar_width, bar_height = 150, 20
        skill_circle_radius = 25
        padding = 10
        hud_width = profile_pic_size + padding + bar_width + padding
        hud_height = profile_pic_size + padding + skill_circle_radius * 2 + padding
        
        hud_surface = pygame.Surface((hud_width, hud_height), pygame.SRCALPHA)
        hud_surface.fill((50, 50, 50, 180))
        
        if self.jugador.hud_icon:
            hud_surface.blit(self.jugador.hud_icon, (padding, padding))
        
        health_pct = self.jugador.salud / self.jugador.salud_maxima
        current_health_width = int(bar_width * health_pct)
        health_bar_x = padding + profile_pic_size + padding
        health_bar_y = padding + (profile_pic_size - bar_height) / 2
        pygame.draw.rect(hud_surface, RED_HEALTH, (health_bar_x, health_bar_y, bar_width, bar_height))
        pygame.draw.rect(hud_surface, GREEN_HEALTH, (health_bar_x, health_bar_y, current_health_width, bar_height))
        
        skills_y = padding + profile_pic_size + padding
        skill_e_pos = (padding + skill_circle_radius, skills_y + skill_circle_radius)
        pygame.draw.circle(hud_surface, (255, 255, 255, 50), skill_e_pos, skill_circle_radius)
        if self.jugador.e_skill_icon:
            icon_rect = self.jugador.e_skill_icon.get_rect(center=skill_e_pos)
            hud_surface.blit(self.jugador.e_skill_icon, icon_rect)
            
        skill_q_pos = (padding + skill_circle_radius * 3 + padding, skills_y + skill_circle_radius)
        pygame.draw.circle(hud_surface, (255, 255, 255, 50), skill_q_pos, skill_circle_radius)
        if self.jugador.q_skill_icon:
            icon_rect = self.jugador.q_skill_icon.get_rect(center=skill_q_pos)
            hud_surface.blit(self.jugador.q_skill_icon, icon_rect)
        
        key_font = FONT_SMALL
        key_e_text = key_font.render("E", True, WHITE)
        key_q_text = key_font.render("Q", True, WHITE)
        hud_surface.blit(key_e_text, (skill_e_pos[0] + skill_circle_radius - 5, skill_e_pos[1] + skill_circle_radius - 15))
        hud_surface.blit(key_q_text, (skill_q_pos[0] + skill_circle_radius - 5, skill_q_pos[1] + skill_circle_radius - 15))
        
        self.screen.blit(hud_surface, (hud_x, hud_y))
        
        key_hud_x = hud_x
        key_hud_y = hud_y + hud_height + padding
        if len(self.key_fragments_on) == 3 and len(self.key_fragments_off) == 3:
            for i in range(3):
                fragment_image = self.key_fragments_on[i] if self.progreso_llave[i] else self.key_fragments_off[i]
                self.screen.blit(fragment_image, (key_hud_x + i * (40 + 5), key_hud_y))

    def play_background_music(self):
        if not self.music_path: return
        try:
            if GameScene._current_music_path != self.music_path:
                pygame.mixer.music.load(self.music_path)
                pygame.mixer.music.play(-1)
                GameScene._current_music_path = self.music_path
        except pygame.error as e:
            print(f"⚠️ No se pudo cargar o reproducir la música '{self.music_path}': {e}")

    def stop_background_music(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            GameScene._current_music_path = None

    def respawn_player(self):
        self.stop_background_music()
        
        quote, author = random.choice(DEATH_QUOTES)
        death_screen = DeathScreenQuote(self.screen, quote, author)
        waiting_for_input = True
        while waiting_for_input:
            death_screen.draw()
            continue_text = FONT_SMALL.render("Presiona ENTER para reaparecer...", True, WHITE)
            continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            self.screen.blit(continue_text, continue_rect)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    waiting_for_input = False
        
        self.jugador.salud = self.jugador.salud_maxima
        self.jugador.rect.topleft = self.jugador.last_checkpoint
        self.jugador.vel_x, self.jugador.vel_y = 0, 0
        self._spawn_enemies()
        self.play_background_music()

    def handle_input(self, evento):
        if self.is_paused:
            accion = self.pause_menu.handle_event(evento, self.can_save)
            if accion == "Continuar":
                self.is_paused = False
                self.play_background_music()
            elif accion == "Salir al Menú":
                self.running = False
                self.next_scene_name = None
                self.stop_background_music()
            elif accion == "Guardar Partida":
                if self.can_save:
                    game_data = {
                        "last_scene": self.name,
                        "progreso_llave": self.progreso_llave,
                        "personaje": self.jugador.personaje,
                        "player_pos_x": self.jugador.rect.x,
                        "player_pos_y": self.jugador.rect.y,
                        "player_health": self.jugador.salud,
                        "player_checkpoint_x": self.jugador.last_checkpoint[0],
                        "player_checkpoint_y": self.jugador.last_checkpoint[1],
                    }
                    save_game(game_data)
                    self.can_save = False
                    self.is_paused = False
                    self.play_background_music()
        else:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.is_paused = True
                    self.stop_background_music()
                if evento.key == pygame.K_e and self.jugador.salud > 0:
                    self.jugador.atacar("elemental")
                if evento.key == pygame.K_q and self.jugador.salud > 0:
                    self.jugador.atacar("special")

    def update(self):
        if self.is_paused: return
        if self.jugador.salud <= 0: self.respawn_player(); return
        
        self.offset_x = self.jugador.rect.centerx - SCREEN_WIDTH // 2
        self.offset_y = self.jugador.rect.centery - SCREEN_HEIGHT // 2
        
        self.offset_x = max(0, min(self.offset_x, self.map_width - SCREEN_WIDTH))
        self.offset_y = max(0, min(self.offset_y, self.map_height - SCREEN_HEIGHT))
        
        if self.shake_timer > 0:
            self.shake_timer -= 1
            if self.shake_timer <= 0:
                self.shake_intensity = 0
        
        teclas = pygame.key.get_pressed()
        self.jugador.actualizar(teclas, self.platforms, self.map_width, self.map_height)
        
        for enemigo in self.enemigos:
            enemigo.actualizar(self.jugador)
            
        for checkpoint in self.checkpoints:
            if self.jugador.rect.colliderect(checkpoint) and not self.can_save:
                self.jugador.last_checkpoint = checkpoint.topleft
                self.can_save = True
                game_data = {
                    "last_scene": self.name,
                    "progreso_llave": self.progreso_llave,
                    "personaje": self.jugador.personaje,
                    "player_pos_x": self.jugador.rect.x,
                    "player_pos_y": self.jugador.rect.y,
                    "player_health": self.jugador.salud,
                    "player_checkpoint_x": self.jugador.last_checkpoint[0],
                    "player_checkpoint_y": self.jugador.last_checkpoint[1],
                }
                save_game(game_data)
        
        for proyectil in self.jugador.proyectiles[:]:
            proyectil.actualizar(self.offset_x) # <--- PASANDO offset_x
            if not proyectil.activo:
                self.jugador.proyectiles.remove(proyectil)
                continue
            
            for puzle_obj in self.interactables:
                if puzle_obj.rect.colliderect(proyectil.rect):
                    puzle_obj.interact(proyectil)
                    if not getattr(proyectil, 'hits_multiple', False):
                        proyectil.activo = False
            
            for enemigo in self.enemigos[:]:
                if enemigo.salud > 0 and proyectil.activo and proyectil.rect.colliderect(enemigo.hitbox):
                    enemigo.tomar_danio(proyectil.danio)
                    self.effects.append(HitSplat(proyectil.rect.centerx, proyectil.rect.centery))
                    if not getattr(proyectil, 'hits_multiple', False):
                        proyectil.activo = False
                    if not proyectil.activo:
                        break

        for enemigo in self.enemigos[:]:
            if enemigo.is_dead:
                self.enemigos.remove(enemigo)
                continue
                
            if enemigo.contact_damage > 0:
                if enemigo.salud > 0 and self.jugador.hitbox.colliderect(enemigo.hitbox):
                    self.jugador.tomar_danio(enemigo.contact_damage)
            
            if hasattr(enemigo, 'proyectiles'):
                for proyectil_enemigo in enemigo.proyectiles[:]:
                    proyectil_enemigo.actualizar(self.offset_x) # <--- PASANDO offset_x
                    if proyectil_enemigo.activo and proyectil_enemigo.rect.colliderect(self.jugador.hitbox):
                        self.jugador.tomar_danio(proyectil_enemigo.danio)
                        proyectil_enemigo.activo = False

        for effect in self.effects[:]:
            effect.update()
            if not effect.is_active: self.effects.remove(effect)
        
        for puzle_obj in self.interactables:
            puzle_obj.update()

        self.transition_conditions_met = (len(self.enemigos) == 0)
        
        if self.next_scene_name and self.jugador.rect.right >= self.map_width - 10 and not self.cambio_escena_activo and self.transition_conditions_met:
            self.running = False
            self.cambio_escena_activo = True

    def draw(self):
        render_offset_x, render_offset_y = self.offset_x, self.offset_y
        if self.shake_timer > 0:
            render_offset_x += random.randint(-self.shake_intensity, self.shake_intensity)
            render_offset_y += random.randint(-self.shake_intensity, self.shake_intensity)
            
        self.screen.blit(self.fondo_original, (-render_offset_x, -render_offset_y))
        
        for puzle_obj in self.interactables:
            puzle_obj.draw(self.screen, render_offset_x, render_offset_y, self.zoom)

        for enemigo in self.enemigos:
            enemigo.dibujar(self.screen, render_offset_x, render_offset_y, self.zoom)
            
        self.jugador.dibujar(self.screen, render_offset_x, render_offset_y, self.zoom)
        
        for effect in self.effects:
            effect.draw(self.screen, render_offset_x, render_offset_y, self.zoom)
            
        self._draw_hud()
        
        if self.is_paused:
            self.pause_menu.draw(self.can_save)

    def run(self, selected_character_for_this_scene=None, loaded_game_data=None):
        if loaded_game_data:
            self.jugador.cambiar_personaje(loaded_game_data["personaje"])
            self.jugador.rect.x = loaded_game_data["player_pos_x"]
            self.jugador.rect.y = loaded_game_data["player_pos_y"]
            self.jugador.salud = loaded_game_data["player_health"]
            self.jugador.last_checkpoint = (loaded_game_data["player_checkpoint_x"], loaded_game_data["player_checkpoint_y"])
            self.set_key_progress(loaded_game_data["progreso_llave"])
            self.can_save = True
        elif selected_character_for_this_scene:
            self.jugador.cambiar_personaje(selected_character_for_this_scene)
            
        self.play_background_music()
        self.cambio_escena_activo = False
        
        while self.running:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()
                self.handle_input(evento)
                
            if not self.is_paused:
                self.update()
                
            self.draw()
            pygame.display.flip()
            self.reloj.tick(60)
            
        return self.next_scene_name, self.jugador.personaje