import pygame
from constants import *

class InteractableObject:
    """La plantilla base para todos los objetos de puzle."""
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.is_active = False

    def interact(self, projectile):
        """Cada puzle específico llenará esta función con su propia lógica."""
        pass

    def update(self):
        """Para puzles que tengan animaciones."""
        pass

    def draw(self, surface, offset_x, offset_y, zoom):
        """Cada puzle se dibujará a sí mismo."""
        pass

# --- Puzle de Antorcha (reacciona al fuego) ---
class Torch(InteractableObject):
    def __init__(self, x, y):
        super().__init__(x, y, 32, 64) 
        
        # Carga sus imágenes únicas
        self.image_off = pygame.transform.scale(
            pygame.image.load("puzzles/antorcha_apagada.png").convert_alpha(), (self.rect.width, self.rect.height)
        )
        self.image_on_sheet = pygame.image.load("puzzles/antorcha_encendida.png").convert_alpha()
        
        # Lógica para la animación de la antorcha encendida
        self.animation_frames = []
        frame_height = self.image_on_sheet.get_height()
        # Asumimos que los cuadros de la antorcha son cuadrados
        frame_width = frame_height 
        num_frames = self.image_on_sheet.get_width() // frame_width
        for i in range(num_frames):
            frame = self.image_on_sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
            self.animation_frames.append(pygame.transform.scale(frame, (self.rect.width, self.rect.height)))
        
        self.current_frame_index = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_cooldown = 120

    def interact(self, projectile):
        if hasattr(projectile, 'tipo_elemental') and projectile.tipo_elemental == "fuego":
            if not self.is_active:
                # Aquí podrías reproducir un sonido de "fwoosh"
                pass
            self.is_active = True

    def update(self):
        # Si la antorcha está encendida, anima la llama
        if self.is_active:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_update > self.animation_cooldown:
                self.last_update = current_time
                self.current_frame_index = (self.current_frame_index + 1) % len(self.animation_frames)

    def draw(self, surface, offset_x, offset_y, zoom):
        pos_x = self.rect.x - offset_x
        pos_y = self.rect.y - offset_y
        
        if self.is_active:
            # Muestra el cuadro actual de la animación de la llama
            image_to_draw = self.animation_frames[self.current_frame_index]
        else:
            # Muestra la imagen de la antorcha apagada
            image_to_draw = self.image_off
            
        surface.blit(image_to_draw, (pos_x, pos_y))


# --- Puzle de Muro Rompible (reacciona a la tierra) ---
class BreakableWall(InteractableObject):
    def __init__(self, x, y):
        super().__init__(x, y, 64, 128)
        self.image = pygame.transform.scale(
            pygame.image.load("puzzles/muro_cayendo.png").convert_alpha(), (self.rect.width, self.rect.height)
        )
        self.is_active = False # 'is_active' aquí significa 'está roto'

    def interact(self, projectile):
        if hasattr(projectile, 'tipo_elemental') and projectile.tipo_elemental == "tierra":
            self.is_active = True
            # Aquí podríamos añadir un sonido de rocas rompiéndose

    def draw(self, surface, offset_x, offset_y, zoom):
        # Solo se dibuja si NO está roto
        if not self.is_active:
            surface.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))