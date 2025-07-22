import pygame
from game_scene import GameScene
from constants import *
from dialogue import DialogueBox
from aldea_scene import global_selected_character_g
from enemy import Boss1
from game_state import save_game
from ui import BossHealthBar
from interactables import *

class MazmorraJefeScene(GameScene):
    def __init__(self, screen):
        self.map_width = 1920
        self.map_height = 1080
        
        dungeon_platforms = [ pygame.Rect(0, 900, self.map_width, 50) ]
        dungeon_checkpoints = [ pygame.Rect(150, 800, 100, 100) ]
        
        # Este nivel no tiene puzles, así que pasamos una lista vacía
        dungeon_interactables = []
        
        player_start = (150, 900 - PLAYER_HEIGHT)
        
        dungeon_enemies = []

        # --- LLAMADA AL CONSTRUCTOR CORREGIDA ---
        # Añadimos la lista de puzles vacía en la posición correcta
        super().__init__(
            screen, MAP_MAZMORRA_JEFE_PATH, dungeon_platforms,
            dungeon_checkpoints,
            dungeon_interactables, # <-- Argumento añadido
            player_start, 
            dungeon_enemies,
            self.map_width, 
            self.map_height, 
            next_scene_name="mazmorra_p4"
        )
import pygame
from game_scene import GameScene
from constants import *
from dialogue import DialogueBox
from aldea_scene import global_selected_character_g
from enemy import Boss1
from game_state import save_game
from ui import BossHealthBar
from interactables import *

class MazmorraJefeScene(GameScene):
    def __init__(self, screen):
        self.map_width = 1920
        self.map_height = 1080
        
        dungeon_platforms = [ pygame.Rect(0, 900, self.map_width, 50) ]
        dungeon_checkpoints = [ pygame.Rect(150, 800, 100, 100) ]
        dungeon_interactables = []
        player_start = (150, 900 - PLAYER_HEIGHT)
        dungeon_enemies = []

        super().__init__(
            screen, MAP_MAZMORRA_JEFE_PATH, dungeon_platforms,
            dungeon_checkpoints,
            dungeon_interactables,
            player_start, 
            dungeon_enemies,
            self.map_width, 
            self.map_height, 
            next_scene_name="mazmorra_p4"
        )
        
        # --- LÍNEA CORREGIDA PARA CREAR AL JEFE ---
        # Ahora se crea usando su nombre "boss1" desde ENEMY_INFO, como los demás enemigos.
        boss_start_x = self.map_width - 400
        boss_start_y = 900 
        self.boss = Boss1(boss_start_x, boss_start_y, "boss1")
        self.enemigos.append(self.boss)
        
        self.boss_name = "Entidad Oscura del Vacío"
        self.boss_health_bar = BossHealthBar(screen, self.boss, self.boss_name)
        
        self.victory_dialogue = DialogueBox(screen, text_lines=["¡Has conseguido el primer fragmento!", "Pero tu aventura apenas comienza..."], speaker_name="Eco Ancestral")
        self.victory_dialogue_triggered = False
        self.sound_fragment_collected = self._load_sound("sounds/fragmento.wav")
        
        self.music_path = BOSS_MUSIC_PATH
        self.name = "mazmorra_jefe"

    # El resto de tu clase (respawn_player, update, etc.) se mantiene igual
    # ...

    def respawn_player(self):
        # Llama a la lógica de la pantalla de muerte de la clase base
        super().respawn_player()
        
        # --- LÓGICA CLAVE: REVIVE AL JEFE ---
        # Si el jefe no está en la lista de enemigos (porque fue derrotado), lo vuelve a añadir
        if self.boss not in self.enemigos:
            self.enemigos.append(self.boss)
        
        # Le restaura la vida
        self.boss.salud = self.boss.salud_maxima

    def update(self):
        if self.victory_dialogue.active:
            self.victory_dialogue.update()
            if self.victory_dialogue.finished:
                self.running = False
            return
            
        super().update()
        
        if self.boss in self.enemigos:
            self.boss_health_bar.update(self.boss)
        
        if not self.enemigos and not self.victory_dialogue_triggered:
            self.progreso_llave[0] = True
            
            game_data = {
                "last_scene": self.next_scene_name,
                "progreso_llave": self.progreso_llave,
                "personaje": self.jugador.personaje
            }
            save_game(game_data)
            
            self.can_save = False
            
            if self.sound_fragment_collected: self.sound_fragment_collected.play()
            self.victory_dialogue.start()
            self.victory_dialogue_triggered = True
            self.stop_background_music()

    def handle_input(self, evento):
        if self.is_paused:
            super().handle_input(evento)
            return
        if self.victory_dialogue.active:
            self.victory_dialogue.handle_input(evento)
        else:
            super().handle_input(evento)
    
    def draw(self):
        super().draw()
        if self.victory_dialogue.active:
            self.victory_dialogue.draw()
        if self.boss in self.enemigos:
            self.boss_health_bar.draw()