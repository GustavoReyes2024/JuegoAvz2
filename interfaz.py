import pygame
import sys # sys es necesario para sys.exit() en LoadGameScreen.run()
from guardar import get_saved_games

# Importar constantes necesarias desde constants.py
from biblioteca import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    FONT_LARGE, FONT_MEDIUM, FONT_SMALL,
    WHITE, BLACK, DARK_GREY, MAGIC_BLUE, RED_HEALTH, GREEN_HEALTH
)

# biblioteca ELIMINADA si su contenido se ha movido a constants

class PauseMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = FONT_LARGE
        self.opciones = ["Continuar", "Guardar Partida", "Salir al Menú"]
        self.botones_rect = [] # Almacena los rectángulos de cada opción
        
        # Calcular posiciones de los botones
        y_initial = SCREEN_HEIGHT // 2 - 80
        for i, opcion in enumerate(self.opciones):
            # Renderizar el texto para obtener su tamaño y crear el rectángulo
            text_surf = self.font.render(opcion, True, WHITE) # Renderiza una vez para el tamaño
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y_initial + i * 80))
            self.botones_rect.append(text_rect)

    def handle_event(self, event, can_save):
        """
        Maneja los eventos del menú de pausa.
        Devuelve el nombre de la acción seleccionada o None.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, rect in enumerate(self.botones_rect):
                if rect.collidepoint(event.pos):
                    # Deshabilitar la opción "Guardar Partida" si no se puede guardar
                    if self.opciones[i] == "Guardar Partida" and not can_save:
                        return None # No se selecciona nada si no se puede guardar
                    return self.opciones[i] # Devuelve la acción seleccionada
        return None

    def draw(self, can_save):
        """
        Dibuja el menú de pausa en la pantalla.
        """
        # Capa semi-transparente para oscurecer el fondo del juego
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) # Negro con 150 de alfa (transparencia)
        self.screen.blit(overlay, (0, 0))
        
        mouse_pos = pygame.mouse.get_pos() # Posición del ratón para el hover
        
        for i, opcion in enumerate(self.opciones):
            rect = self.botones_rect[i]
            color = WHITE # Color por defecto
            
            # Cambiar color al pasar el ratón por encima
            if rect.collidepoint(mouse_pos):
                color = MAGIC_BLUE
            
            # Deshabilitar visualmente la opción "Guardar Partida"
            if opcion == "Guardar Partida" and not can_save:
                color = (100, 100, 100) # Gris para indicar que está deshabilitado
            
            # Renderizar y dibujar el texto de la opción
            text_surf = self.font.render(opcion, True, color)
            self.screen.blit(text_surf, rect)

class DeathScreenQuote:
    def __init__(self, screen, quote, author):
        self.screen = screen
        self.font_quote = FONT_MEDIUM
        self.font_author = FONT_SMALL
        
        # Renderizar los textos de la cita y el autor
        self.quote_surf = self.font_quote.render(f'"{quote}"', True, (180, 180, 180)) # Gris claro
        self.author_surf = self.font_author.render(f"- {author}", True, (150, 150, 150)) # Gris medio
        
        # Posicionar los textos en el centro de la pantalla
        self.quote_rect = self.quote_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        self.author_rect = self.author_surf.get_rect(center=(SCREEN_WIDTH / 2, self.quote_rect.bottom + 30))

    def draw(self):
        """
        Dibuja la pantalla de muerte con la cita.
        """
        self.screen.fill(BLACK) # Fondo negro
        self.screen.blit(self.quote_surf, self.quote_rect)
        self.screen.blit(self.author_surf, self.author_rect)

class LoadGameScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = FONT_LARGE
        self.font_item = FONT_MEDIUM
        
        self.saved_games = get_saved_games() # Obtiene la lista de archivos guardados
        self.opciones = [] # Lista para almacenar los datos de cada opción de carga
        
        y_pos = 200 # Posición Y inicial para los elementos de la lista
        
        # Prepara las opciones de visualización de partidas guardadas
        if not self.saved_games:
            # Si no hay partidas guardadas, mostrar un mensaje
            no_saves_text = "No hay partidas guardadas."
            text_rect = self.font_item.render(no_saves_text, True, WHITE).get_rect(center=(SCREEN_WIDTH / 2, y_pos))
            self.opciones.append({"file": None, "text": no_saves_text, "rect": text_rect})
        else:
            for game_file in self.saved_games:
                try:
                    # Intenta formatear la marca de tiempo del nombre del archivo
                    raw_datetime = game_file.replace("save_", "").replace(".json", "")
                    # Asumiendo formato "YYYY-MM-DD_HH-MM-SS"
                    date_part, time_part = raw_datetime.split('_')
                    # Convertir el formato de hora de "HH-MM-SS" a "HH:MM:SS" para mejor legibilidad
                    formatted_time = time_part.replace("-", ":")
                    texto_legible = f"{date_part}  {formatted_time}"
                except ValueError:
                    # En caso de error de formato, usa el nombre de archivo sin modificar
                    texto_legible = game_file
                
                text_rect = self.font_item.render(texto_legible, True, WHITE).get_rect(center=(SCREEN_WIDTH / 2, y_pos))
                self.opciones.append({"file": game_file, "text": texto_legible, "rect": text_rect})
                y_pos += 60 # Espacio entre opciones

    def run(self):
        """
        Bucle principal para la pantalla de carga de partida.
        Devuelve el nombre del archivo de la partida seleccionada o None si se cancela.
        """
        while True:
            self.screen.fill(DARK_GREY) # Fondo de la pantalla de carga
            mouse_pos = pygame.mouse.get_pos()
            
            # Dibujar título
            titulo_surf = self.font_title.render("Cargar Partida", True, WHITE)
            self.screen.blit(titulo_surf, titulo_surf.get_rect(center=(SCREEN_WIDTH / 2, 80)))
            
            # Dibujar cada opción de partida guardada
            for opcion in self.opciones:
                color = MAGIC_BLUE if opcion["rect"].collidepoint(mouse_pos) else WHITE
                # Si no hay partidas guardadas, el texto será gris y no seleccionable
                if opcion["file"] is None: 
                    color = (150, 150, 150) # Un gris más claro para "no hay partidas"
                
                text_surf = self.font_item.render(opcion["text"], True, color)
                self.screen.blit(text_surf, opcion["rect"])
            
            # Manejo de eventos
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    return None # Regresar al menú anterior
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    for opcion in self.opciones:
                        if opcion["rect"].collidepoint(mouse_pos) and opcion["file"] is not None:
                            return opcion["file"] # Retorna el nombre del archivo seleccionado
            
            pygame.display.flip()

class BossHealthBar:
    def __init__(self, screen, boss, boss_name):
        self.screen = screen
        self.boss = boss # Referencia al objeto jefe
        self.boss_name = boss_name # Nombre del jefe a mostrar
        self.width = SCREEN_WIDTH * 0.6 # Ancho de la barra (60% de la pantalla)
        self.height = 25 # Altura de la barra
        self.x = (SCREEN_WIDTH - self.width) // 2 # Centrar horizontalmente
        self.y = 40 # Posición Y
        self.font = FONT_SMALL # Fuente para el nombre del jefe

    def update(self, boss):
        """
        Actualiza la referencia al objeto jefe si es necesario (ej. para múltiples jefes).
        """
        self.boss = boss

    def draw(self):
        """
        Dibuja la barra de vida del jefe.
        """
        if self.boss.salud <= 0:
            return # No dibujar la barra si el jefe ya está muerto
            
        # Dibujar fondo negro semi-transparente para la barra
        bg_rect = pygame.Rect(self.x - 4, self.y - 4, self.width + 8, self.height + 8)
        # Usamos (0,0,0,150) para un fondo negro semitransparente, requiere SRCALPHA en la superficie de la pantalla
        # Si la superficie de la pantalla no es SRCALPHA, el 150 se ignora y será negro opaco.
        # Para que funcione la transparencia, asegúrate de que el modo de pantalla se configure con pygame.SRCALPHA.
        pygame.draw.rect(self.screen, (0,0,0,150), bg_rect, border_radius=5)
        
        # Calcular porcentaje de vida
        health_percentage = max(0, self.boss.salud / self.boss.salud_maxima)
        health_width = int(self.width * health_percentage)
        
        # Dibujar barra de vida (rojo de fondo, verde para la vida actual)
        pygame.draw.rect(self.screen, RED_HEALTH, (self.x, self.y, self.width, self.height)) # Fondo rojo
        if health_width > 0:
            pygame.draw.rect(self.screen, GREEN_HEALTH, (self.x, self.y, health_width, self.height)) # Vida actual en verde
        
        # Borde blanco de la barra
        pygame.draw.rect(self.screen, WHITE, (self.x, self.y, self.width, self.height), 2, border_radius=5)
        
        # Dibujar nombre del jefe encima de la barra
        text_surface = self.font.render(self.boss_name, True, WHITE)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, self.y - 15))
        self.screen.blit(text_surface, text_rect)