"""
Configuration - Game Settings and Constants
===========================================

Central configuration file for all game settings, constants, and tunable parameters.
Allows for easy balancing and customization without code changes.

TODO:
- Implement configuration loading from files (JSON/YAML)
- Add runtime configuration modification
- Create configuration validation
- Add preset configurations for different game modes
- Implement save/load user preferences
"""

import os

class GameConfig:
    """
    Main game configuration class
    
    TODO: Load from external config files and allow runtime modification
    """
    
    # Display settings
    SCREEN_WIDTH = 1920
    SCREEN_HEIGHT = 1080
    TARGET_FPS = 60
    FULLSCREEN = False
    VSYNC = True
    
    # Game settings
    MAX_PLAYERS = 2
    DEFAULT_LIVES = 3
    MATCH_TIME_LIMIT = 480  # 8 minutes in seconds
    
    # Physics constants
    GRAVITY = 0.8
    AIR_FRICTION = 0.02
    GROUND_FRICTION = 0.15
    TERMINAL_VELOCITY = 20.0
    
    # Input settings
    INPUT_BUFFER_FRAMES = 6  # Frames to buffer inputs for combos
    INPUT_LAG_COMPENSATION = True
    
    # Audio settings
    MASTER_VOLUME = 1.0
    MUSIC_VOLUME = 0.7
    SFX_VOLUME = 0.8
    
    # Debug settings
    DEBUG_MODE = False
    SHOW_HITBOXES = False
    SHOW_FPS = False
    SHOW_INPUT_DISPLAY = False

class CharacterConfig:
    """
    Character-specific configuration values
    
    TODO: Load character data from external files
    """
    
    # Default character stats (can be overridden per character)
    DEFAULT_HEALTH = 100
    DEFAULT_WEIGHT = 1.0
    DEFAULT_WALK_SPEED = 3.0
    DEFAULT_RUN_SPEED = 6.0
    DEFAULT_JUMP_STRENGTH = 15.0
    DEFAULT_AIR_SPEED = 4.0
    
    # Combat constants
    DEFAULT_HITSTUN_MULTIPLIER = 1.0
    DEFAULT_KNOCKBACK_MULTIPLIER = 1.0
    INVINCIBILITY_FRAMES_ON_HIT = 30

class StageConfig:
    """
    Stage-specific configuration values
    
    TODO: Load stage data from external files
    """
    
    # Default stage dimensions
    DEFAULT_STAGE_WIDTH = 1200
    DEFAULT_STAGE_HEIGHT = 800
    
    # Blast zone offsets
    BLAST_ZONE_LEFT_OFFSET = 200
    BLAST_ZONE_RIGHT_OFFSET = 200
    BLAST_ZONE_TOP_OFFSET = 200
    BLAST_ZONE_BOTTOM_OFFSET = 200
    
    # Platform defaults
    DEFAULT_PLATFORM_WIDTH = 200
    DEFAULT_PLATFORM_HEIGHT = 20

class InputConfig:
    """
    Input configuration and key mappings
    
    TODO: Allow customizable key bindings
    TODO: Add controller support configuration
    """
    
    # Player 1 default keys (WASD + extras)
    P1_MOVE_LEFT = 'a'
    P1_MOVE_RIGHT = 'd'
    P1_JUMP = 'w'
    P1_CROUCH = 's'
    P1_LIGHT_ATTACK = 'q'
    P1_HEAVY_ATTACK = 'e'
    P1_SIDE_SPECIAL = 'r'
    P1_UP_SPECIAL = 't'
    P1_DOWN_SPECIAL = 'f'
    P1_GRAB = 'g'
    
    # Player 2 default keys (IJKL + extras)
    P2_MOVE_LEFT = 'j'
    P2_MOVE_RIGHT = 'l'
    P2_JUMP = 'i'
    P2_CROUCH = 'k'
    P2_LIGHT_ATTACK = 'u'
    P2_HEAVY_ATTACK = 'o'
    P2_SIDE_SPECIAL = 'p'
    P2_UP_SPECIAL = '['
    P2_DOWN_SPECIAL = ';'
    P2_GRAB = "'"
    
    # Global keys
    PAUSE = 'escape'
    CONFIRM = 'return'
    CANCEL = 'escape'

