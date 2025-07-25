# biblioteca.py (Este archivo es tu archivo de constantes principal)

import pygame

pygame.init()
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h

# --- Colors --- #
WHITE = (255, 255, 255)
DARK_GREY = (50, 50, 50)
MAGIC_BLUE = (80, 160, 255)
RED_HEALTH = (255, 0, 0)
GREEN_HEALTH = (0, 255, 0)
BLACK = (0, 0, 0)

# --- Fonts --- #
FONT_LARGE = pygame.font.SysFont("arial", 38)
FONT_MEDIUM = pygame.font.SysFont("arial", 30)
FONT_SMALL = pygame.font.SysFont("arial", 24)

# --- Game Physics --- #
PLAYER_SPEED = 5
ENEMY_SPEED = 2
DETECTION_RADIUS = 350
GRAVITY = 0.6
JUMP_STRENGTH = -9

# --- Player and Enemy Sizes --- #
PLAYER_WIDTH = 100
PLAYER_HEIGHT = 100
ENEMY_WIDTH = 100
ENEMY_HEIGHT = 75  # Default size
BOSS_WIDTH = 500
BOSS_HEIGHT = 500
BOSS_HEALTH = 2000

# --- Projectile Properties --- #
ELEMENTAL_COOLDOWN = 500
SPECIAL_COOLDOWN = 2000

# --- Asset Paths ---
# Rutas de personajes (carpeta "Characters")
PLAYER_SPRITE_PATHS = {
    "Prota": "Characters/prota.png",
    "Lia": "Characters/lia.png",
    "Kael": "Characters/kael.png",
    "Aria": "Characters/aria.png"
}

# Rutas de iconos de habilidades (carpeta "poderes")
SKILL_ICON_PATHS = {
    "rock": "poderes/rock.png",
    "sarten": "poderes/sarten.png",
    "fire": "poderes/fire_projectile.png",
    "ice": "poderes/ice_projectile.png",
    "mixed": "poderes/mixed_projectile.png",
    "root": "poderes/root.png",
    "earth_spike": "poderes/earth_spike.png",
    "lightning_bolt": "poderes/lightning_bolt.png",
    "storm": "poderes/storm.png",
    "boss_fireball": "poderes/boss_fireball.png",
    "boss_groundwave": "poderes/boss_groundwave.png",
    "lightning_strike": "poderes/lightning_strike.png",
    "skeleton_sword": "poderes/skeleton_sword.png",
    "hongo_proyectil": "poderes/hongo_proyectil.png"
}

## --- DICCIONARIO CENTRAL DE ENEMIGOS (sprites en la carpeta "entidades") ---
ENEMY_INFO = {
    "esqueleto": {
        "health": 60, "speed": 1.5, "contact_damage": 0.2,
        "scale": 0.25, # ¡MUCHO MÁS PEQUEÑO! Si el lobo era 0.3, este debería ser similar o menos.
        "width": 120, "height": 180, # Asumiendo dimensiones REALES de tu archivo esqueleto.png (ej. 120x180 pixels)
        "y_offset": 0, # Ajuste fino si es necesario
        "hitbox_scale": (0.6, 0.9), "hitbox_offset": (0, 0),
        "sprite_path": "entidades/esqueleto.png",
        "death_sound": "sounds/muerte_esqueleto.wav",
        "detection_radius": 300,
        "attack_range": 70,
        "attack_cooldown": 1000,
        "attack_damage": 15
    },
    "goblins": {
        "health": 35, "speed": 2.2, "contact_damage": 0.2,
        "scale": 0.2, # Un poco más pequeño que el esqueleto, como en la imagen
        "width": 100, "height": 80, # Asumiendo dimensiones REALES de tu goblins.png
        "y_offset": 0,
        "hitbox_scale": (0.8, 0.9), "hitbox_offset": (0, 0),
        "sprite_path": "entidades/goblins.png",
        "death_sound": "sounds/goblin_death.mp3",
        "detection_radius": 250
    },
    "gole": {
        "health": 120, "speed": 0.8, "contact_damage": 0.2,
        "scale": 0.35, # Puede ser un poco más grande que el esqueleto/goblin
        "width": 200, "height": 200, # Asumiendo dimensiones REALES de tu gole.png
        "y_offset": 0,
        "hitbox_scale": (0.9, 0.9), "hitbox_offset": (0, 0),
        "sprite_path": "entidades/gole.png",
        "death_sound": "sounds/gole_death.mp3",
        "detection_radius": 350
    },
    # PARA LOS JEFES, TAMBIÉN NECESITAMOS REDUCIR LA ESCALA SIGNIFICATIVAMENTE
    "jefe1": {
        "health": BOSS_HEALTH, "speed": 0, "death_sound": "sounds/muerte_jefe1.wav",
        "scale": 0.2, # Reducido a la quinta parte del tamaño original si es muy grande
        "width": 800, "height": 800, # Dimensiones REALES de tu jefe1.png (ej. 800x800 pixels)
        "y_offset": 0,
        "hitbox_scale": (0.7, 0.9), "hitbox_offset": (0,0),
        "sprite_path": "entidades/jefe1.png",
        "is_boss": True
    },
    "jefe2": {
        "health": BOSS_HEALTH * 1.5, "speed": 0, "death_sound": "sounds/muerte_jefe2.wav",
        "scale": 0.22, # Ligeramente más grande que jefe1, si aplica
        "width": 800, "height": 800, # Dimensiones REALES de tu jefe2.png
        "y_offset": 0,
        "hitbox_scale": (0.7, 0.9), "hitbox_offset": (0,0),
        "sprite_path": "entidades/jefe2.png",
        "is_boss": True
    },
    "jefe3": {
        "health": BOSS_HEALTH * 2, "speed": 0, "death_sound": "sounds/muerte_jefe3.wav",
        "scale": 0.25, # El jefe final puede ser un poco más grande
        "width": 800, "height": 800, # Dimensiones REALES de tu jefe3.png
        "y_offset": 0,
        "hitbox_scale": (0.7, 0.9), "hitbox_offset": (0,0),
        "sprite_path": "entidades/jefe3.png",
        "is_boss": True
    }
}


# --- Map and Sound Paths (fondos en la carpeta "backgrounds") ---
MENU_BACKGROUND_PATH = "interfaz/fondo.png" # Asumiendo que esta es la ruta correcta para el fondo del menú

MAP_ALDEA_PATH = "backgrounds/aldea_scene.png"
MAP_MAZMORRA_PATH = "backgrounds/mazmorra.png"
MAP_MAZMORRA_P1_PATH = "backgrounds/p1_mazmorra.png"
MAP_MAZMORRA_JEFE1_PATH = "backgrounds/jefe1.png"
MAP_MAZMORRA_P2_PATH = "backgrounds/p2_mazmorra.png"
MAP_MAZMORRA_JEFE2_PATH = "backgrounds/jefe2.png"
MAP_MAZMORRA_P3_PATH = "backgrounds/p3_mazmorra.png"
MAP_MAZMORRA_JEFE3_PATH = "backgrounds/jefe3.png"

MENU_MUSIC_PATH = "Soundtracks/menu.mp3"
BOSS_MUSIC_PATH = "Soundtracks/soundtrackboss.mp3"

INITIAL_ZOOM = 0.85
DEATH_QUOTES = [
    ("La muerte de un hombre es una tragedia. La muerte de millones es estadística.", "Iósif Stalin"),
    ("El hombre que teme la muerte no hará nunca nada digno de un hombre vivo.", "Séneca"),
]