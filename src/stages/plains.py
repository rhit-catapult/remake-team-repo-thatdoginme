"""
Plains Stage - Wide Open Battlefield Arena
==========================================

The Plains stage offers a completely different gameplay experience from Battlefield,
emphasizing ground-based combat and horizontal movement over vertical platform play.
This stage is perfect for characters who excel in neutral game and spacing.

Stage Design Philosophy:
========================
- Extremely wide main platform encourages ground-based neutral game
- Minimal vertical elements keep focus on horizontal spacing
- Open design rewards precise movement and positioning
- Long-range combat and projectile play are emphasized
- Perfect for teaching fundamental fighting game concepts

Unique Features:
===============
- Extra-wide main platform (largest fighting surface)
- Small side platforms for minimal vertical options
- Enhanced gravity effects that favor grounded play
- Rolling terrain with subtle elevation changes
- Natural grass and dirt visual theme

Gravity Mechanics Differences:
=============================
- Slightly increased gravity encourages staying grounded
- Reduced air time makes jumping more committal
- Enhanced ground friction for precise movement control
- Modified air friction affects projectile physics
- Platform magnetism helps with precise positioning

Visual Theme:
============
- Rolling grasslands with natural terrain
- Distant mountains and horizon for depth
- Dynamic sky with weather effects
- Realistic lighting that changes throughout the match
- Organic, natural aesthetic contrasts with Battlefield's floating platforms

A castle-like structure for vertical combat and platforming challenges.
"""

from .base_stage import Stage, Platform, PlatformType
import pygame
import numpy as np
import math
import random

