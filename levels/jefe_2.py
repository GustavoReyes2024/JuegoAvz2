import pygame
from escenas import GameScene
from dialogos import DialogueBox
# from biblioteca import * # ELIMINADO: Asumimos que todas las constantes están en constants.py
# from aldea_scene import global_selected_character_g # No es directamente necesario aquí, se gestiona en GameScene
from entidad import Jefe2 # <-- Importamos la clase específica del Jefe2
from guardar import save_game
from interfaz import BossHealthBar
# from interactables import * # ELIMINADO: Si no hay interactables específicos aquí que lo justifiquen

# Importar constantes necesarias
from biblioteca import (
    PLAYER_HEIGHT, MAP_MAZMORRA_JEFE2_PATH, BOSS_MUSIC_PATH # Asegúrate de que estas constantes existan en constants.py
)

class Jefe2Scene(GameScene): # Nombre de la clase corregido para coincidir con main.py
    def __init__(self, screen):
        self.map_width = 1920 # Ancho típico para arena de jefe
        self.map_height = 1080 # Altura típica
        
        ground_y = 900 # Altura del suelo
        
        # Plataformas: Solo el suelo para la pelea
        dungeon_platforms = [ pygame.Rect(0, ground_y, self.map_width, 50) ]
        
        # Checkpoints e interactuables vacíos
        dungeon_checkpoints = []
        dungeon_interactables = []
        
        player_start = (150, ground_y - PLAYER_HEIGHT) # Posición inicial del jugador
        
        # Inicializamos GameScene sin enemigos, el jefe se añadirá manualmente.
        super().__init__(
            screen, MAP_MAZMORRA_JEFE2_PATH, dungeon_platforms,
            dungeon_checkpoints,
            dungeon_interactables,
            player_start,
            [], # Lista de enemigos inicial vacía para la superclase
            self.map_width,
            self.map_height,
            next_scene_name="mazmorrap3" # <-- Siguiente escena: mazmorrap3
        )
        
        self.name = "mazmorrajefe2" # Nombre de la escena
        self.music_path = BOSS_MUSIC_PATH # Música para la pelea de jefe

        # --- Instanciar al Jefe2 ---
        boss_start_x = self.map_width - 400 # Posición de spawn del jefe
        boss_start_y = ground_y # El jefe aparece en el suelo
        self.boss = Jefe2(boss_start_x, boss_start_y) # Instancia la clase Jefe2
        self.enemigos.append(self.boss) # Añade el jefe a la lista de enemigos de la escena
        
        # --- Configurar la barra de vida del Jefe ---
        self.boss_name_display = "Guardián Ancestral" # Nombre más épico para la barra
        self.boss_health_bar = BossHealthBar(screen, self.boss, self.boss_name_display)
        
        # Diálogo de victoria al derrotar al jefe
        self.victory_dialogue = DialogueBox(screen, text_lines=[
            "El Guardián ha caído. ¡Has obtenido el segundo fragmento de llave!",
            "Solo uno más... el corazón de la mazmorra espera."
        ], speaker_name="Voz Misteriosa")
        self.victory_dialogue_triggered = False # Para asegurar que el diálogo solo se active una vez
        
        self.sound_fragment_collected = self._load_sound("sounds/fragmento.wav") # Sonido de fragmento (asegúrate de que exista)

    def respawn_player(self):
        """
        Maneja la reaparición del jugador después de morir en la escena del jefe.
        Restablece al jefe si es necesario.
        """
        super().respawn_player() # Llama a la lógica de respawn de GameScene
        
        # Lógica para revivir al jefe si el jugador muere
        if self.boss not in self.enemigos: # Si el jefe fue removido (derrotado), lo añadimos de nuevo
            self.enemigos.append(self.boss)
        self.boss.salud = self.boss.salud_maxima # Restaurar la vida del jefe al máximo
        self.boss.is_dying = False # Asegurarse que no esté en estado de muerte
        self.boss.is_dead = False # Asegurarse que no esté marcado como muerto
        # Resetear cualquier estado de ataque o cooldown del jefe si es necesario
        self.boss.last_attack_time = pygame.time.get_ticks() # Resetear cooldown de ataque

    def update(self):
        """
        Actualiza la lógica de la escena del jefe.
        """
        # Si el diálogo de victoria está activo, solo actualiza el diálogo
        if self.victory_dialogue.active:
            self.victory_dialogue.update()
            if self.victory_dialogue.finished:
                self.running = False # Termina la escena para pasar al siguiente nivel
            return
            
        super().update() # Llama al método update de GameScene (actualiza jugador, enemigos, proyectiles)
        
        # Actualizar la barra de vida del jefe si está vivo
        if self.boss in self.enemigos:
            self.boss_health_bar.update(self.boss)
        
        # Condición de victoria: si no quedan enemigos (el jefe fue derrotado)
        if not self.enemigos and not self.victory_dialogue_triggered:
            self.progreso_llave[1] = True # ¡Obtiene el SEGUNDO fragmento de llave!
            
            # Guardar partida automáticamente al derrotar un jefe
            game_data = {
                "last_scene": self.next_scene_name, # Guardar la escena a la que vas a transicionar
                "progreso_llave": self.progreso_llave,
                "personaje": self.jugador.personaje,
                "player_pos_x": self.player_start_pos[0], # Posición de inicio del siguiente nivel (o un checkpoint)
                "player_pos_y": self.player_start_pos[1],
                "player_health": self.jugador.salud,
                "player_checkpoint_x": self.player_start_pos[0], # Guardar también el checkpoint
                "player_checkpoint_y": self.player_start_pos[1],
            }
            save_game(game_data)
            self.can_save = False # Para evitar guardar repetidamente en este mismo punto
            
            # Activar diálogo de victoria y sonido
            if self.sound_fragment_collected: self.sound_fragment_collected.play()
            self.victory_dialogue.start()
            self.victory_dialogue_triggered = True
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