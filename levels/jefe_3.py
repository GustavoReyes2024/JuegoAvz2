import pygame
from escenas import GameScene
from dialogos import DialogueBox
# from biblioteca import * # ELIMINADO
# from aldea_scene import global_selected_character_g # No es directamente necesario aquí
from entidad import Jefe3 # <-- Importamos la clase específica del Jefe3
from guardar import save_game
from interfaz import BossHealthBar
# from interactables import * # ELIMINADO

# Importar constantes necesarias
from biblioteca import (
    PLAYER_HEIGHT, MAP_MAZMORRA_JEFE3_PATH, BOSS_MUSIC_PATH # Asegúrate de que estas constantes existan en constants.py
)

class Jefe3Scene(GameScene): # Nombre de la clase para jefe_3.py
    def __init__(self, screen):
        self.map_width = 2500 # Un poco más grande para el jefe final
        self.map_height = 1200 # Más altura para posible verticalidad en ataques
        
        ground_y = 1000 # Altura del suelo para esta arena final
        
        # Plataformas: Arena del jefe final, usualmente simple o con pocas plataformas.
        platforms = [
            pygame.Rect(0, ground_y, self.map_width, 50) # Suelo principal
            # Puedes añadir plataformas si el jefe usa verticalidad
            # pygame.Rect(self.map_width / 2 - 150, ground_y - 250, 300, 30)
        ]
        
        player_start = (200, ground_y - PLAYER_HEIGHT) # Posición de inicio del jugador
        
        # Inicializamos GameScene sin enemigos, el jefe se añadirá manualmente.
        super().__init__(
            screen, MAP_MAZMORRA_JEFE3_PATH, platforms,
            [], # Checkpoints (probablemente ninguno en una arena de jefe)
            [], # Interactables (probablemente ninguno)
            player_start, [], # Lista de enemigos inicial vacía para la superclase
            self.map_width, self.map_height,
            next_scene_name=None # <-- FIN DEL JUEGO / VOLVER AL MENÚ PRINCIPAL
        )
        
        self.name = "mazmorrajefe3" # Nombre de la escena
        self.music_path = BOSS_MUSIC_PATH # Música para la pelea de jefe final

        # --- Instanciar al Jefe3 (el jefe final) ---
        # Usa el nombre "jefe3" para que cargue la información de ENEMY_INFO
        boss_start_x = self.map_width / 2 # Centrar al jefe en el mapa
        boss_start_y = ground_y # El jefe aparece en el suelo
        self.boss = Jefe3(boss_start_x, boss_start_y) # Instancia la clase Jefe3
        self.enemigos.append(self.boss) # Añade el jefe a la lista de enemigos de la escena
        
        # --- Configurar la barra de vida del Jefe ---
        self.boss_name_display = "El Tirano de las Sombras" # Nombre impactante para el jefe final
        self.boss_health_bar = BossHealthBar(screen, self.boss, self.boss_name_display)
        
        # Diálogo de victoria final
        self.victory_dialogue = DialogueBox(screen, text_lines=[
            "¡Lo has logrado! El Tirano ha caído y la Mazmorra está libre.",
            "Los tres fragmentos de llave se unen, abriendo un nuevo camino...",
            "Tu leyenda ha comenzado. ¡Gracias, Guardián!"
        ], speaker_name="La Voz del Destino")
        self.victory_dialogue_triggered = False
        
        self.sound_fragment_collected = self._load_sound("sounds/fragmento.wav") # Sonido de fragmento

    def respawn_player(self):
        """
        Maneja la reaparición del jugador después de morir en la escena del jefe.
        Restablece al jefe si es necesario.
        """
        super().respawn_player() # Llama a la lógica de respawn de GameScene
        
        # Lógica para revivir al jefe si el jugador muere
        if self.boss not in self.enemigos:
            self.enemigos.append(self.boss)
        self.boss.salud = self.boss.salud_maxima
        self.boss.is_dying = False
        self.boss.is_dead = False
        self.boss.last_attack_time = pygame.time.get_ticks()

    def update(self):
        """
        Actualiza la lógica de la escena del jefe final.
        """
        # Si el diálogo de victoria está activo, solo actualiza el diálogo
        if self.victory_dialogue.active:
            self.victory_dialogue.update()
            if self.victory_dialogue.finished:
                self.running = False # Termina la escena para volver al menú principal
            return
            
        super().update() # Llama al método update de GameScene
        
        # Actualizar la barra de vida del jefe si está vivo
        if self.boss in self.enemigos:
            self.boss_health_bar.update(self.boss)
        
        # Condición de victoria: si no quedan enemigos (el jefe fue derrotado)
        if not self.enemigos and not self.victory_dialogue_triggered:
            self.progreso_llave[2] = True # ¡Obtiene el TERCER fragmento de llave!
            
            # Guardar partida automáticamente al derrotar al jefe final
            game_data = {
                "last_scene": self.next_scene_name, # Esto podría ser None, lo que indica final de juego
                "progreso_llave": self.progreso_llave,
                "personaje": self.jugador.personaje,
                "player_pos_x": self.player_start_pos[0],
                "player_pos_y": self.player_start_pos[1],
                "player_health": self.jugador.salud,
                "player_checkpoint_x": self.player_start_pos[0],
                "player_checkpoint_y": self.player_start_pos[1],
            }
            save_game(game_data)
            self.can_save = False
            
            # Activar diálogo de victoria final y sonido
            if self.sound_fragment_collected: self.sound_fragment_collected.play()
            self.victory_dialogue.start()
            self.victory_dialogue_triggered = True
            self.stop_background_music() # Detener música de jefe

    def handle_input(self, evento):
        """
        Maneja los eventos de entrada del usuario en la escena del jefe final.
        """
        if self.is_paused:
            super().handle_input(evento)
            return
        
        if self.victory_dialogue.active:
            self.victory_dialogue.handle_input(evento)
        else:
            super().handle_input(evento)
    
    def draw(self):
        """
        Dibuja todos los elementos de la escena del jefe final.
        """
        super().draw()
        
        if self.victory_dialogue.active:
            self.victory_dialogue.draw()
        
        if self.boss in self.enemigos:
            self.boss_health_bar.draw()