class Plains(Stage):
    """
    Plains Stage Implementation
    
    This stage creates a fundamentally different fighting experience focused
    on ground-based combat, spacing, and neutral game rather than platform
    movement and aerial mixups.
    """
    
    def __init__(self):
        """
        Initialize the Plains stage with ground-focused design
        
        Stage Dimensions:
        - Width: 1400 pixels (wider than Battlefield for more spacing)
        - Height: 700 pixels (less vertical space emphasizes ground game)
        
        The increased width and reduced height create a 2:1 aspect ratio
        that emphasizes horizontal movement and spacing over vertical play.
        """
        # Call parent constructor with ground-focused dimensions
        super().__init__("Snowdin", 1400, 700)
        
        # === STAGE METADATA ===
        # Describes the stage's role and characteristics
        self.description = "A castle-like structure for vertical combat."
        self.theme = "Castle Siege"
        self.music_track = "castle_theme.ogg" # Placeholder music
        self.competitive_legal = True
        self.difficulty_rating = "Intermediate"
        
        # === UNIQUE GRAVITY SETTINGS ===
        # These values create a heavier, more grounded feel
        self.gravity_multiplier = 1.15     # 15% stronger gravity than Battlefield
        self.air_friction_modifier = 1.3   # 30% more air resistance
        self.terminal_velocity_cap = 16.0  # Lower terminal velocity
        self.platform_magnetism = 1.2      # Stronger "stickiness" when landing
        
        # === GROUND-FOCUSED PHYSICS ===
        # Enhanced properties for ground-based gameplay
        self.wind_resistance = 0.05        # Slight wind affects aerial movement
        self.surface_friction = 0.08       # Less ground friction for smoother movement
        self.ledge_grab_distance = 15      # Shorter ledge grab range (fewer platforms)
        self.platform_drop_frames = 12    # Longer drop-through time (more committal)
        
        # === TERRAIN PROPERTIES ===
        # Natural terrain affects movement slightly
        self.terrain_variation = 5         # Height variation in terrain (pixels)
        self.grass_friction_zones = []     # Areas with different friction
        self.elevation_changes = []        # Subtle slopes and hills
        self.natural_boundaries = True     # Organic-looking stage edges
        
        # === WEATHER SYSTEM ===
        # Dynamic weather effects that don't affect gameplay
        self.weather_enabled = True
        self.wind_direction = random.choice([-1, 1])  # Wind direction for effects
        self.wind_strength = random.uniform(0.3, 0.7)  # Wind intensity
        self.cloud_coverage = random.uniform(0.2, 0.8)  # Sky cloud density
        
        # === VISUAL EFFECTS SETTINGS ===
        # Natural, organic visual elements
        self.enable_parallax = True        # Mountain/horizon parallax
        self.grass_animation_speed = 0.0   # Swaying grass animation
        self.ambient_particle_count = 25   # More particles for natural feel
        self.lighting_intensity = 0.9      # Brighter natural lighting
        self.time_of_day = "midday"       # Affects lighting and shadows
        
        # Initialize all stage components
        self.setup_platforms()     # Create the castle platform layout
        self.setup_spawn_points()  # Define symmetric spawn positions
        self.setup_blast_zones()   # Set wide blast zone boundaries
        self.setup_terrain()       # Create natural ground variations
        self.setup_visuals()       # Initialize natural graphics
        self.setup_camera_bounds() # Define camera for wide stage
        self.setup_weather_system() # Initialize dynamic weather
        
        # Load the background image
        self.background_image = pygame.image.load("assets/images/plains bg.png").convert()
        self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))

        # Initialize particles
        self.particles = []

        print(f"✓ Snowdin stage initialized with {len(self.platforms)} platforms")
        print(f"✓ Wind blowing {['left', 'right'][self.wind_direction == 1]} at {self.wind_strength:.1f} strength")
    
    def spawn_particle(self):
        """Spawns a single snow particle at a random location at the top of the screen."""
        x = random.uniform(0, self.width)
        y = random.uniform(-50, -10)
        vx = random.uniform(-0.5, 0.5) + self.wind_direction * self.wind_strength
        vy = random.uniform(0.5, 1.5)
        size = random.randint(1, 3)
        lifetime = random.randint(300, 600) # Frames
        
        particle = {
            'x': x, 'y': y, 'vx': vx, 'vy': vy, 
            'size': size, 'lifetime': lifetime, 'landed_timer': -1,
            'color': (255, 255, 255, random.randint(150, 220))
        }
        
        self.particles.append(particle)
        print(f"🌨️ Spawned snow particle at ({x:.1f}, {y:.1f}), total particles: {len(self.particles)}")

    def setup_platforms(self):
        """
        Create the Castle platform layout.

        Platform Design Philosophy:
        ===========================
        1. A large central tower to act as a focal point for combat.
        2. Side ledges on the tower to allow for climbing and vertical movement.
        3. Walls on the side of the stage to prevent players from falling off.
        4. A flat ground plane spanning the width of the stage.
        """

        # === MAIN PLATFORM (Ground Level) ===
        main_platform_width = self.width  # Span the entire stage width
        main_platform_height = 100
        main_platform_x = 0
        main_platform_y = self.height - 100

        self.main_platform = Platform(
            x=main_platform_x,
            y=main_platform_y,
            width=main_platform_width,
            height=main_platform_height,
            platform_type=PlatformType.SOLID
        )
        self.main_platform.has_ledges = True
        self.main_platform.surface_grip = 1.0
        self.main_platform.is_main_stage = True
        self.main_platform.terrain_type = "snow"
        self.platforms.append(self.main_platform)
        print(f"✓ Main ground platform created: {main_platform_width}x{main_platform_height}")

        # === CASTLE TOWER ===
        tower_width = 200
        tower_height = 180  # Lowered for easier access
        tower_x = (self.width - tower_width) / 2
        tower_y = main_platform_y - tower_height

        castle_tower = Platform(
            x=tower_x,
            y=tower_y,
            width=tower_width,
            height=tower_height,
            platform_type=PlatformType.SOLID
        )
        castle_tower.has_ledges = True
        castle_tower.terrain_type = "rock"
        castle_tower.platform_id = "castle_tower"
        self.platforms.append(castle_tower)
        print("✓ Castle tower created.")

        # === SIDE TOWERS ===
        side_tower_width = 150
        side_tower_height = 120
        side_tower_y = main_platform_y - side_tower_height

        # Left Tower
        left_tower_x = 150
        left_tower = Platform(
            x=left_tower_x,
            y=side_tower_y,
            width=side_tower_width,
            height=side_tower_height,
            platform_type=PlatformType.SOLID
        )
        left_tower.has_ledges = True
        left_tower.terrain_type = "rock"
        left_tower.platform_id = "left_side_tower"
        self.platforms.append(left_tower)

        # Right Tower
        right_tower_x = self.width - 150 - side_tower_width
        right_tower = Platform(
            x=right_tower_x,
            y=side_tower_y,
            width=side_tower_width,
            height=side_tower_height,
            platform_type=PlatformType.SOLID
        )
        right_tower.has_ledges = True
        right_tower.terrain_type = "rock"
        right_tower.platform_id = "right_side_tower"
        self.platforms.append(right_tower)
        print("✓ Side towers created.")

        # === FLOATING PLATFORMS ===
        floating_platform_width = 120
        floating_platform_height = 20
        floating_platform_y = tower_y  # Same height as central tower

        # Left floating platform
        gap_left_start = left_tower_x + side_tower_width
        gap_left_end = tower_x
        left_floating_platform_x = gap_left_start + (gap_left_end - gap_left_start - floating_platform_width) / 2
        left_floating_platform = Platform(
            x=left_floating_platform_x,
            y=floating_platform_y,
            width=floating_platform_width,
            height=floating_platform_height,
            platform_type=PlatformType.PASS_THROUGH
        )
        left_floating_platform.has_ledges = True
        left_floating_platform.drop_through_enabled = True
        left_floating_platform.terrain_type = "rock"
        left_floating_platform.platform_id = "left_floating_platform"
        self.platforms.append(left_floating_platform)

        # Right floating platform
        gap_right_start = tower_x + tower_width
        gap_right_end = right_tower_x
        right_floating_platform_x = gap_right_start + (gap_right_end - gap_right_start - floating_platform_width) / 2
        right_floating_platform = Platform(
            x=right_floating_platform_x,
            y=floating_platform_y,
            width=floating_platform_width,
            height=floating_platform_height,
            platform_type=PlatformType.PASS_THROUGH
        )
        right_floating_platform.has_ledges = True
        right_floating_platform.drop_through_enabled = True
        right_floating_platform.terrain_type = "rock"
        right_floating_platform.platform_id = "right_floating_platform"
        self.platforms.append(right_floating_platform)
        print("✓ Floating platforms created.")

        # === PLATFORM MEASUREMENT STORAGE ===
        # Store measurements for gameplay systems
        self.platform_heights = {
            'main': main_platform_y,
            'tower': tower_y,
            'side_tower': side_tower_y,
            'floating_platform': floating_platform_y
        }
        
        # Calculate spacing for AI and movement systems
        self.platform_distances = {
            'tower_width': tower_width,
            'side_tower_width': side_tower_width,
            'floating_platform_width': floating_platform_width,
            'main_width': main_platform_width
        }
    
    def setup_terrain(self):
        """
        Create natural terrain variations and features
        
        Terrain Philosophy:
        ==================
        - Subtle elevation changes add visual interest without affecting gameplay
        - Different surface types provide variety in movement feel
        - Natural boundaries feel organic rather than artificial
        - Terrain guides players toward center stage combat
        """
        
        # === ELEVATION VARIATIONS ===
        # Subtle height changes across the main platform
        self.elevation_changes = []
        
        # Create gentle rolling hills across the stage
        num_elevation_points = 20
        for i in range(num_elevation_points):
            x_position = (self.width / num_elevation_points) * i
            # Use sine wave for natural rolling terrain
            elevation_offset = math.sin(i * 0.5) * self.terrain_variation
            
            self.elevation_changes.append({
                'x': x_position,
                'height_offset': elevation_offset,
                'terrain_type': 'snow'
            })
        
        # === SURFACE FRICTION ZONES ===
        # Different areas have slightly different movement properties
        self.grass_friction_zones = []
        
        print("✓ Natural terrain variations created for visual and tactical variety")
    
    def setup_spawn_points(self):
        """
        Define spawn points optimized for ground-based combat
        
        Spawn Philosophy:
        ================
        - Greater distance between players emphasizes neutral game
        - Positioned on main platform for immediate ground access
        - Wider spacing requires more commitment to approach
        - Equal distance from center maintains competitive balance
        """
        
        # Calculate spawn positions with extra spacing for ground-focused play
        main_platform_center = self.main_platform.x + (self.main_platform.width // 2)
        spawn_distance_from_center = 320  # Much wider than Battlefield (250px)
        spawn_height_offset = -60         # Slightly higher above platform
        
        # Player 1 spawn point (left side)
        player1_spawn_x = main_platform_center - spawn_distance_from_center
        player1_spawn_y = self.main_platform.y + spawn_height_offset
        
        self.add_spawn_point(player1_spawn_x, player1_spawn_y)
        
        # Player 2 spawn point (right side)
        player2_spawn_x = main_platform_center + spawn_distance_from_center
        player2_spawn_y = self.main_platform.y + spawn_height_offset
        
        self.add_spawn_point(player2_spawn_x, player2_spawn_y)
        
        print(f"✓ Spawn points set with wider spacing ({spawn_distance_from_center}px) for neutral game")
        
        # Store spawn information for respawning and camera setup
        self.spawn_info = {
            'center_x': main_platform_center,
            'center_y': player1_spawn_y,
            'distance': spawn_distance_from_center,
            'spacing_philosophy': 'wide_neutral_game',
            'facing_inward': True
        }
    
    def setup_blast_zones(self):
        """
        Define blast zones optimized for the wider stage
        
        Blast Zone Philosophy:
        =====================
        - Wider horizontal blast zones match the increased stage width
        - Closer vertical blast zones compensate for enhanced gravity
        - Bottom blast zone positioned for spike/meteor opportunities
        - Balanced to prevent excessive camping or stalling
        """
        
        # Horizontal blast zones (adjusted for side KOs)
        horizontal_distance = 200  # Closer than before for easier side KOs
        self.left_blast_zone = -horizontal_distance
        self.right_blast_zone = self.width + horizontal_distance
        
        # Vertical blast zones (adjusted for better visibility)
        top_distance = 200        # Top blast zone
        bottom_distance = 200     # Much closer bottom blast zone for better particle visibility
        
        self.top_blast_zone = -top_distance
        self.bottom_blast_zone = self.height + bottom_distance
        
        print(f"✓ Blast zones set for side KOs: X±{horizontal_distance}, Y+{top_distance}/-{bottom_distance}")
        
        # Store blast zone information
        self.blast_zone_info = {
            'horizontal_distance': horizontal_distance,
            'top_distance': top_distance,
            'bottom_distance': bottom_distance,
            'allows_side_kos': True,  # New flag
            'total_width': self.right_blast_zone - self.left_blast_zone,
            'total_height': self.bottom_blast_zone - self.top_blast_zone
        }
    
    def setup_weather_system(self):
        """
        Initialize dynamic weather effects
        
        Weather Philosophy:
        ==================
        - Weather provides atmosphere without affecting gameplay balance
        - Visual effects enhance the natural theme
        - Subtle environmental storytelling
        - Adds variety to multiple matches on the same stage
        """
        
        # === WIND SYSTEM ===
        # Affects visual elements but not gameplay physics
        self.wind_system = {
            'direction': self.wind_direction,
            'strength': self.wind_strength,
            'gusts': {
                'enabled': True,
                'frequency': random.uniform(0.1, 0.3),  # Gusts per second
                'strength_multiplier': random.uniform(1.5, 2.5)
            },
            'affects_grass': True,
            'affects_clouds': True,
            'affects_particles': True
        }
        
        # === CLOUD SYSTEM ===
        # Dynamic cloud coverage and movement
        self.cloud_system = {
            'coverage': self.cloud_coverage,
            'movement_speed': 0.4 * self.wind_strength,
            'types': ['cumulus', 'cirrus', 'stratus'],
            'weather_chance': {
                'clear': 0.4,
                'partly_cloudy': 0.4,
                'overcast': 0.2
            }
        }
        
        # === LIGHTING SYSTEM ===
        # Natural lighting that changes throughout the match
        self.lighting_system = {
            'time_of_day': self.time_of_day,
            'sun_angle': 45,  # Degrees above horizon
            'shadow_length': 0.6,  # Relative to object height
            'color_temperature': 5500,  # Kelvin (daylight)
            'atmospheric_scattering': True
        }
        
        print(f"✓ Weather system initialized: {['cloudy', 'clear'][self.cloud_coverage < 0.5]} skies")
    
    def setup_camera_bounds(self):
        """
        Define camera bounds optimized for the wider Plains stage
        
        Camera Philosophy:
        =================
        - Wider camera bounds accommodate the larger fighting area
        - Camera follows action while keeping the natural horizon visible
        - Smooth movement prevents motion sickness during long matches
        - Zoom limits ensure players never lose track of the action
        """
        
        # Camera movement bounds (adjusted for wider stage)
        camera_margin = 150  # Larger margins for the wider stage
        
        self.camera_bounds = pygame.Rect(
            camera_margin,                    # Left bound
            camera_margin,                    # Top bound
            self.width - (camera_margin * 2), # Width
            self.height - (camera_margin * 2) # Height
        )
        
        # Camera zoom limits (adjusted for ground-focused gameplay)
        self.min_camera_zoom = 0.6   # Zoomed out more (shows full wide stage)
        self.max_camera_zoom = 1.2   # Less zoomed in (maintains spacing visibility)
        self.default_camera_zoom = 0.8  # Slightly zoomed out by default
        
        # Camera movement smoothing (slower for the larger stage)
        self.camera_follow_speed = 0.04    # Slightly slower following
        self.camera_zoom_speed = 0.025     # Slower zoom changes
        
        print(f"✓ Camera bounds set for wide stage with {camera_margin}px margins")
    
    def setup_visuals(self):
        """
        Initialize natural visual elements and atmospheric effects
        
        Visual Design Goals:
        ===================
        - Natural, organic aesthetic contrasts with Battlefield's clean look
        - Rich environmental details create immersive atmosphere
        - Dynamic weather and lighting add variety to repeated matches
        - Performance-optimized effects maintain smooth gameplay
        """
        
        # === PARTICLE EFFECTS ===
        # Natural atmospheric particles
        self.particle_system = {
            "enabled": True,
            "max_particles": self.ambient_particle_count,
            "spawn_rate": 0.15,               # Particles per frame
            "wind_affected": True,            # Particles move with wind
            "particle_types": [
                {
                    "type": "snowflakes",
                    "size_range": (1, 3),
                    "color": (255, 255, 255, 180),  # White snowflakes
                    "speed_range": (0.5, 1.5),
                    "lifetime_range": (400, 800),
                    "wind_sensitivity": 1.2
                },
                {
                    "type": "dust_motes",
                    "size_range": (1, 2),
                    "color": (255, 255, 255, 20),  # Light dust
                    "speed_range": (0.05, 0.3),
                    "lifetime_range": (500, 1000),
                    "wind_sensitivity": 0.8         # Moderately wind-affected
                }
            ]
        }
        
        # === LIGHTING SYSTEM ===
        # Natural lighting that changes with weather and time
        self.lighting = {
            "ambient_light": {
                "color": (255, 255, 240),        # Warm natural light
                "intensity": self.lighting_intensity,
                "direction": "omnidirectional",
                "weather_affected": True          # Dims with clouds
            },
            "sun_light": {
                "color": (255, 250, 200),        # Warm sunlight
                "intensity": 0.8,
                "angle": 60,                     # Higher sun angle
                "creates_shadows": True,         # Natural shadows
                "shadow_softness": 0.6          # Soft natural shadows
            },
            "atmospheric_scattering": {
                "enabled": True,
                "intensity": 0.3,               # Subtle atmospheric haze
                "color": (200, 220, 255),       # Blue atmospheric tint
                "distance_fade": True           # Objects fade with distance
            }
        }
        
        # === PLATFORM VISUAL PROPERTIES ===
        # Natural materials and textures
        self.platform_visuals = {
            "main_platform": {
                "base_color": (128, 128, 140),     # Cold earth brown
                "snow_color": (255, 255, 255),    # White snow
                "edge_color": (80, 50, 20),      # Darker earth edges
                "texture": "snowy_ground",      # Organic texture
                "has_snow": True,               # Snow layer on top
                "snow_density": 0.9,            # Thick snow coverage
                "shadow_opacity": 100,
                "weathering": True               # Shows natural wear
            },
            "side_platforms": {
                "base_color": (120, 120, 120),   # Gray stone
                "highlight_color": (150, 150, 150), # Lighter stone
                "edge_color": (90, 90, 90),      # Darker stone edges
                "texture": "rough_stone",        # Rocky texture
                "has_moss": True,                # Moss growth on stone
                "moss_color": (60, 100, 60),     # Dark green moss
                "shadow_opacity": 90,
                "weathering": True               # Natural stone weathering
            }
        }
        
        # === ANIMATION STATE TRACKING ===
        # Track timing for all animated elements
        self.animation_state = {
            "grass_sway_phase": 0.0,          # Grass swaying animation
            "particle_spawn_timer": 0.0,     # Particle spawning timing
            "lighting_flicker_phase": 0.0,   # Natural lighting variation
            "wind_gust_timer": 0.0,           # Wind gust timing
            "cloud_movement_offset": 0.0,    # Cloud position tracking
            "total_elapsed_time": 0.0,       # Total time for effects
            "weather_transition_timer": 0.0  # Weather change timing
        }
        
        # Initialize total elapsed time for immediate use
        self.total_elapsed_time = 0.0
        
        # Initialize grass animation phase
        self.grass_sway_phase = 0.0
        
        print("✓ Natural visual system initialized with weather effects and terrain animation")
    
    def apply_stage_gravity(self, character, delta_time):
        """
        Apply Plains-specific gravity effects to characters
        
        === PLAINS PHYSICS PHILOSOPHY ===
        Plains is designed as the "ground-focused" alternative to Battlefield.
        While Battlefield emphasizes aerial combat, Plains rewards ground game:
        
        Key Differences from Battlefield:
        - Enhanced gravity (1.15x multiplier vs 1.0x) keeps players grounded longer
        - Reduced terminal velocity (16.0 vs 18.0) for more controlled falls
        - Increased air friction (1.3x vs 0.8x) makes aerial movement more committal
        - Wind resistance affects horizontal air movement
        - Different terrain zones provide subtle movement variations
        
        Gameplay Impact:
        - Shorter combos due to faster falling
        - More emphasis on ground-based neutral game
        - Air approaches are riskier and more committal
        - Favors characters with strong ground options
        
        This creates a heavier, more deliberate feel that emphasizes
        ground-based combat and precise spacing over aerial mixups.
        
        Args:
            character: The character object to apply gravity to
            delta_time (float): Time in seconds since last frame
        """
        
        print(f"🌾 Plains gravity for P{character.player_id}: on_ground={character.on_ground}, dt={delta_time:.3f}")
        
        # Get base gravity and apply Plains modifications
        base_gravity = 0.8  # Standard gravity value
        stage_gravity = base_gravity * self.gravity_multiplier  # 15% stronger
        
        print(f"   Base gravity: {base_gravity}, multiplier: {self.gravity_multiplier}, stage gravity: {stage_gravity}")
        
        # === TERRAIN-BASED GRAVITY VARIATIONS ===
        # Different areas of the stage have slightly different gravity
        character_x = character.position[0]
        character_y = character.position[1]
        
        # Check if character is over different terrain types
        terrain_gravity_modifier = 1.0
        
        # Slightly stronger gravity near the edges (encourages center stage play)
        if character_x < self.main_platform.x + 100 or character_x > self.main_platform.x + self.main_platform.width - 100:
            terrain_gravity_modifier = 1.05  # 5% stronger gravity near edges
            print(f"   🏔️ Edge gravity boost: {terrain_gravity_modifier}x")
        
        # Apply terrain modification
        stage_gravity *= terrain_gravity_modifier
        
        # === WIND RESISTANCE EFFECTS ===
        # Subtle wind affects aerial movement (visual/atmospheric, minimal gameplay impact)
        wind_effect = 0.0
        if not character.is_on_ground() and self.weather_enabled:
            # Very subtle horizontal push based on wind direction
            wind_effect = self.wind_direction * self.wind_strength * 0.02  # Minimal effect
            print(f"   💨 Wind effect: {wind_effect:.3f}")
        
        # === APPLY MODIFIED GRAVITY ===
        if not character.is_on_ground():
            print(f"   🌊 Applying enhanced gravity {stage_gravity} to airborne P{character.player_id}")
            old_vel_y = character.velocity[1]
            
            # Apply enhanced gravity acceleration
            character.velocity[1] += stage_gravity
            
            print(f"   📈 Velocity Y: {old_vel_y:.2f} -> {character.velocity[1]:.2f}")
            
            # Apply enhanced air friction (makes jumping more committal)
            air_friction = 0.02 * self.air_friction_modifier  # 30% more air friction
            old_vel_x = character.velocity[0]
            character.velocity[0] *= (1.0 - air_friction)
            
            print(f"   🌬️ Enhanced air friction {air_friction:.4f}: vel_x {old_vel_x:.2f} -> {character.velocity[0]:.2f}")
            
            # Apply subtle wind resistance
            if wind_effect != 0.0:
                old_vel_x2 = character.velocity[0]
                character.velocity[0] += wind_effect
                print(f"   💨 Wind resistance: vel_x {old_vel_x2:.2f} -> {character.velocity[0]:.2f}")
            
            # Enforce lower terminal velocity (falls feel more controlled)
            if character.velocity[1] > self.terminal_velocity_cap:
                character.velocity[1] = self.terminal_velocity_cap
                print(f"   🏁 Terminal velocity cap applied: {self.terminal_velocity_cap}")
        else:
            print(f"   🏃 P{character.player_id} on ground")
            
            # === GROUND FRICTION VARIATIONS ===
            # Different terrain zones have slightly different friction
            ground_friction = self.surface_friction
            
            # Check if character is in a special friction zone
            for zone in self.grass_friction_zones:
                if zone['x'] <= character_x <= zone['x'] + zone['width']:
                    ground_friction *= zone['friction_modifier']
                    print(f"   🌱 Special friction zone: {ground_friction:.3f}")
                    break
            
            # Apply ground friction
            old_vel_x = character.velocity[0]
            character.velocity[0] *= (1.0 - ground_friction)
            print(f"   🏔️ Ground friction {ground_friction:.3f}: vel_x {old_vel_x:.2f} -> {character.velocity[0]:.2f}")
        
        # === ENHANCED PLATFORM MAGNETISM ===
        # Make platforms feel more "sticky" for precise positioning
        if character.is_on_ground() and hasattr(character, 'just_landed') and character.just_landed:
            # Stronger reduction of horizontal momentum when landing
            magnetism_effect = self.platform_magnetism * 0.15  # Stronger than Battlefield
            old_vel_x = character.velocity[0]
            character.velocity[0] *= (1.0 - magnetism_effect)
            print(f"   🧲 Enhanced platform magnetism: vel_x {old_vel_x:.2f} -> {character.velocity[0]:.2f}")
    
    def update(self, delta_time):
        """
        Update all dynamic Plains stage elements
        
        This method handles:
        - Weather system updates (wind, clouds, lighting)
        - Terrain animation (swaying grass, particle effects)
        - Natural lighting changes
        - Environmental sound effects
        
        Args:
            delta_time (float): Time in seconds since last update
        """
        
        # Call parent update for base functionality
        super().update(delta_time)
        
        # Track total elapsed time for natural effects
        if not hasattr(self, 'total_elapsed_time'):
            self.total_elapsed_time = 0.0
        self.total_elapsed_time += delta_time
        
        # Spawn new particles
        if random.random() < 0.5: # Spawn roughly every other frame
            self.spawn_particle()
        
        # Update existing particles
        self.update_particles()
        
        # === UPDATE WEATHER SYSTEM ===
        if self.weather_enabled:
            self.update_weather_effects(delta_time)
        
        # === UPDATE TERRAIN ANIMATION ===
        self.update_terrain_effects(delta_time)
        
        # === UPDATE NATURAL LIGHTING ===
        self.update_lighting_effects(delta_time)
        
        # === UPDATE PLATFORM STATES ===
        for platform in self.platforms:
            platform.update(delta_time)
    
    def update_weather_effects(self, delta_time):
        """
        Update dynamic weather effects
        
        Args:
            delta_time (float): Time in seconds since last update
        """
        
        # === UPDATE WIND SYSTEM ===
        # Occasional wind gusts for visual variety
        if hasattr(self, 'wind_system') and self.wind_system['gusts']['enabled']:
            # Check for wind gust timing
            if not hasattr(self, 'next_gust_time'):
                self.next_gust_time = self.total_elapsed_time + random.uniform(3.0, 8.0)
            
            if self.total_elapsed_time >= self.next_gust_time:
                # Trigger wind gust
                self.wind_strength *= self.wind_system['gusts']['strength_multiplier']
                self.wind_gust_duration = random.uniform(0.5, 1.5)
                self.wind_gust_start = self.total_elapsed_time
                
                # Schedule next gust
                self.next_gust_time = self.total_elapsed_time + random.uniform(5.0, 12.0)
            
            # End wind gust
            if hasattr(self, 'wind_gust_start'):
                if self.total_elapsed_time - self.wind_gust_start > self.wind_gust_duration:
                    self.wind_strength = random.uniform(0.3, 0.7)  # Return to normal
                    delattr(self, 'wind_gust_start')
        
        # === UPDATE CLOUD MOVEMENT ===
        if hasattr(self, 'cloud_system'):
            # Clouds move based on wind strength and direction
            cloud_speed = self.cloud_system['movement_speed'] * self.wind_direction
            # Cloud positions would be updated here in a full implementation
    
    def update_terrain_effects(self, delta_time):
        """
        Update natural terrain animations
        
        Args:
            delta_time (float): Time in seconds since last update
        """
        
        # === GRASS SWAYING ANIMATION ===
        # Grass sways based on wind strength and direction
        if not hasattr(self, 'grass_sway_phase'):
            self.grass_sway_phase = 0.0
        
        # Update grass animation phase
        sway_speed = self.grass_animation_speed * (1.0 + self.wind_strength * 0.5)
        self.grass_sway_phase += delta_time * sway_speed * 2 * math.pi
        
        # Keep phase in reasonable range
        if self.grass_sway_phase > 2 * math.pi:
            self.grass_sway_phase -= 2 * math.pi
        
        # === PARTICLE EFFECTS ===
        # Natural particles like pollen, dust, or leaves
        if not hasattr(self, 'particle_spawn_timer'):
            self.particle_spawn_timer = 0.0
        
        self.particle_spawn_timer += delta_time
        
        # Spawn particles based on wind strength
        spawn_rate = 0.2 + (self.wind_strength * 0.3)  # More particles in stronger wind
        if self.particle_spawn_timer >= spawn_rate:
            self.particle_spawn_timer = 0.0
            # Particle spawning would be implemented here
    
    def update_lighting_effects(self, delta_time):
        """
        Update natural lighting effects
        
        Args:
            delta_time (float): Time in seconds since last update
        """
        
        # === DYNAMIC LIGHTING ===
        # Subtle changes in lighting intensity based on cloud coverage
        if hasattr(self, 'lighting_system'):
            base_intensity = self.lighting_intensity
            
            # Cloud coverage affects lighting
            cloud_dimming = self.cloud_coverage * 0.2  # Up to 20% dimming
            current_intensity = base_intensity * (1.0 - cloud_dimming)
            
            # Subtle flickering for natural feel
            flicker_amount = 0.02
            flicker = math.sin(self.total_elapsed_time * 3.0) * flicker_amount
            
            self.current_lighting_intensity = current_intensity + flicker
    
    def update_particles(self):
        """Update snow particle positions and lifetimes."""
        for particle in self.particles[:]:  # Iterate over a copy
            # Handle landed particles
            if particle['landed_timer'] > 0:
                particle['landed_timer'] -= 1
                if particle['landed_timer'] == 0:
                    self.particles.remove(particle)
                    continue
            else:
                # Movement
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                particle['lifetime'] -= 1

                # Apply wind
                particle['x'] += self.wind_direction * self.wind_strength * 0.2

                # Check for collision with platforms
                for platform in self.platforms:
                    if platform.get_rect().collidepoint(particle['x'], particle['y']):
                        particle['vy'] = 0
                        particle['vx'] = 0
                        particle['landed_timer'] = 120  # Despawn after 2 seconds
                        break

            # Remove particles that are off-screen or dead
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
    
    def render_background(self, screen, camera_offset):
        """
        Render the Plains background with a static image and particle effects.
        
        Args:
            screen: Pygame surface to render to
            camera_offset: (x, y) tuple of camera position offset
        """
        
        # Render the static background image with a parallax effect
        parallax_offset_x = camera_offset[0] * 0.1  # Scroll at 10% of camera speed
        parallax_offset_y = camera_offset[1] * 0.1
        screen.blit(self.background_image, (-parallax_offset_x, -parallax_offset_y))
        
        # === RENDER ATMOSPHERIC PARTICLES ===
        # Natural particles like snow
        self.render_atmospheric_particles(screen, camera_offset)
    
    def render_foreground(self, screen, camera_offset):
        """
        Render foreground elements, such as weather effects.
        """
        # === RENDER ATMOSPHERIC PARTICLES ===
        # Natural particles like snow
        self.render_atmospheric_particles(screen, camera_offset)
        
        # === RENDER KO PARTICLES ===
        # Render KO particles if they were passed from the game state
        if hasattr(self, 'ko_particles_from_game') and self.ko_particles_from_game:
            self.render_ko_particles_here(screen, camera_offset, self.ko_particles_from_game)
    
    def render_ko_particles_here(self, screen, camera_offset, ko_particles):
        """Render KO particles directly in the stage foreground alongside snow."""
        for p in ko_particles:
            # Calculate screen position from world position
            pos_x = p['pos'][0] - camera_offset[0]
            pos_y = p['pos'][1] - camera_offset[1]
            
            # Only draw if on screen
            if -50 <= pos_x <= screen.get_width() + 50 and -50 <= pos_y <= screen.get_height() + 50:
                # Draw clean particles
                pygame.draw.circle(screen, p['color'], (int(pos_x), int(pos_y)), p['size'])

    def render_atmospheric_particles(self, screen, camera_offset):
        """
        Render natural atmospheric particles
        
        Args:
            screen: Pygame surface to render to
            camera_offset: Camera position for parallax calculation
        """
        
        # Just render particles, don't update them here
        for particle in self.particles:
            screen_x = particle['x'] - camera_offset[0]
            screen_y = particle['y'] - camera_offset[1]

            # Only draw if on screen
            if 0 <= screen_x <= screen.get_width() and 0 <= screen_y <= screen.get_height():
                # Draw particle with white color
                pygame.draw.circle(screen, (255, 255, 255), (int(screen_x), int(screen_y)), particle['size'])
    
    def render_platforms(self, screen, camera_offset):
        """
        Render Plains platforms with natural styling
        
        Args:
            screen: Pygame surface to render to
            camera_offset: (x, y) tuple of camera position offset
        """
        
        # === RENDER PLATFORM SHADOWS ===
        for platform in self.platforms:
            self.render_platform_shadow(screen, platform, camera_offset)
        
        # === RENDER PLATFORMS WITH NATURAL STYLING ===
        for platform in self.platforms:
            screen_x = platform.x - camera_offset[0]
            screen_y = platform.y - camera_offset[1]
            
            # Determine platform visual style based on terrain type
            if platform == self.main_platform:
                # Main platform: natural grass and dirt
                base_color = (101, 67, 33)  # Rich brown earth
                snow_color = (255, 255, 255)  # White snow
                
                # Render earth base
                platform_rect = pygame.Rect(screen_x, screen_y, platform.width, platform.height)
                pygame.draw.rect(screen, base_color, platform_rect)
                
                # Add grass layer on top
                snow_height = 8
                snow_rect = pygame.Rect(screen_x, screen_y - snow_height, platform.width, snow_height)
                pygame.draw.rect(screen, snow_color, snow_rect)
                
                # Add grass texture with swaying effect
                self.render_snow_texture(screen, snow_rect, camera_offset)
                
            else:
                # Side platforms: rocky outcroppings
                rock_color = (120, 120, 120)  # Gray stone
                highlight_color = (150, 150, 150)  # Lighter gray
                
                platform_rect = pygame.Rect(screen_x, screen_y, platform.width, platform.height)
                pygame.draw.rect(screen, rock_color, platform_rect)
                
                # Add rock texture
                pygame.draw.line(screen, highlight_color,
                               (screen_x, screen_y),
                               (screen_x + platform.width, screen_y), 2)
    
    def render_snow_texture(self, screen, snow_rect, camera_offset):
        """
        Render animated snow texture on the main platform
        
        Args:
            screen: Pygame surface to render to
            snow_rect: Rectangle area to render snow in
            camera_offset: Camera position offset
        """
        
        # Render a solid layer of snow
        snow_color = (255, 255, 255)
        pygame.draw.rect(screen, snow_color, snow_rect)
    
    def render_platform_shadow(self, screen, platform, camera_offset):
        """
        Render natural shadows beneath platforms
        
        Args:
            screen: Pygame surface to render to
            platform: Platform object to render shadow for
            camera_offset: Camera position offset
        """
        
        # Calculate shadow position based on lighting angle
        shadow_offset_x = 8   # Horizontal offset based on sun angle
        shadow_offset_y = 12  # Vertical offset
        
        screen_x = platform.x - camera_offset[0] + shadow_offset_x
        screen_y = platform.y - camera_offset[1] + shadow_offset_y
        
        # Shadow opacity based on lighting intensity
        shadow_opacity = int(80 * (1.0 - getattr(self, 'current_lighting_intensity', 0.9)))
        
        # Create shadow surface
        shadow_surface = pygame.Surface((platform.width, platform.height), pygame.SRCALPHA)
        shadow_color = (0, 0, 0, shadow_opacity)
        pygame.draw.rect(shadow_surface, shadow_color, (0, 0, platform.width, platform.height))
        
        screen.blit(shadow_surface, (screen_x, screen_y))
    
    def get_stage_info(self):
        """
        Get comprehensive information about the Snowdin stage
        
        Returns:
            dict: Complete stage information including unique features and mechanics
        """
        
        base_info = super().get_stage_info()
        
        plains_info = {
            # === BASIC INFORMATION ===
            "description": self.description,
            "theme": self.theme,
            "music_track": self.music_track,
            "difficulty_rating": self.difficulty_rating,
            
            # === COMPETITIVE INFORMATION ===
            "competitive_legal": self.competitive_legal,
            "tournament_approved": True,
            "skill_level": "Intermediate to Advanced",
            "character_advantages": "Balanced with multiple levels for combat",
            
            # === LAYOUT INFORMATION ===
            "platform_layout": "Castle with multiple platforms",
            "platform_count": len(self.platforms),
            "main_platform_width": self.platform_distances['main_width'],
            "has_ledges": True,
            "has_hazards": False,
            "symmetrical": True,
            
            # === UNIQUE MECHANICS ===
            "gravity_multiplier": self.gravity_multiplier,
            "air_friction_modifier": self.air_friction_modifier,
            "terminal_velocity": self.terminal_velocity_cap,
            "surface_friction": self.surface_friction,
            "wind_effects": self.weather_enabled,
            
            # === VISUAL FEATURES ===
            "natural_theme": False,
            "weather_system": self.weather_enabled,
            "terrain_variation": True,
            "grass_animation": False,
            "mountain_parallax": False,
            
            # === GAMEPLAY DIFFERENCES ===
            "compared_to_battlefield": {
                "wider_main_platform": f"+{self.platform_distances['main_width'] - 800}px",
                "stronger_gravity": f"+{(self.gravity_multiplier - 1.0) * 100:.0f}%",
                "more_air_friction": f"+{(self.air_friction_modifier - 1.0) * 100:.0f}%",
                "fewer_platforms": f"{len(self.platforms)} vs 4",
                "wider_blast_zones": f"+{self.blast_zone_info['width_advantage']}px"
            },
            
            # === RECOMMENDATIONS ===
            "recommended_for": [
                "Vertical and horizontal combat",
                "Platforming skills",
                "Controlling space",
                "Defensive and offensive play"
            ],
            
            "strategies": [
                "Use platforms for mixups and escapes",
                "Control center stage to apply pressure",
                "Utilize walls for defense",
                "Master movement between levels"
            ],
            
            "character_types": {
                "excellent": ["All-rounders", "Characters with strong aerials"],
                "good": ["Zoners", "Rushdown characters"],
                "challenging": ["Characters with poor vertical recovery"]
            }
        }
        
        base_info.update(plains_info)
        return base_info 