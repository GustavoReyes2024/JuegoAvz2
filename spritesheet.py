import pygame

class SpriteSheet():
    def __init__(self, image):
        self.sheet = image

    def get_image(self, row, frame_index, width, height, scale, colour):
        """
        Extrae y escala un cuadro específico de la hoja de sprites.
        """
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        # Corta el cuadro exacto de la hoja de sprites
        image.blit(self.sheet, (0, 0), (frame_index * width, row * height, width, height))
        # Escala la imagen al tamaño deseado en el juego
        image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        # Elimina el color de fondo para hacerlo transparente
        image.set_colorkey(colour)
        return image