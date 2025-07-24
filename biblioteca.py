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
ENEMY_HEIGHT = 75  # Tamaño por defecto
BOSS_WIDTH = 500
BOSS_HEIGHT = 500
BOSS_HEALTH = 2000

# --- Projectile Properties --- #
ELEMENTAL_COOLDOWN = 500
SPECIAL_COOLDOWN = 2000

# --- Asset Paths --- #
MENU_BACKGROUND_PATH = "interfaz/fondo.png"
PLAYER_SPRITE_PATHS = {
    "Prota": "Characters/prota.png",
    "Lia": "Characters/lia.png",
    "Kael": "Characters/kael.png",
    "Aria": "Characters/aria.png"
}
# PLAYER_ANIMATION_DATA ELIMINADO - Los personajes no usarán animaciones.

SKILL_ICON_PATHS = {
    "rock": "Skills/rock.png",
    "sarten": "Skills/sarten.png",
    "fire": "Skills/fire_projectile.png",
    "ice": "Skills/ice_projectile.png",
    "mixed": "Skills/mixed_projectile.png",
    "root": "Skills/root.png",
    "earth_spike": "Skills/earth_spike.png",
    "lightning_bolt": "Skills/lightning_bolt.png",
    "storm": "Skills/storm.png",
    "boss_fireball": "Skills/boss_fireball.png",
    "boss_groundwave": "Skills/boss_groundwave.png",
    "lightning_strike": "Skills/lightning_strike.png",
    "skeleton_sword": "Skills/skeleton_sword.png",
    "hongo_proyectil": "Skills/hongo_proyectil.png"
}

## --- DICCIONARIO CENTRAL DE ENEMIGOS (en constants.py) ---
ENEMY_INFO = {
    "esqueleto": {
        "health": 60, "speed": 1.5, "contact_damage": 10, "scale": 2.0, "width": 60, "height": 90, "y_offset": 0, "hitbox_scale": (0.5, 0.9), "hitbox_offset": (0, 0),
        "sprite_path": "Enemies/esqueleto.png", # Asumiendo un sprite estático para el esqueleto
        "death_sound": "sounds/muerte_esqueleto.wav",
        "detection_radius": 300, # Ajustado
        "attack_range": 70, # Para ataques de contacto simulados o cortos
        "attack_cooldown": 1000,
        "attack_damage": 15
    },
    "goblins": {
        "health": 35, "speed": 2.2, "contact_damage": 5, "scale": 0.5, "width": 50, "height": 40, "y_offset": 0, "hitbox_scale": (0.8, 0.8), "hitbox_offset": (0, 0),
        "sprite_path": "Enemies/goblins.png", # Asegúrate de que esta ruta sea correcta
        "death_sound": "sounds/goblin_death.mp3", # Ajustar si tienes otro sonido
        "detection_radius": 250
    },
    "gole": {
        "health": 120, "speed": 0.8, "contact_damage": 20, "scale": 1.2, "width": 90, "height": 80, "y_offset": 0, "hitbox_scale": (0.9, 0.9), "hitbox_offset": (0, 0),
        "sprite_path": "Enemies/gole.png", # Asegúrate de que esta ruta sea correcta
        "death_sound": "sounds/gole_death.mp3", # Ajustar si tienes otro sonido
        "detection_radius": 350
    },
    "jefe1": {
        "health": BOSS_HEALTH, "speed": 0, "death_sound": "sounds/muerte_jefe1.wav", "scale": 1.0, "width": 250, "height": 250, "y_offset": 0, "hitbox_scale": (0.7, 0.9), "hitbox_offset": (0,0),
        "sprite_path": "Enemies/jefe1.png", # Asumiendo un sprite estático para el jefe
        "is_boss": True
    },
    "jefe2": {
        "health": BOSS_HEALTH * 1.5, "speed": 0, "death_sound": "sounds/muerte_jefe2.wav", "scale": 1.2, "width": 300, "height": 300, "y_offset": 0, "hitbox_scale": (0.7, 0.9), "hitbox_offset": (0,0),
        "sprite_path": "Enemies/jefe2.png", # Asumiendo un sprite estático para el jefe
        "is_boss": True
    },
    "jefe3": {
        "health": BOSS_HEALTH * 2, "speed": 0, "death_sound": "sounds/muerte_jefe3.wav", "scale": 1.5, "width": 350, "height": 350, "y_offset": 0, "hitbox_scale": (0.7, 0.9), "hitbox_offset": (0,0),
        "sprite_path": "Enemies/jefe3.png", # Asumiendo un sprite estático para el jefe
        "is_boss": True
    }
}


# --- Map and Sound Paths ---
# Actualizando los paths de mapas a la nueva estructura.
MAP_ALDEA_PATH = "fondos/aldea_scene.png"
MAP_MAZMORRA_PATH = "fondos/mazmorra_scene.png"
MAP_MAZMORRA_P1_PATH = "fondos/mazmorrap1.png"
MAP_MAZMORRA_JEFE1_PATH = "fondos/mazmorrajefe1.png"
MAP_MAZMORRA_P2_PATH = "fondos/mazmorrap2.png"
MAP_MAZMORRA_JEFE2_PATH = "fondos/mazmorrajefe2.png"
MAP_MAZMORRA_P3_PATH = "fondos/mazmorrap3.png"
MAP_MAZMORRA_JEFE3_PATH = "fondos/mazmorrajefe3.png"

MENU_MUSIC_PATH = "Soundtracks/menu.mp3"
BOSS_MUSIC_PATH = "Soundtracks/soundtrackboss1.mp3" # Considera si habrá una música diferente por cada jefe.

INITIAL_ZOOM = 0.85
DEATH_QUOTES = [
    ("La muerte de un hombre es una tragedia. La muerte de millones es estadística.", "Iósif Stalin"),
    ("El hombre que teme la muerte no hará nunca nada digno de un hombre vivo.", "Séneca"),
]