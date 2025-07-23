import pygame
import sys
from game_scene import GameScene
from constants import *
from dialogue import DialogueBox
from ui import PauseMenu
from interactables import *

global_selected_character_g = "Prota"

class CharacterSelectSceneInGame:
    # ... (Esta clase no cambia, puedes mantener la que tienes)
    def __init__(self, screen, characters):
        self.screen = screen; self.running = True; self.selected_character = None
        self.characters = characters; self.reloj = pygame.time.Clock()
        self.title_text = FONT_LARGE.render("Elige tu Guardián", True, WHITE)
        self.title_rect = self.title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.character_data = []
        character_names = self.characters
        total_cards_width = len(character_names) * 96; total_spacing_between_cards = (len(character_names) - 1) * 50
        total_area_width = total_cards_width + total_spacing_between_cards
        start_x_initial = (SCREEN_WIDTH - total_area_width) // 2
        for i, name in enumerate(character_names):
            try:
                img = pygame.transform.scale(pygame.image.load(PLAYER_SPRITE_PATHS.get(name, PLAYER_SPRITE_PATHS["Prota"])).convert_alpha(), (96, 144))
                card_x = start_x_initial + i * (96 + 50)
                rect = img.get_rect(midtop=(card_x + 96//2, SCREEN_HEIGHT // 2 - 72))
                text_surf = FONT_MEDIUM.render(name, True, WHITE)
                text_rect = text_surf.get_rect(center=(rect.centerx, rect.bottom + 20))
                self.character_data.append({"name": name, "image": img, "rect": rect, "text_surf": text_surf, "text_rect": text_rect})
            except pygame.error: print(f"Error cargando imagen para selector: {name}")
        self.selection_made = False; self.selected_rect = None

    def handle_input(self, evento):
        if evento.type == pygame.QUIT: self.running = False; pygame.quit(); sys.exit()
        if not self.selection_made and evento.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = evento.pos
            for data in self.character_data:
                if data["rect"].collidepoint(mouse_pos):
                    self.selected_character = data["name"]; self.selection_made = True; self.selected_rect = data["rect"].copy()
        if self.selection_made and evento.type == pygame.KEYDOWN and (evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE):
            self.running = False

    def draw(self):
        self.screen.fill(DARK_GREY); self.screen.blit(self.title_text, self.title_rect)
        for data in self.character_data:
            self.screen.blit(data["image"], data["rect"].topleft); self.screen.blit(data["text_surf"], data["text_rect"].topleft)
            if self.selected_rect and self.selected_rect.colliderect(data["rect"]): pygame.draw.rect(self.screen, MAGIC_BLUE, data["rect"], 5)
        if self.selection_made:
            continue_text = FONT_SMALL.render("Presiona ENTER para continuar...", True, WHITE)
            continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            self.screen.blit(continue_text, continue_rect)

    def run(self):
        self.running = True; self.selected_character = None; self.selection_made = False; self.selected_rect = None
        while self.running:
            for evento in pygame.event.get(): self.handle_input(evento)
            self.draw(); pygame.display.flip(); self.reloj.tick(60)
        return self.selected_character

class AldeaScene(GameScene):
    def __init__(self, screen):
        self.map_width = 2500; self.map_height = 830
        ground_y_aldea = 640
        aldea_platforms = [ pygame.Rect(0, ground_y_aldea, self.map_width, 50) ]
        aldea_checkpoints = []
        aldea_interactables = [] # La aldea no tiene puzles
        player_start = (100, ground_y_aldea - PLAYER_HEIGHT + 50)
        aldea_enemies = []
        
        super().__init__(
            screen, MAP_ALDEA_PATH, aldea_platforms, 
            aldea_checkpoints,
            aldea_interactables,
            player_start, aldea_enemies, 
            self.map_width, self.map_height, next_scene_name="mazmorra"
        )
        
        self.name = "aldea"
        self.dialogue_mission = DialogueBox(screen, text_lines=["..."], speaker_name="Anciano Sabio")
        self.dialogue_pre_selection = DialogueBox(screen, text_lines=["..."], speaker_name="Anciano Sabio")
        self.dialogue_after_selection = DialogueBox(screen, text_lines=["..."], speaker_name="Anciano Sabio")
        self.elder_trigger_x = 1200; self.trigger_radius = 100
        self.dialogue_phase = 0; self.mission_dialogue_done = False; self.pre_selection_dialogue_done = False; self.selection_processed = False

    def update(self):
        global global_selected_character_g
        if self.jugador.salud <= 0: self.respawn_player(); return

        if self.dialogue_phase == 1: 
            self.dialogue_mission.update(); self.jugador.vel_x = 0; self.jugador.vel_y = 0
            if self.dialogue_mission.finished: self.mission_dialogue_done = True; self.dialogue_phase = 2; self.dialogue_pre_selection.start()
        elif self.dialogue_phase == 2:
            self.dialogue_pre_selection.update(); self.jugador.vel_x = 0; self.jugador.vel_y = 0
            if self.dialogue_pre_selection.finished: self.pre_selection_dialogue_done = True; self.dialogue_phase = 3
        elif self.dialogue_phase == 3: 
            if not self.selection_processed:
                character_select = CharacterSelectSceneInGame(self.screen, ["Lia", "Kael", "Aria"])
                chosen_char = character_select.run()
                if chosen_char:
                    global_selected_character_g = chosen_char
                    self.jugador.cambiar_personaje(global_selected_character_g)
                self.selection_processed = True; self.dialogue_phase = 4; self.dialogue_after_selection.start() 
            else: self.dialogue_phase = 4 
        elif self.dialogue_phase == 4: 
            self.dialogue_after_selection.update(); self.jugador.vel_x = 0; self.jugador.vel_y = 0
            if self.dialogue_after_selection.finished: self.dialogue_phase = 5 
        else:
            super().update()
            distance_to_elder = abs(self.jugador.rect.centerx - self.elder_trigger_x)
            if self.dialogue_phase == 0 and distance_to_elder <= self.trigger_radius:
                self.dialogue_phase = 1; self.dialogue_mission.start()
        
    def handle_input(self, evento):
        if self.is_paused:
            super().handle_input(evento); return
        if self.dialogue_phase == 1: self.dialogue_mission.handle_input(evento)
        elif self.dialogue_phase == 2: self.dialogue_pre_selection.handle_input(evento)
        elif self.dialogue_phase == 3: pass
        elif self.dialogue_phase == 4: self.dialogue_after_selection.handle_input(evento)
        else: super().handle_input(evento)

    def draw(self):
        super().draw()
        if self.dialogue_phase == 1: self.dialogue_mission.draw()
        elif self.dialogue_phase == 2: self.dialogue_pre_selection.draw()
        elif self.dialogue_phase == 4: self.dialogue_after_selection.draw()

    def run(self, selected_character_for_this_scene=None):
        super().run(selected_character_for_this_scene)
        return self.next_scene_name, global_selected_character_g