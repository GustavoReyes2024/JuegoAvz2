import pygame
import sys
import math
import random

# Importar constantes y clases necesarias desde los módulos correctos
from biblioteca import (
    SCREEN_WIDTH, SCREEN_HEIGHT, INITIAL_ZOOM, BLACK, WHITE,
    RED_HEALTH, GREEN_HEALTH, ENEMY_INFO, DEATH_QUOTES
)
from jugador import Jugador
from entidad import Enemigo, Jefe1, Jefe2, Jefe3 # Importa las clases de Enemigo y los Jefes
from visuales import HitSplat # Para el efecto visual de impacto
from interfaz import PauseMenu, DeathScreenQuote # Clases de interfaz
from guardar import save_game # Para guardar la partida
# interactables import * # ELIMINADO si los interactables se manejan de otra forma o no se usan genéricamente aquí

# Eliminar 'biblioteca' si su contenido se ha movido a 'constants' o ya no es necesario.
# from biblioteca import * # ELIMINADO

class GameScene:
    _current_music_path = None # Para evitar recargar la misma música

    def __init__(self, screen, background_path, platforms, checkpoints, interactables, player_start_pos, enemies_data, map_width, map_height, next_scene_name=None):
        self.screen = screen
        self.background_path = background_path
        self.platforms = platforms
        self.checkpoints = checkpoints
        self.interactables = interactables # Lista de objetos interactuables
        self.player_start_pos = player_start_pos
        self.enemies_data = enemies_data # Datos para spawnear enemigos
        self.next_scene_name = next_scene_name # Nombre de la siguiente escena para la transición
        self.fondo_original = self._load_background() # Carga el fondo del mapa
        self.map_width = map_width
        self.map_height = map_height
        
        # El jugador se inicializará con un personaje por defecto, luego se cambiará si hay uno guardado o seleccionado.
        self.jugador = Jugador(player_start_pos[0], player_start_pos[1], "Prota")
        
        self.enemigos = []
        self._spawn_enemies() # Llama a la función para crear los enemigos iniciales
        
        self.effects = [] # Para efectos visuales como HitSplat
        self.zoom = INITIAL_ZOOM # Nivel de zoom de la cámara
        self.reloj = pygame.time.Clock()
        self.running = True # Controla el bucle de la escena
        
        # Offsets de la cámara
        self.offset_x = 0
        self.offset_y = 0
        
        self.music_path = "Soundtracks/soundtrack1.mp3" # Música por defecto de la escena
        self.cambio_escena_activo = False # Bandera para indicar una transición de escena
        self.is_paused = False # Estado de pausa del juego
        
        # Efectos de pantalla (shake)
        self.shake_timer = 0
        self.shake_intensity = 0
        
        self.name = "" # Nombre de la escena (se establecerá en las subclases como AldeaScene, MazmorraScene)
        
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        self.pause_menu = PauseMenu(self.screen) # Menú de pausa
        self.can_save = False # Indica si se puede guardar la partida en este punto
        
        # Carga de fragmentos de llave para el HUD (ahora desde constantes si los paths están ahí)
        self.key_fragments_on = []
        self.key_fragments_off = []
        key_fragment_size = (40, 40)
        for i in range(1, 4):
            try:
                # Asegúrate de que las rutas 'interfaz/key_fragment_X_on.png' existan
                on_image = pygame.image.load(f"interfaz/key_fragment_{i}_on.png").convert_alpha()
                self.key_fragments_on.append(pygame.transform.scale(on_image, key_fragment_size))
                off_image = pygame.image.load(f"interfaz/key_fragment_{i}_off.png").convert_alpha()
                self.key_fragments_off.append(pygame.transform.scale(off_image, key_fragment_size))
            except pygame.error:
                print(f"⚠️ No se pudo cargar imagen de llave {i}.")
        self.progreso_llave = [False, False, False] # Estado de cada fragmento de llave

    def set_key_progress(self, progress):
        """Establece el progreso de los fragmentos de llave."""
        self.progreso_llave = progress

    def trigger_shake(self, duration, intensity):
        """Activa un efecto de sacudida de pantalla."""
        self.shake_timer = duration
        self.shake_intensity = intensity

    def _load_background(self):
        """Carga y escala la imagen de fondo de la escena."""
        try:
            bg = pygame.image.load(self.background_path).convert_alpha()
            return pygame.transform.scale(bg, (self.map_width, self.map_height))
        except pygame.error:
            print(f"⚠️ No se pudo cargar el fondo '{self.background_path}'. Usando color sólido.")
            temp_surface = pygame.Surface((self.map_width, self.map_height))
            temp_surface.fill((50, 50, 80)) # Color de fallback
            return temp_surface

    def _load_sound(self, path):
        """Carga un archivo de sonido."""
        if not path: return None
        try:
            return pygame.mixer.Sound(path)
        except pygame.error as e:
            print(f"⚠️ No se pudo cargar el sonido '{path}': {e}")
            return None

    def _spawn_enemies(self):
        """Instancia a los enemigos y jefes en la escena según los datos iniciales."""
        self.enemigos = [] # Limpiar enemigos existentes
        for x, y, patrol_width, enemy_name in self.enemies_data:
            enemy_info = ENEMY_INFO.get(enemy_name)
            if enemy_info:
                if enemy_name == "jefe1":
                    self.enemigos.append(Jefe1(x, y))
                elif enemy_name == "jefe2":
                    self.enemigos.append(Jefe2(x, y))
                elif enemy_name == "jefe3":
                    self.enemigos.append(Jefe3(x, y))
                # elif enemy_info.get("is_flying"): # ELIMINADO FlyingEnemy si no se usa
                #    self.enemigos.append(FlyingEnemy(x, y, enemy_name))
                else:
                    # Enemigo normal (esqueleto, goblins, gole)
                    self.enemigos.append(Enemigo(x, y, enemy_name)) # Ahora solo toma x,y,nombre
            else:
                print(f"⚠️ Advertencia: Enemigo '{enemy_name}' no encontrado en ENEMY_INFO.")
                
    def _draw_hud(self):
        """Dibuja la interfaz de usuario (HUD) en la pantalla."""
        hud_x, hud_y = 20, 20
        profile_pic_size = 60
        bar_width, bar_height = 150, 20
        skill_circle_radius = 25
        padding = 10
        hud_width = profile_pic_size + padding + bar_width + padding
        hud_height = profile_pic_size + padding + skill_circle_radius * 2 + padding
        
        hud_surface = pygame.Surface((hud_width, hud_height), pygame.SRCALPHA)
        hud_surface.fill((50, 50, 50, 180)) # Fondo semitransparente
        
        if self.jugador.hud_icon:
            hud_surface.blit(self.jugador.hud_icon, (padding, padding))
        
        # Barra de vida
        health_pct = self.jugador.salud / self.jugador.salud_maxima
        current_health_width = int(bar_width * health_pct)
        health_bar_x = padding + profile_pic_size + padding
        health_bar_y = padding + (profile_pic_size - bar_height) / 2
        pygame.draw.rect(hud_surface, RED_HEALTH, (health_bar_x, health_bar_y, bar_width, bar_height))
        pygame.draw.rect(hud_surface, GREEN_HEALTH, (health_bar_x, health_bar_y, current_health_width, bar_height))
        
        # Iconos de habilidades
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
        
        # Teclas de habilidades
        key_font = pygame.font.SysFont("arial", 14, bold=True)
        key_e_text = key_font.render("E", True, WHITE)
        key_q_text = key_font.render("Q", True, WHITE)
        hud_surface.blit(key_e_text, (skill_e_pos[0] + skill_circle_radius - 5, skill_e_pos[1] + skill_circle_radius - 15))
        hud_surface.blit(key_q_text, (skill_q_pos[0] + skill_circle_radius - 5, skill_q_pos[1] + skill_circle_radius - 15))
        
        self.screen.blit(hud_surface, (hud_x, hud_y))
        
        # Fragmentos de llave
        key_hud_x = hud_x
        key_hud_y = hud_y + hud_height + padding
        if len(self.key_fragments_on) == 3 and len(self.key_fragments_off) == 3:
            for i in range(3):
                fragment_image = self.key_fragments_on[i] if self.progreso_llave[i] else self.key_fragments_off[i]
                self.screen.blit(fragment_image, (key_hud_x + i * (40 + 5), key_hud_y))

    def play_background_music(self):
        """Reproduce la música de fondo de la escena si es diferente a la actual."""
        if not self.music_path: return
        try:
            if GameScene._current_music_path != self.music_path:
                pygame.mixer.music.load(self.music_path)
                pygame.mixer.music.play(-1) # Reproducir en bucle
                GameScene._current_music_path = self.music_path
        except pygame.error as e:
            print(f"⚠️ No se pudo cargar o reproducir la música '{self.music_path}': {e}")

    def stop_background_music(self):
        """Detiene la música de fondo."""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            GameScene._current_music_path = None

    def respawn_player(self):
        """Maneja la lógica de reaparición del jugador tras morir."""
        self.stop_background_music() # Detener música de juego al morir
        
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
        
        self.jugador.salud = self.jugador.salud_maxima # Restaurar vida
        self.jugador.rect.topleft = self.jugador.last_checkpoint # Mover al último checkpoint
        self.jugador.vel_x, self.jugador.vel_y = 0, 0 # Reiniciar velocidad
        self._spawn_enemies() # Respawnear enemigos
        self.play_background_music() # Reiniciar música de fondo

    def handle_input(self, evento):
        """Maneja los eventos de entrada del usuario."""
        if self.is_paused:
            accion = self.pause_menu.handle_event(evento, self.can_save)
            if accion == "Continuar":
                self.is_paused = False
                self.play_background_music() # Reanudar música
            elif accion == "Salir al Menú":
                self.running = False
                self.next_scene_name = None # Para salir al menú principal
                self.stop_background_music() # Asegurarse de detener la música
            elif accion == "Guardar Partida":
                if self.can_save:
                    # Guardar el estado actual del juego
                    game_data = {
                        "last_scene": self.name,
                        "progreso_llave": self.progreso_llave,
                        "personaje": self.jugador.personaje,
                        "player_pos_x": self.jugador.rect.x,
                        "player_pos_y": self.jugador.rect.y,
                        "player_health": self.jugador.salud,
                        "player_checkpoint_x": self.jugador.last_checkpoint[0],
                        "player_checkpoint_y": self.jugador.last_checkpoint[1],
                        # Puedes añadir más datos del jugador si es necesario
                    }
                    save_game(game_data)
                    self.can_save = False # Evitar guardado múltiple en el mismo checkpoint
                    self.is_paused = False
                    self.play_background_music() # Reanudar música después de guardar
        else:
            # Entrada normal del juego (movimiento del jugador, habilidades, pausa)
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.is_paused = True
                    self.stop_background_music() # Pausar música
                if evento.key == pygame.K_e and self.jugador.salud > 0:
                    self.jugador.atacar("elemental")
                if evento.key == pygame.K_q and self.jugador.salud > 0:
                    self.jugador.atacar("special")
            
            # El manejo de las teclas de movimiento y salto del jugador se hace en jugador.actualizar()

    def update(self):
        """Actualiza la lógica de la escena: jugador, enemigos, colisiones, etc."""
        if self.is_paused: return # No actualizar si está pausado
        if self.jugador.salud <= 0: self.respawn_player(); return # Manejar muerte del jugador
        
        # Lógica de la cámara con zoom y shake
        self.offset_x = self.jugador.rect.centerx - SCREEN_WIDTH // 2
        self.offset_y = self.jugador.rect.centery - SCREEN_HEIGHT // 2
        
        # Limitar el offset para no mostrar fuera de los límites del mapa
        self.offset_x = max(0, min(self.offset_x, self.map_width - SCREEN_WIDTH))
        self.offset_y = max(0, min(self.offset_y, self.map_height - SCREEN_HEIGHT))
        
        # Actualizar shake de pantalla
        if self.shake_timer > 0:
            self.shake_timer -= 1
            if self.shake_timer <= 0:
                self.shake_intensity = 0
        
        # Actualización del jugador
        teclas = pygame.key.get_pressed()
        self.jugador.actualizar(teclas, self.platforms, self.map_width, self.map_height)
        
        # Actualización de enemigos
        for enemigo in self.enemigos:
            enemigo.actualizar(self.jugador)
            
        # Lógica de checkpoints (guardar partida)
        for checkpoint in self.checkpoints:
            if self.jugador.rect.colliderect(checkpoint) and not self.can_save:
                self.jugador.last_checkpoint = checkpoint.topleft
                self.can_save = True # Habilitar guardado al llegar al checkpoint
                # Aquí se guarda automáticamente al pasar por el checkpoint por primera vez
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
        
        # Colisiones de Proyectiles del Jugador
        for proyectil in self.jugador.proyectiles[:]:
            proyectil.actualizar() # Los proyectiles ya no necesitan offset_x en su actualizar
            if not proyectil.activo:
                self.jugador.proyectiles.remove(proyectil)
                continue
            
            # Colisión con interactuables (ej. palancas, botones)
            for puzle_obj in self.interactables:
                if puzle_obj.rect.colliderect(proyectil.rect):
                    puzle_obj.interact(proyectil)
                    if not getattr(proyectil, 'hits_multiple', False): # Si no golpea múltiples objetivos, desactivar
                        proyectil.activo = False
            
            # Colisión con enemigos
            for enemigo in self.enemigos[:]:
                # Asegurarse de que el enemigo esté vivo y el proyectil activo
                if enemigo.salud > 0 and proyectil.activo and proyectil.rect.colliderect(enemigo.hitbox): # Usar hitbox del enemigo
                    enemigo.tomar_danio(proyectil.danio)
                    self.effects.append(HitSplat(proyectil.rect.centerx, proyectil.rect.centery))
                    if not getattr(proyectil, 'hits_multiple', False):
                        proyectil.activo = False
                    if not proyectil.activo: # Si el proyectil ya no está activo, salir del bucle de enemigos
                        break

        # Limpieza y Colisiones de Enemigos
        for enemigo in self.enemigos[:]:
            if enemigo.is_dead: # El flag is_dead ahora es suficiente para removerlos
                self.enemigos.remove(enemigo)
                continue
                
            # Daño por contacto del enemigo al jugador
            if enemigo.contact_damage > 0: # Solo si el enemigo causa daño por contacto
                if enemigo.salud > 0 and self.jugador.hitbox.colliderect(enemigo.hitbox):
                    self.jugador.tomar_danio(enemigo.contact_damage)
                    # Aquí podrías añadir efectos visuales o de sonido por el daño de contacto
            
            # Colisiones de proyectiles de enemigos con el jugador
            if hasattr(enemigo, 'proyectiles'):
                for proyectil_enemigo in enemigo.proyectiles[:]:
                    if proyectil_enemigo.activo and proyectil_enemigo.rect.colliderect(self.jugador.hitbox):
                        self.jugador.tomar_danio(proyectil_enemigo.danio)
                        proyectil_enemigo.activo = False # Desactivar proyectil al golpear
                        # Podrías añadir un efecto de HitSplat para el jugador también

        # Actualización de efectos visuales (splats, etc.)
        for effect in self.effects[:]:
            effect.update()
            if not effect.is_active:
                self.effects.remove(effect)
        
        # Actualización de objetos interactuables
        for puzle_obj in self.interactables:
            puzle_obj.update()

        # Condiciones de transición de escena (todos los enemigos deben estar muertos en esta escena)
        self.transition_conditions_met = (len(self.enemigos) == 0) # Ejemplo: solo transicionar si no hay enemigos

        # Transición si el jugador llega al borde derecho del mapa y se cumplen las condiciones
        if self.next_scene_name and self.jugador.rect.right >= self.map_width - 10 and not self.cambio_escena_activo and self.transition_conditions_met: # Añadir un pequeño margen al final del mapa
            self.running = False # Detener el bucle de la escena actual
            self.cambio_escena_activo = True # Indicar que se ha activado la transición

    def draw(self):
        """Dibuja todos los elementos de la escena en la pantalla."""
        render_offset_x, render_offset_y = self.offset_x, self.offset_y
        # Aplicar shake a los offsets de renderizado
        if self.shake_timer > 0:
            render_offset_x += random.randint(-self.shake_intensity, self.shake_intensity)
            render_offset_y += random.randint(-self.shake_intensity, self.shake_intensity)
            
        # Dibujar fondo escalado con offset de la cámara
        self.screen.blit(self.fondo_original, (-render_offset_x, -render_offset_y))
        
        # Dibujar interactuables
        for puzle_obj in self.interactables:
            puzle_obj.draw(self.screen, render_offset_x, render_offset_y, self.zoom)

        # Dibujar enemigos
        for enemigo in self.enemigos:
            enemigo.dibujar(self.screen, render_offset_x, render_offset_y, self.zoom)
            
        # Dibujar jugador
        self.jugador.dibujar(self.screen, render_offset_x, render_offset_y, self.zoom)
        
        # Dibujar efectos visuales
        for effect in self.effects:
            effect.draw(self.screen, render_offset_x, render_offset_y, self.zoom)
            
        # Dibujar HUD
        self._draw_hud()
        
        # Dibujar menú de pausa si está activo
        if self.is_paused:
            self.pause_menu.draw(self.can_save)

        # Dibujar rectángulos de depuración de plataformas (opcional)
        # for p in self.platforms:
        #     debug_rect = p.copy()
        #     debug_rect.x = (p.x - render_offset_x) * self.zoom
        #     debug_rect.y = (p.y - render_offset_y) * self.zoom
        #     debug_rect.width *= self.zoom
        #     debug_rect.height *= self.zoom
        #     pygame.draw.rect(self.screen, (0, 0, 255), debug_rect, 2) # Dibuja en azul

    def run(self, selected_character_for_this_scene=None, loaded_game_data=None):
        """
        Bucle principal de la escena.
        selected_character_for_this_scene: nombre del personaje si viene de una selección inicial.
        loaded_game_data: datos cargados si la partida viene de un guardado.
        """
        if loaded_game_data:
            # Si se cargó una partida, restaurar el estado del jugador
            self.jugador.cambiar_personaje(loaded_game_data["personaje"])
            self.jugador.rect.x = loaded_game_data["player_pos_x"]
            self.jugador.rect.y = loaded_game_data["player_pos_y"]
            self.jugador.salud = loaded_game_data["player_health"]
            self.jugador.last_checkpoint = (loaded_game_data["player_checkpoint_x"], loaded_game_data["player_checkpoint_y"])
            self.set_key_progress(loaded_game_data["progreso_llave"])
            self.can_save = True # Asumimos que si se cargó, ya puede guardar
        elif selected_character_for_this_scene:
            # Si viene de una selección de personaje (ej. en AldeaScene)
            self.jugador.cambiar_personaje(selected_character_for_this_scene)
            
        self.play_background_music() # Iniciar la música de la escena
        self.cambio_escena_activo = False # Resetear la bandera de transición
        
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
            
        # Devolver el nombre de la siguiente escena y el personaje actual
        return self.next_scene_name, self.jugador.personaje