# dialogue.py
import pygame
from constants import *

class DialogueBox:
    def __init__(self, screen, text_lines, speaker_name="", duration=None):
        self.screen = screen
        self.text_lines = text_lines
        self.speaker_name = speaker_name
        self.current_line_index = 0
        self.active = False
        self.finished = False

        self.font = FONT_SMALL # Considera usar FONT_DIALOGUE_TEXT
        self.speaker_font = FONT_MEDIUM # Considera usar FONT_DIALOGUE_SPEAKER

        self.width = SCREEN_WIDTH * 0.8
        self.height = SCREEN_HEIGHT * 0.2
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = SCREEN_HEIGHT - self.height - 20
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.padding = 20
        self.line_height = self.font.get_linesize() + 5

        self.advance_text = False
        self.clock = pygame.time.Clock()
        self.typing_speed = 30 # ms por caracter
        self.current_char_index = 0
        self.current_display_text = ""

        self.duration = duration
        self.start_time = 0

    def start(self):
        self.active = True
        self.finished = False
        self.current_line_index = 0
        self.current_char_index = 0
        self.current_display_text = ""
        self.start_time = pygame.time.get_ticks()

    def update(self):
        if not self.active or self.finished:
            return

        full_text = self.text_lines[self.current_line_index]
        if self.current_char_index < len(full_text):
            if pygame.time.get_ticks() - self.start_time > self.typing_speed:
                self.current_char_index += 1
                self.current_display_text = full_text[:self.current_char_index]
                self.start_time = pygame.time.get_ticks()
        else:
            self.current_display_text = full_text

        if self.duration and self.current_char_index >= len(full_text):
            if pygame.time.get_ticks() - self.start_time > self.duration:
                self.advance_line()


    def handle_input(self, event):
        if not self.active or self.finished:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.current_char_index < len(self.text_lines[self.current_line_index]):
                    self.current_char_index = len(self.text_lines[self.current_line_index])
                    self.current_display_text = self.text_lines[self.current_line_index]
                else:
                    self.advance_line()

    def advance_line(self):
        self.current_line_index += 1
        if self.current_line_index < len(self.text_lines):
            self.current_char_index = 0
            self.current_display_text = ""
            self.start_time = pygame.time.get_ticks()
        else:
            self.active = False
            self.finished = True

    def draw(self):
        if not self.active:
            return

        pygame.draw.rect(self.screen, DARK_GREY, self.rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, self.rect, 3, border_radius=10)

        if self.speaker_name:
            speaker_surf = self.speaker_font.render(self.speaker_name, True, MAGIC_BLUE)
            speaker_rect = speaker_surf.get_rect(bottomleft=(self.x + self.padding, self.y))
            self.screen.blit(speaker_surf, speaker_rect)

        text_surf = self.font.render(self.current_display_text, True, WHITE)
        self.screen.blit(text_surf, (self.x + self.padding, self.y + self.padding))

        if self.current_char_index >= len(self.text_lines[self.current_line_index]):
            advance_indicator = self.font.render("Presiona ENTER/ESPACIO para continuar...", True, WHITE)
            self.screen.blit(advance_indicator, (self.rect.right - advance_indicator.get_width() - self.padding, self.rect.bottom - advance_indicator.get_height() - 5))