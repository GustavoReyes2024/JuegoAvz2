import pygame

pygame.init()
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h

# --- Colors --- #
WHITE = (255, 255, 255); DARK_GREY = (50, 50, 50); MAGIC_BLUE = (80, 160, 255)
RED_HEALTH = (255, 0, 0); GREEN_HEALTH = (0, 255, 0); BLACK = (0, 0, 0)

# --- Fonts --- #
FONT_LARGE = pygame.font.SysFont("arial", 38); FONT_MEDIUM = pygame.font.SysFont("arial", 30)
FONT_SMALL = pygame.font.SysFont("arial", 24)

# --- Game Physics --- #
PLAYER_SPEED = 5; ENEMY_SPEED = 2; DETECTION_RADIUS = 350
GRAVITY = 0.6; JUMP_STRENGTH = -9

# --- Player and Enemy Sizes --- #
PLAYER_WIDTH = 100; PLAYER_HEIGHT = 100
ENEMY_WIDTH = 100; ENEMY_HEIGHT = 75 # Tamaño por defecto
BOSS_WIDTH = 500; BOSS_HEIGHT = 500
BOSS_HEALTH = 2000

# --- Projectile Properties --- #
ELEMENTAL_COOLDOWN = 500; SPECIAL_COOLDOWN = 2000

# --- Asset Paths --- #
MENU_BACKGROUND_PATH = "interfaz/fondo.png"
PLAYER_SPRITE_PATHS = {
    "Prota": "Characters/prota.png", "Lia": "Characters/lia.png",
    "Kael": "Characters/kael.png", "Aria": "Characters/aria.png"
}
PLAYER_ANIMATION_DATA = {
    "Prota": {"idle": {"frames": 4}, "run": {"frames": 4}},
    "Lia":   {"idle": {"frames": 3}, "run": {"frames": 3}},
    "Kael":  {"idle": {"frames": 4}, "run": {"frames": 3}},
    "Aria":  {"idle": {"frames": 3}, "run": {"frames": 3}}
}

SKILL_ICON_PATHS = {
    "rock": "Skills/rock.png", "sarten": "Skills/sarten.png",
    "fire": "Skills/fire_projectile.png", "ice": "Skills/ice_projectile.png",
    "mixed": "Skills/mixed_projectile.png", "root": "Skills/root.png",
    "earth_spike": "Skills/earth_spike.png", "lightning_bolt": "Skills/lightning_bolt.png",
    "storm": "Skills/storm.png", "boss_fireball": "Skills/boss_fireball.png",
    "boss_groundwave": "Skills/boss_groundwave.png", "lightning_strike": "Skills/lightning_strike.png",
    "skeleton_sword": "Skills/skeleton_sword.png",
    "hongo_proyectil": "Skills/hongo_proyectil.png"
}
# --- DICCIONARIO CENTRAL DE ENEMIGOS (en constants.py) ---
ENEMY_INFO = {
    # --- Enemigos Básicos (sin animación de ataque, daño por contacto) ---
    "lobo":       {"health": 30, "speed": 2.5, "contact_damage": 5, "scale": 0.2, "y_offset": 12, "sprite_path": "Enemies/lobos.png", "death_sound": "sounds/lobodeath.mp3"}, # <-- Ajuste final de altura
    "depredator": {"health": 50, "speed": 2,   "contact_damage": 8, "scale": 0.5, "y_offset": 5, "sprite_path": "Enemies/depredator.png", "death_sound": "sounds/lobodeath.mp3"},
    "fire":       {"health": 40, "speed": 1.8, "contact_damage": 10, "scale": 5.5, "y_offset": 5, "sprite_path": "Enemies/fire.png", "death_sound": "sounds/lobodeath.mp3"},
    "jades":      {"health": 80, "speed": 1.5, "contact_damage": 12, "scale": 5.5, "y_offset": 5, "sprite_path": "Enemies/jades.png", "death_sound": "sounds/lobodeath.mp3"},
    "wind":       {"health": 35, "speed": 2.2, "contact_damage": 7, "scale": 5.5, "y_offset": 5, "sprite_path": "Enemies/wind.png", "death_sound": "sounds/lobodeath.mp3"},
    
    # --- Enemigos con Animaciones y Lógica de Ataque ---
    "esqueleto": {
        "health": 60, "speed": 1.5, "death_sound": "sounds/muerte_esqueleto.wav", "scale": 1.8, "y_offset": 5,
        "attack_damage": 15, "attack_range": 120, "attack_cooldown": 1500, "attack_damage_frame": 4, "detection_radius": 400,
        "anim_data": { "attack": {"path": "Enemies/Skeleton/skeleton_atk.png", "frames": 6} }
    },
    # Ajuste final de altura Y RANGO DE ATAQUE AUMENTADO
    "golem": {
        "health": 150, "speed": 1, "death_sound": "sounds/muerte_golem.wav", "scale": 3.5, "y_offset": 25, 
        "attack_damage": 25, "attack_range": 220, "attack_cooldown": 2200, "attack_damage_frame": 5, "detection_radius": 350, # <-- RANGO AUMENTADO
        "anim_data": {
            "idle":   {"path": "Enemies/golem/Golem_1_idle.png",   "frames": 8},
            "walk":   {"path": "Enemies/golem/Golem_1_walk.png",   "frames": 10},
            "attack": {"path": "Enemies/golem/Golem_1_attack.png", "frames": 9},
            "die":    {"path": "Enemies/golem/Golem_1_die.png",    "frames": 11}
        }
    },
    "wizzardblue": {
        "health": 70, "speed": 1.8, "death_sound": "sounds/lobodeath.mp3", "scale": 1.2, "y_offset": 15,
        "attack_damage": 18, "attack_range": 350, "attack_cooldown": 1800, "attack_damage_frame": 3, "detection_radius": 500,
        "is_flying": True, "is_ranged": True, 
        "sprite_path": "Enemies/wizzardblue.png"
    },
    "boss1": {
        "health": BOSS_HEALTH, "speed": 0, "death_sound": "sounds/muerte_jefe.wav", "scale": 1.0, "y_offset": 5,
        "sprite_path": "Enemies/boss1.png",
        "is_boss": True
    }
}

# --- Map and Sound Paths ---
MAP_BOSQUE_PATH = "fondos/mapa_bosque.png"; MAP_ALDEA_PATH = "fondos/mapa_aldea.png"
MAP_MAZMORRA_PATH = "fondos/mapa_mazmorra.png"; MAP_MAZMORRA_P1_PATH = "fondos/mazmorra_p1.png"
MAP_MAZMORRA_P2_PATH = "fondos/mazmorra_p2.png"; MAP_MAZMORRA_P3_PATH = "fondos/mazmorra_p3.png"
MAP_MAZMORRA_P4_PATH = "fondos/mazmorra_p4.png"; MAP_MAZMORRA_P5_PATH = "fondos/mazmorra_p5.png"
MAP_MAZMORRA_JEFE_PATH = "fondos/mapa_boss1.png"

MENU_MUSIC_PATH = "Soundtracks/menu.mp3"
BOSS_MUSIC_PATH = "Soundtracks/soundtrackboss1.mp3"

INITIAL_ZOOM = 0.85
DEATH_QUOTES = [
    ("La muerte de un hombre es una tragedia. La muerte de millones es estadística.", "Iósif Stalin"),
    ("El hombre que teme la muerte no hará nunca nada digno de un hombre vivo.", "Séneca"),
]