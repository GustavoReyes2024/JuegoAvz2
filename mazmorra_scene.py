import pygame
from game_scene import GameScene
from constants import *
from aldea_scene import global_selected_character_g
from dialogue import DialogueBox 
from ui import PauseMenu
from interactables import *

class MazmorraScene(GameScene):
    def __init__(self, screen): 
        self.map_width = 2500 
        self.map_height = 830 
        ground_y_mazmorra = 700
        
        mazmorra_platforms = [ pygame.Rect(0, ground_y_mazmorra, self.map_width, 50) ]
        mazmorra_checkpoints = []
        mazmorra_interactables = []
        
        player_start = (50, ground_y_mazmorra - PLAYER_HEIGHT)
        
        # --- LISTA SIMPLIFICADA ---
        self.initial_enemies_data = [
            (400, ground_y_mazmorra-45, 200, "lobo"),
            (800, ground_y_mazmorra-45, 300, "lobo"),
            (1300, ground_y_mazmorra-45, 250, "lobo"),
        ]
        
        super().__init__(
            screen, MAP_MAZMORRA_PATH, mazmorra_platforms, 
            mazmorra_checkpoints,
            mazmorra_interactables,
            player_start, self.initial_enemies_data, 
            self.map_width, self.map_height, next_scene_name="mazmorra_p1"
        )
        
        self.music_path = "Soundtracks/soundtrack1.mp3"
        self.name = "mazmorra"
        
        self.dialogue_entrance = DialogueBox(screen, text_lines=["..."], speaker_name="Ecos del Abismo")
        self.dialogue_trigger_x = self.map_width - 500; self.trigger_radius = 150
        self.entrance_dialogue_triggered = False; self.game_paused_by_dialogue = False  
        self.entered_mazmorra_permanently = False 
        self.door_sound = self._load_sound("sounds/door.mp3")
        self.transitioning_to_next_level = False; self.fade_alpha = 0; self.fade_speed = 5
        self.door_sound_played = False

    # El resto de la clase (update, handle_input, draw) se mantiene igual
    # ...

    def update(self):
        if self.is_paused: return
        if self.jugador.salud <= 0:
            self.respawn_player(); return
            
        if self.dialogue_entrance.active:
            self.dialogue_entrance.update(); self.jugador.vel_x = 0; self.jugador.vel_y = 0; return
            
        if self.entrance_dialogue_triggered and self.dialogue_entrance.finished and not self.transitioning_to_next_level:
            self.entered_mazmorra_permanently = True; self.transitioning_to_next_level = True
            self.stop_background_music()
            
        if self.transitioning_to_next_level:
            if self.door_sound and not self.door_sound_played: self.door_sound.play(); self.door_sound_played = True
            self.fade_alpha += self.fade_speed
            if self.fade_alpha >= 255: self.fade_alpha = 255; self.running = False
            self.jugador.vel_x = 0; self.jugador.vel_y = 0; return
        
        super().update()
        
        distance_to_trigger = abs(self.jugador.rect.centerx - self.dialogue_trigger_x)
        if not self.entrance_dialogue_triggered and distance_to_trigger <= self.trigger_radius:
            self.dialogue_entrance.start(); self.entrance_dialogue_triggered = True
            
        if self.entered_mazmorra_permanently and self.jugador.rect.left < self.dialogue_trigger_x:
            if self.jugador.vel_x < 0: self.jugador.rect.left = self.dialogue_trigger_x

    def handle_input(self, evento):
        if self.is_paused:
            super().handle_input(evento); return
            
        if self.dialogue_entrance.active: self.dialogue_entrance.handle_input(evento)
        elif self.transitioning_to_next_level: pass 
        else: super().handle_input(evento)

    def draw(self):
        super().draw()
        if self.dialogue_entrance.active: self.dialogue_entrance.draw()
        if self.transitioning_to_next_level:
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); fade_surface.fill(BLACK)
            fade_surface.set_alpha(self.fade_alpha); self.screen.blit(fade_surface, (0, 0))