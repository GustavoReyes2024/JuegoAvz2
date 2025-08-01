# Archivo: creditos.py

import pygame
import sys
from biblioteca import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_LARGE, FONT_MEDIUM, FONT_SMALL, WHITE, BLACK

class CreditosScene:
    def __init__(self, screen):
        self.screen = screen
        self.font_titulo = FONT_LARGE
        self.font_rol = FONT_MEDIUM
        self.font_nombre = FONT_SMALL
        self.reloj = pygame.time.Clock()
        self.running = True
        
        # aqui van los datos de los creditos
        self.creditos_data = [
            ("Director del Juego", "Cristian, Gustavo, Jose"),
            ("", ""),


            ("Diseño de Niveles", "Jose"),
            ("Escritor de la Historia", "Gustavo"),
            ("", ""),

            ("Programación Principal", "Cristian, Gustavo, Jose"),
            ("Inteligencia Artificial", "Gemini"),
            ("", ""),
            
            ("Arte de Personajes y Entornos", "Cristian, Gustavo, Jose"),
            ("Animación de Sprites", "Cristian, Gustavo, Jose"),
            ("", ""),

            ("Música y Efectos de Sonido", "Cristian"),
            ("", ""),

            ("Control de Calidad y Pruebas", ""),
            ("Tester 1", "Gustavo"),
            ("Tester 2", "Jose"),
            ("", ""),

            ("Agradecimientos Especiales", "Al Ingeniero Teruel"),
            ("A la comunidad de Pygame", ""),
            ("", ""),
            ("", ""),
            
            ("¡Gracias por Jugar!", ""),
        ]
        
        # Posición inicial del texto (empieza debajo de la pantalla)
        self.scroll_y = SCREEN_HEIGHT
        self.scroll_speed = 1.5 # Velocidad de desplazamiento 

    def run(self, *args, **kwargs):
        """
        El bucle principal para la escena de créditos.
        Acepta *args y **kwargs para ser compatible con el gestor de escenas.
        """
        while self.running:
            # --- Manejo de Eventos ---
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # Salir de los créditos si se presiona ESC o ENTER
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE or evento.key == pygame.K_RETURN:
                        self.running = False

            # --- Lógica de Actualización ---
            # Mover el texto hacia arriba
            self.scroll_y -= self.scroll_speed
            
            # Condición para terminar los créditos automáticamente
            # Cuando la última línea de texto ha desaparecido por arriba
            if self.scroll_y < -len(self.creditos_data) * 60:
                self.running = False

            # --- Dibujado en Pantalla ---
            self.screen.fill(BLACK) # Fondo negro

            # Renderizar y posicionar cada línea de los créditos
            current_y = self.scroll_y
            for rol, nombre in self.creditos_data:
                # Renderizar el rol
                rol_surf = self.font_rol.render(rol, True, WHITE)
                rol_rect = rol_surf.get_rect(center=(SCREEN_WIDTH / 2, current_y))
                self.screen.blit(rol_surf, rol_rect)
                
                # Renderizar el nombre debajo del rol
                nombre_surf = self.font_nombre.render(nombre, True, (200, 200, 200)) # Un gris claro
                nombre_rect = nombre_surf.get_rect(center=(SCREEN_WIDTH / 2, current_y + 30))
                self.screen.blit(nombre_surf, nombre_rect)
                
                current_y += 80 # Espacio para la siguiente línea de créditos

            # Mensaje para saltar los créditos
            skip_surf = FONT_SMALL.render("Presiona ESC o ENTER para omitir", True, WHITE)
            skip_rect = skip_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 30))
            self.screen.blit(skip_surf, skip_rect)

            pygame.display.flip()
            self.reloj.tick(60)
            
        # Devuelve None para indicar que se debe volver al menú principal
        return None, None