import pygame
from escenas import GameScene
from dialogos import DialogueBox # Se importa si vas a usar diálogos de victoria o iniciales
# from biblioteca import * # ELIMINADO: Ya importamos las constantes específicas
# de biblioteca abajo

# Importar constantes necesarias desde biblioteca.py
from biblioteca import (
    PLAYER_HEIGHT, MAP_MAZMORRA_JEFE1_PATH, BOSS_MUSIC_PATH, # Rutas de fondo y música
    FONT_SMALL, WHITE # Para el diálogo de victoria si se usa
)

# Importar las clases de entidad y interfaz necesarias
from entidad import Jefe1 # Importamos la clase específica del Jefe1
from interfaz import BossHealthBar # Para la barra de vida del jefe
from guardar import save_game # Para guardar la partida al derrotar al jefe

class Jefe1Scene(GameScene): # Nombre de la clase corregido para coincidir con main.py
    def __init__(self, screen):
        self.map_width = 1920 # O el ancho que desees para el área del jefe
        self.map_height = 1080 # O la altura que desees
        
        ground_y = 900 # Altura del suelo para esta escena de jefe
        
        # Plataformas: Generalmente, un área plana para la pelea de jefe.
        platforms = [
            pygame.Rect(0, ground_y, self.map_width, 50) # Suelo principal
        ]
        
        player_start = (200, ground_y - PLAYER_HEIGHT) # Posición de inicio del jugador
        
        # Inicializamos la escena base sin enemigos al principio,
        # ya que el jefe se añadirá manualmente para tener una referencia directa.
        super().__init__(
            screen, MAP_MAZMORRA_JEFE1_PATH, platforms,
            [], # Checkpoints (probablemente ninguno en una arena de jefe)
            [], # Interactables (probablemente ninguno)
            player_start, [], # Lista de enemigos inicial vacía para la superclase
            self.map_width, self.map_height,
            next_scene_name="mazmorrap2" # Siguiente escena después de derrotar al jefe
        )
        
        self.name = "mazmorrajefe1" # Nombre de la escena
        self.music_path = BOSS_MUSIC_PATH # Música específica del jefe
        
        # --- Instanciar al Jefe directamente y añadirlo a la lista de enemigos de GameScene ---
        # Asegúrate de que la posición 'y' sea adecuada para la base del jefe.
        # Usa el nombre "jefe1" para que cargue la información de ENEMY_INFO
        boss_start_x = self.map_width - 400 # Posición del jefe (ej. a la derecha)
        boss_start_y = ground_y+150  # El jefe debería estar en el suelo
        self.boss = Jefe1(boss_start_x, boss_start_y) # Instancia la clase Jefe1
        self.enemigos.append(self.boss) # Añade el jefe a la lista de enemigos de la escena
        
        # --- Crear la barra de vida del Jefe ---
        self.boss_name_display = "Jefe de la Mazmorra 1" # Puedes personalizar el nombre
        self.boss_health_bar = BossHealthBar(screen, self.boss, self.boss_name_display)

        # --- Lógica de Diálogo de Victoria y Fragmento de Llave (Adaptado) ---
        self.victory_dialogue = DialogueBox(screen, text_lines=[
            "¡Has derrotado al primer Guardián!",
            "Un fragmento de la llave ancestral es tuyo...",
            "La mazmorra aún esconde secretos más profundos."
        ], speaker_name="Narrador")
        self.victory_dialogue_triggered = False # Bandera para activar el diálogo solo una vez
        
        self.sound_fragment_collected = self._load_sound("sounds/fragmento.wav") # Asegúrate que este sonido exista.

    def respawn_player(self):
        """
        Maneja la reaparición del jugador después de morir en la escena del jefe.
        Restablece al jefe si es necesario.
        """
        super().respawn_player() # Llama a la lógica de respawn de GameScene
        
        # Lógica para revivir al jefe si el jugador muere
        if self.boss not in self.enemigos: # Si el jefe fue removido (porque murió), lo añadimos de nuevo
            self.enemigos.append(self.boss)
        self.boss.salud = self.boss.salud_maxima # Restaurar la vida del jefe al máximo
        self.boss.is_dying = False # Asegurarse que no esté en estado de muerte
        self.boss.is_dead = False # Asegurarse que no esté marcado como muerto
        self.boss.last_attack_time = pygame.time.get_ticks() # Resetear cooldown de ataque
        # También podrías resetear aquí los proyectiles del jefe si se mantienen en la escena:
        self.boss.proyectiles = []

    def update(self):
        """
        Actualiza la lógica de la escena del jefe.
        """
        # Si el diálogo de victoria está activo, solo actualiza el diálogo y detiene el juego
        if self.victory_dialogue.active:
            self.victory_dialogue.update()
            if self.victory_dialogue.finished:
                self.running = False # Termina la escena para pasar al siguiente nivel
            return # IMPORTANT: Salir del update para no procesar el juego normal durante el diálogo
            
        super().update() # Llama al método update de GameScene (actualiza jugador, enemigos, proyectiles)

        # Actualizar la barra de vida del jefe
        # Solo actualizamos si el jefe aún está en la lista de enemigos (es decir, no ha muerto aún)
        if self.boss in self.enemigos:
            self.boss_health_bar.update(self.boss)
        
        # Lógica de VICTORIA: Si no quedan enemigos (el jefe fue derrotado) y el diálogo no se ha activado
        if not self.enemigos and not self.victory_dialogue_triggered:
            # Revisa que el jefe esté realmente muerto, ya que `not self.enemigos` significa que fue removido
            # y esto solo ocurre si `self.boss.is_dead` es True
            
            # Recoge el primer fragmento de llave
            self.progreso_llave[0] = True # ¡Obtiene el PRIMER fragmento de llave!
            
            # Guardar partida automáticamente al derrotar al jefe
            game_data = {
                "last_scene": self.next_scene_name, # Guardar la escena a la que vas a transicionar
                "progreso_llave": self.progreso_llave,
                "personaje": self.jugador.personaje,
                "player_pos_x": self.jugador.rect.x, # Posición actual del jugador
                "player_pos_y": self.jugador.rect.y,
                "player_health": self.jugador.salud,
                "player_checkpoint_x": self.jugador.last_checkpoint[0], # Último checkpoint
                "player_checkpoint_y": self.jugador.last_checkpoint[1],
            }
            save_game(game_data)
            self.can_save = False # Para evitar guardar repetidamente en este mismo punto
            
            # Activar diálogo de victoria y sonido
            if self.sound_fragment_collected: self.sound_fragment_collected.play()
            self.victory_dialogue.start() # Inicia el diálogo
            self.victory_dialogue_triggered = True # Marca que el diálogo ya se activó
            self.stop_background_music() # Detener música de jefe

    def handle_input(self, evento):
        """
        Maneja los eventos de entrada del usuario en la escena del jefe.
        """
        if self.is_paused:
            super().handle_input(evento)
            return
        
        # Si el diálogo de victoria está activo, solo el diálogo maneja la entrada
        if self.victory_dialogue.active:
            self.victory_dialogue.handle_input(evento)
        else:
            super().handle_input(evento) # Si no hay diálogo, la escena normal maneja la entrada
    
    def draw(self):
        """
        Dibuja todos los elementos de la escena del jefe.
        """
        super().draw() # Dibuja fondo, jugador, jefe, proyectiles, etc.
        
        # Dibujar el diálogo de victoria si está activo
        if self.victory_dialogue.active:
            self.victory_dialogue.draw()
        
        # Dibujar la barra de vida del jefe si el jefe está vivo
        if self.boss in self.enemigos: # O self.boss.salud > 0, cualquiera es válido
            self.boss_health_bar.draw()