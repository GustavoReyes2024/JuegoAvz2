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
ENEMY_HEIGHT = 75
BOSS_WIDTH = 500
BOSS_HEIGHT = 500
BOSS_HEALTH = 2000

# --- Projectile Properties --- #
ELEMENTAL_COOLDOWN = 500
SPECIAL_COOLDOWN = 2000

# --- Asset Paths ---
PLAYER_SPRITE_PATHS = {
    "Prota": "Characters/prota.png",
    "Lia": "Characters/lia.png",
    "Kael": "Characters/kael.png",
    "Aria": "Characters/aria.png"
}

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

## --- DICCIONARIO CENTRAL DE ENEMIGOS ---
ENEMY_INFO = {
    "esqueleto": {
    "health": 60, "speed": 1.5, "contact_damage": 0.2,
    "scale": 0.8, "width": 120, "height": 180, "y_offset": 0,
    "hitbox_scale": (0.6, 0.7), # <-- CORREGIDO: Más pequeña y proporcionada al sprite.
    "hitbox_offset": (0, 10),  # <-- CORREGIDO: Desplazada un poco hacia abajo para cubrir el cuerpo.
    "sprite_path": "entidades/esqueleto.png", "death_sound": "sounds/muerte_esqueleto.wav",
    "detection_radius": 300, "attack_range": 70, "attack_cooldown": 1000, "attack_damage": 15
    },
    "goblins": {
        "health": 35, "speed": 2.2, "contact_damage": 0.2,
        "scale": 0.8, "width": 100, "height": 80, "y_offset": 0,
        "hitbox_scale": (1.3, 2.0), "hitbox_offset": (0, 20),
        "sprite_path": "entidades/goblins.png", "death_sound": "sounds/goblin_death.mp3",
        "detection_radius": 250
    },
    "gole": {
        "health": 120, "speed": 0.8, "contact_damage": 0.2,
        "scale": 1, "width": 200, "height": 200, "y_offset": 0,
        "hitbox_scale": (1.0, 1.0), "hitbox_offset": (0, 0),
        "sprite_path": "entidades/gole.png", "death_sound": "sounds/gole_death.mp3",
        "detection_radius": 350
    },
    "jefe1": {
        "health": 2000, "speed": 0, "death_sound": "sounds/muerte_jefe1.wav",
        "scale": 1.0, "width": 800, "height": 800, "y_offset": 0,
        # ...
        "hitbox_scale": (0.4, 0.7), "hitbox_offset": (0, 80),
        # ...
        "sprite_path": "entidades/jefe1.png", "is_boss": True,
        "is_flying": True
    },
    "jefe2": {
        "health": 3000.0, "speed": 0, "death_sound": "sounds/muerte_jefe2.wav",
        "scale": 0.55, "width": 800, "height": 800, "y_offset": 0,
        "hitbox_scale": (1.0, 1.0), "hitbox_offset": (0,0),
        "sprite_path": "entidades/jefe2.png", "is_boss": True,
        "is_flying": True
    },
    "jefe3": {
        "health": 4000, "speed": 0, "death_sound": "sounds/muerte_jefe3.wav",
        "scale": 0.6, "width": 800, "height": 800, "y_offset": 0,
        "hitbox_scale": (1.0, 1.0), "hitbox_offset": (0,0),
        "sprite_path": "entidades/jefe3.png", "is_boss": True,
        "is_flying": True
    }
}


# --- Map and Sound Paths ---
MENU_BACKGROUND_PATH = "interfaz/fondo.png"
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