class AudioConfig:
    """
    Audio configuration and file paths
    
    TODO: Implement audio asset management
    """
    
    # Audio file paths (TODO: populate with actual files)
    MENU_MUSIC = "assets/audio/music/menu_theme.ogg"
    CHARACTER_SELECT_MUSIC = "assets/audio/music/character_select.ogg"
    BATTLEFIELD_MUSIC = "assets/audio/music/battlefield_theme.ogg"
    VOLCANO_MUSIC = "assets/audio/music/volcano_theme.ogg"
    
    # Sound effect paths
    MENU_NAVIGATE_SFX = "assets/audio/sfx/menu_navigate.wav"
    MENU_SELECT_SFX = "assets/audio/sfx/menu_select.wav"
    HIT_SFX = "assets/audio/sfx/hit.wav"
    JUMP_SFX = "assets/audio/sfx/jump.wav"
    LAND_SFX = "assets/audio/sfx/land.wav"

class VisualConfig:
    """
    Visual configuration and asset paths
    
    TODO: Implement visual asset management
    """
    
    # Character sprite paths (TODO: populate with actual files)
    WARRIOR_SPRITES = "assets/images/characters/warrior/"
    SPEEDSTER_SPRITES = "assets/images/characters/speedster/"
    HEAVY_SPRITES = "assets/images/characters/heavy/"
    
    # Stage background paths
    BATTLEFIELD_BG = "assets/images/stages/battlefield/"
    VOLCANO_BG = "assets/images/stages/volcano/"
    
    # UI element paths
    UI_ELEMENTS = "assets/images/ui/"
    
    # Visual effect settings
    PARTICLE_COUNT_MULTIPLIER = 1.0
    SCREEN_SHAKE_INTENSITY = 1.0
    FLASH_EFFECT_INTENSITY = 1.0

class DevelopmentConfig:
    """
    Development and debugging configuration
    
    TODO: Add more debug visualization options
    """
    
    # Debug rendering
    DEBUG_DRAW_HITBOXES = True
    DEBUG_DRAW_HURTBOXES = True
    DEBUG_DRAW_COLLISION_RECTS = False
    DEBUG_DRAW_VELOCITY_VECTORS = False
    DEBUG_DRAW_PLATFORM_EDGES = False
    
    # Debug colors
    HITBOX_COLOR = (255, 0, 0)      # Red
    HURTBOX_COLOR = (0, 0, 255)     # Blue
    COLLISION_COLOR = (0, 255, 0)   # Green
    VELOCITY_COLOR = (255, 255, 0)  # Yellow
    
    # Performance monitoring
    SHOW_PERFORMANCE_METRICS = False
    LOG_FRAME_TIMES = False
    PROFILE_PHYSICS = False

def load_config_from_file(filepath):
    """
    Load configuration from external file
    
    TODO:
    - Support JSON and YAML config files
    - Validate configuration values
    - Handle missing or invalid config gracefully
    - Allow partial config overrides
    """
    # TODO: Implement config file loading
    # if os.path.exists(filepath):
    #     with open(filepath, 'r') as f:
    #         config_data = json.load(f)
    #         # Apply config_data to appropriate Config classes
    pass

def save_config_to_file(filepath):
    """
    Save current configuration to file
    
    TODO:
    - Export current config values to file
    - Support user preference saving
    - Handle file write errors gracefully
    """
    # TODO: Implement config file saving
    pass

def get_user_config_path():
    """
    Get path to user configuration directory
    
    TODO:
    - Create platform-specific config directories
    - Handle permissions and directory creation
    """
    # TODO: Implement platform-specific config paths
    # Windows: %APPDATA%/SuperSmashFighters/
    # Linux: ~/.config/SuperSmashFighters/
    # Mac: ~/Library/Application Support/SuperSmashFighters/
    return "config/"

def validate_config():
    """
    Validate all configuration values
    
    TODO:
    - Check that all required values are set
    - Validate ranges for numeric values
    - Ensure file paths exist
    - Check for conflicting settings
    """
    # TODO: Implement configuration validation
    errors = []
    
    # Example validations:
    # if GameConfig.SCREEN_WIDTH < 640:
    #     errors.append("Screen width too small (minimum 640)")
    # if GameConfig.TARGET_FPS < 30:
    #     errors.append("Target FPS too low (minimum 30)")
    
    return errors

# Initialize with default values
# TODO: Load from config file if it exists
def initialize_config():
    """
    Initialize configuration system
    
    TODO:
    - Load user config if it exists
    - Apply command line overrides
    - Validate final configuration
    """
    user_config_path = os.path.join(get_user_config_path(), "config.json")
    
    # TODO: Load user config
    # load_config_from_file(user_config_path)
    
    # TODO: Validate configuration
    # errors = validate_config()
    # if errors:
    #     print("Configuration errors:", errors)
    
    pass 