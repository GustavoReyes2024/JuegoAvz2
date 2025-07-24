import pygame
import sys
from escenas import GameScene
# Asegúrate de que 'biblioteca' contiene lo que necesitas, si no, puedes eliminarlo
# from biblioteca import * # ELIMINADO si no se usa
from aldea import global_selected_character_g # Necesario para mantener el personaje seleccionado
from dialogos import DialogueBox
from interfaz import PauseMenu
# interactables import * # ELIMINADO si no hay interactables específicos de esta escena

# Importar constantes necesarias
from biblioteca import (
    SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_HEIGHT,
    MAP_MAZMORRA_PATH, BLACK
)
# También necesitarás importar las clases de enemigos si las instancias directamente aquí.
# Por ahora, GameScene se encargará de instanciarlos con el nombre.

class MazmorraScene(GameScene):
    def __init__(self, screen):
        self.map_width = 2500
        self.map_height = 830
        ground_y_mazmorra = 700
        
        mazmorra_platforms = [pygame.Rect(0, ground_y_mazmorra, self.map_width, 50)]
        mazmorra_checkpoints = [] # Puedes añadir checkpoints si los necesitas
        mazmorra_interactables = [] # Puedes añadir interactables si los necesitas
        
        player_start = (50, ground_y_mazmorra - PLAYER_HEIGHT)
        
        # --- LISTA DE ENEMIGOS PARA MAZMORRA_SCENE ---
        # Usando los nuevos nombres de enemigos: "esqueleto", "goblins", "gole"
        # Propuesta inicial, puedes modificarla.
        self.initial_enemies_data = [
            # Formato: (x, y, patrol_range_width, "nombre_enemigo")
            # Ajusta la 'y' para que el enemigo quede sobre la plataforma
            (400, ground_y_mazmorra - 60, 200, "goblins"),
            (800, ground_y_mazmorra - 90, 300, "esqueleto"), # Esqueleto puede ser más alto
            (1300, ground_y_mazmorra - 60, 250, "gole"),
        ]
        
        super().__init__(
            screen, MAP_MAZMORRA_PATH, mazmorra_platforms,
            mazmorra_checkpoints,
            mazmorra_interactables,
            player_start, self.initial_enemies_data,
            self.map_width, self.map_height, next_scene_name="mazmorrap1" # Transición a mazmorrap1
        )
        
        self.music_path = "Soundtracks/soundtrack1.mp3" # Música de ambiente para la mazmorra
        self.name = "escenario_mazmorra" # Nombre de la escena según la nueva estructura
        
        self.dialogue_entrance = DialogueBox(screen, text_lines=[
            "Has entrado al oscuro umbral de la Mazmorra de las Sombras...",
            "Aquí, los débiles caen y solo los valientes avanzan."
        ], speaker_name="Narrador Misterioso") # Diálogo actualizado
        
        self.dialogue_trigger_x = self.map_width - 500 # Posición X para activar el diálogo
        self.trigger_radius = 150 # Radio alrededor del trigger
        
        self.entrance_dialogue_triggered = False
        self.game_paused_by_dialogue = False # Posiblemente no necesario si el DialogueBox ya pausa el juego.
        self.entered_mazmorra_permanently = False # Bandera para control de transición
        
        self.door_sound = self._load_sound("sounds/door.mp3") # Sonido de la puerta al entrar/salir
        self.transitioning_to_next_level = False
        self.fade_alpha = 0
        self.fade_speed = 5
        self.door_sound_played = False # Para asegurar que el sonido solo se reproduce una vez

    # Nota: Los métodos update, handle_input, y draw son funcionales
    # con los cambios de arriba, pero los incluyo por completitud para que veas el archivo final.

    def update(self):
        if self.is_paused:
            return
        
        if self.jugador.salud <= 0:
            self.respawn_player()
            return
            
        # Lógica para el diálogo de entrada
        if self.dialogue_entrance.active:
            self.dialogue_entrance.update()
            self.jugador.vel_x = 0; self.jugador.vel_y = 0 # Detener jugador durante el diálogo
            return
            
        # Cuando el diálogo termina y no estamos en transición, iniciar la transición
        if self.entrance_dialogue_triggered and self.dialogue_entrance.finished and not self.transitioning_to_next_level:
            self.entered_mazmorra_permanently = True
            self.transitioning_to_next_level = True
            self.stop_background_music() # Asegúrate de que este método exista en GameScene o main

        # Lógica de desvanecimiento (fade-out) para la transición
        if self.transitioning_to_next_level:
            if self.door_sound and not self.door_sound_played:
                self.door_sound.play()
                self.door_sound_played = True
            self.fade_alpha += self.fade_speed
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.running = False # Indica al bucle de la escena que debe terminar
            self.jugador.vel_x = 0; self.jugador.vel_y = 0 # Mantener al jugador quieto durante el fade
            return
        
        # Actualización normal de la escena (movimiento del jugador, enemigos, colisiones, etc.)
        super().update()
        
        # Detectar si el jugador ha llegado al punto de activación del diálogo
        distance_to_trigger = abs(self.jugador.rect.centerx - self.dialogue_trigger_x)
        if not self.entrance_dialogue_triggered and distance_to_trigger <= self.trigger_radius:
            self.dialogue_entrance.start()
            self.entrance_dialogue_triggered = True
            
        # Evitar que el jugador retroceda más allá del punto de no retorno si ya "entró"
        if self.entered_mazmorra_permanently and self.jugador.rect.left < self.dialogue_trigger_x:
            if self.jugador.vel_x < 0: # Si el jugador intenta ir a la izquierda
                self.jugador.rect.left = self.dialogue_trigger_x # Lo mantiene en el borde

    def handle_input(self, evento):
        if self.is_paused:
            super().handle_input(evento)
            return
            
        if self.dialogue_entrance.active:
            self.dialogue_entrance.handle_input(evento)
        elif self.transitioning_to_next_level:
            pass # No se permite entrada del jugador durante la transición
        else:
            super().handle_input(evento)

    def draw(self):
        super().draw() # Dibuja el fondo del mapa, el jugador, enemigos, etc.
        
        if self.dialogue_entrance.active:
            self.dialogue_entrance.draw()
            
        # Dibujar la pantalla de desvanecimiento si la transición está activa
        if self.transitioning_to_next_level:
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surface.fill(BLACK)
            fade_surface.set_alpha(self.fade_alpha)
            self.screen.blit(fade_surface, (0, 0))