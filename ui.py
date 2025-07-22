import pygame
from constants import *
from game_state import get_saved_games

class PauseMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = FONT_LARGE
        self.opciones = ["Continuar", "Guardar Partida", "Salir al Menú"]
        self.botones_rect = []
        y_inicial = SCREEN_HEIGHT // 2 - 80
        for i, opcion in enumerate(self.opciones):
            texto_surf = self.font.render(opcion, True, WHITE)
            texto_rect = texto_surf.get_rect(center=(SCREEN_WIDTH // 2, y_inicial + i * 80))
            self.botones_rect.append(texto_rect)

    def handle_event(self, event, can_save):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, rect in enumerate(self.botones_rect):
                if rect.collidepoint(event.pos):
                    if self.opciones[i] == "Guardar Partida" and not can_save:
                        return None
                    return self.opciones[i]
        return None

    def draw(self, can_save):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        mouse_pos = pygame.mouse.get_pos()
        for i, opcion in enumerate(self.opciones):
            rect = self.botones_rect[i]
            color = MAGIC_BLUE if rect.collidepoint(mouse_pos) else WHITE
            if opcion == "Guardar Partida" and not can_save:
                color = (100, 100, 100)
            
            texto_surf = self.font.render(opcion, True, color)
            self.screen.blit(texto_surf, rect)

class DeathScreenQuote:
    def __init__(self, screen, quote, author):
        self.screen = screen; self.font_quote = FONT_MEDIUM; self.font_author = FONT_SMALL
        self.quote_surf = self.font_quote.render(f'"{quote}"', True, (180, 180, 180))
        self.author_surf = self.font_author.render(f"- {author}", True, (150, 150, 150))
        self.quote_rect = self.quote_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        self.author_rect = self.author_surf.get_rect(center=(SCREEN_WIDTH / 2, self.quote_rect.bottom + 30))

    def draw(self):
        self.screen.fill(BLACK); self.screen.blit(self.quote_surf, self.quote_rect); self.screen.blit(self.author_surf, self.author_rect)

class LoadGameScreen:
    def __init__(self, screen):
        self.screen = screen; self.font_title = FONT_LARGE; self.font_item = FONT_MEDIUM
        self.saved_games = get_saved_games(); self.opciones = []
        y_pos = 200
        for game_file in self.saved_games:
            try:
                raw_datetime = game_file.replace("save_", "").replace(".json", "")
                date_part, time_part = raw_datetime.split('_')
                formatted_time = time_part.replace("-", ":")
                texto_legible = f"{date_part}   {formatted_time}"
            except ValueError:
                texto_legible = game_file
            
            texto_rect = self.font_item.render(texto_legible, True, WHITE).get_rect(center=(SCREEN_WIDTH / 2, y_pos))
            self.opciones.append({"file": game_file, "text": texto_legible, "rect": texto_rect})
            y_pos += 60

    def run(self):
        import sys
        while True:
            self.screen.fill(DARK_GREY); mouse_pos = pygame.mouse.get_pos()
            titulo_surf = self.font_title.render("Cargar Partida", True, WHITE)
            self.screen.blit(titulo_surf, titulo_surf.get_rect(center=(SCREEN_WIDTH / 2, 80)))
            for opcion in self.opciones:
                color = MAGIC_BLUE if opcion["rect"].collidepoint(mouse_pos) else WHITE
                texto_surf = self.font_item.render(opcion["text"], True, color)
                self.screen.blit(texto_surf, opcion["rect"])
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT: pygame.quit(); sys.exit()
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE: return None
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    for opcion in self.opciones:
                        if opcion["rect"].collidepoint(mouse_pos): return opcion["file"]
            pygame.display.flip()

# --- CLASE AÑADIDA PARA LA BARRA DE VIDA DEL JEFE ---
class BossHealthBar:
    def __init__(self, screen, boss, boss_name):
        self.screen = screen
        self.boss = boss
        self.boss_name = boss_name
        self.width = SCREEN_WIDTH * 0.6
        self.height = 25
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = 40
        self.font = FONT_SMALL

    def update(self, boss):
        self.boss = boss

    def draw(self):
        if self.boss.salud <= 0:
            return
            
        bg_rect = pygame.Rect(self.x - 4, self.y - 4, self.width + 8, self.height + 8)
        pygame.draw.rect(self.screen, (0,0,0,150), bg_rect, border_radius=5)
        
        health_percentage = max(0, self.boss.salud / self.boss.salud_maxima)
        health_width = int(self.width * health_percentage)
        
        pygame.draw.rect(self.screen, (180, 0, 0), (self.x, self.y, self.width, self.height))
        if health_width > 0:
            pygame.draw.rect(self.screen, GREEN_HEALTH, (self.x, self.y, health_width, self.height))
        
        pygame.draw.rect(self.screen, WHITE, (self.x, self.y, self.width, self.height), 2, border_radius=5)
        
        text_surface = self.font.render(self.boss_name, True, WHITE)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, self.y - 15))
        self.screen.blit(text_surface, text_rect)