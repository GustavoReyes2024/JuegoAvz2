import pygame
import sys
from escenas import GameScene
from dialogos import DialogueBox
from interfaz import PauseMenu

# Importar constantes necesarias
from biblioteca import ( # <-- Importar de biblioteca
    SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_HEIGHT,
    MAP_MAZMORRA_PATH, BLACK
)

class MazmorraScene(GameScene): # <-- Clase llamada MazmorraScene
    def __init__(self, screen):
        self.map_width = 2500
        self.map_height = 830
        ground_y_mazmorra = 700
        
        mazmorra_platforms = [pygame.Rect(0, ground_y_mazmorra, self.map_width, 50)]
        
        # --- ¡ESTA ES LA LÍNEA QUE HE MODIFICADO! ---
        # He añadido un Rectángulo que funciona como punto de guardado
        mazmorra_checkpoints = [
            pygame.Rect(300, 600, 50, 100) # x=300, y=600, ancho=50, alto=100
        ]
        # --- FIN DE LA MODIFICACIÓN ---

        mazmorra_interactables = []
        
        player_start = (50, ground_y_mazmorra - PLAYER_HEIGHT)
        self.initial_enemies_data = [
            (400, ground_y_mazmorra, "goblins"), 
            (800, ground_y_mazmorra, "esqueleto"),
            (1300, ground_y_mazmorra, "gole"),
        ]
        
        super().__init__(
            screen, MAP_MAZMORRA_PATH, mazmorra_platforms,
            mazmorra_checkpoints,
            mazmorra_interactables,
            player_start, self.initial_enemies_data,
            self.map_width, self.map_height, next_scene_name="mazmorrap1"
        )
        
        self.music_path = "Soundtracks/soundtrack1.mp3"
        self.name = "mazmorra_scene"
        
        self.dialogue_entrance = DialogueBox(screen, text_lines=[
            "Has entrado al oscuro umbral de la Mazmorra de las Sombras...",
            "Aquí, los débiles caen y solo los valientes avanzan."
        ], speaker_name="Narrador Misterioso")
        
        self.dialogue_trigger_x = self.map_width - 500
        self.trigger_radius = 150
        
        self.entrance_dialogue_triggered = False
        self.game_paused_by_dialogue = False
        self.entered_mazmorra_permanently = False
        
        self.door_sound = self._load_sound("sounds/door.mp3")
        self.transitioning_to_next_level = False
        self.fade_alpha = 0
        self.fade_speed = 5
        self.door_sound_played = False

    def update(self):
        if self.is_paused:
            return
        
        if self.jugador.salud <= 0:
            self.respawn_player()
            return
            
        if self.dialogue_entrance.active:
            self.dialogue_entrance.update()
            self.jugador.vel_x = 0; self.jugador.vel_y = 0
            return
            
        if self.entrance_dialogue_triggered and self.dialogue_entrance.finished and not self.transitioning_to_next_level:
            self.entered_mazmorra_permanently = True
            self.transitioning_to_next_level = True
            self.stop_background_music()

        if self.transitioning_to_next_level:
            if self.door_sound and not self.door_sound_played:
                self.door_sound.play()
                self.door_sound_played = True
            self.fade_alpha += self.fade_speed
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.running = False
            self.jugador.vel_x = 0; self.jugador.vel_y = 0
            return
        
        super().update()
        
        distance_to_trigger = abs(self.jugador.rect.centerx - self.dialogue_trigger_x)
        if not self.entrance_dialogue_triggered and distance_to_trigger <= self.trigger_radius:
            self.dialogue_entrance.start()
            self.entrance_dialogue_triggered = True
            
        if self.entered_mazmorra_permanently and self.jugador.rect.left < self.dialogue_trigger_x:
            if self.jugador.vel_x < 0:
                self.jugador.rect.left = self.dialogue_trigger_x

    def handle_input(self, evento):
        if self.is_paused:
            super().handle_input(evento)
            return
            
        if self.dialogue_entrance.active:
            self.dialogue_entrance.handle_input(evento)
        elif self.transitioning_to_next_level:
            pass
        else:
            super().handle_input(evento)

    def draw(self):
        super().draw()
        
        if self.dialogue_entrance.active:
            self.dialogue_entrance.draw()
            
        if self.transitioning_to_next_level:
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surface.fill(BLACK)
            fade_surface.set_alpha(self.fade_alpha)
            self.screen.blit(fade_surface, (0, 0))