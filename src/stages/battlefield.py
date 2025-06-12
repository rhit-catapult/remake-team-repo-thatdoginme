"""
Battlefield Stage - Premier Competitive Fighting Arena
======================================================

The Battlefield stage is the gold standard for competitive platform fighting games.
It features a carefully balanced layout designed to provide equal opportunities
for all character types while maintaining competitive integrity.

Stage Design Philosophy:
========================
- Symmetrical layout ensures fairness for both players
- Multiple platform heights create vertical gameplay options
- No hazards or gimmicks keep focus on pure skill
- Balanced spacing accommodates different character archetypes
- Ledge mechanics provide recovery options without being overpowered

Platform Layout Details:
=======================
- Main Platform: Wide, stable ground level for neutral game
- Side Platforms: Medium height, enables platform tech-chasing
- Top Platform: Highest level, creates escape options and aerial mixups
- All platforms use pass-through mechanics for dynamic movement

Gravity Mechanics:
=================
This stage implements standard gravity that affects:
- Character fall speed and air control
- Knockback trajectories and combo potential  
- Recovery difficulty and edge-guarding options
- Platform drop-through mechanics
- Landing lag calculations

Visual Theme:
============
- Sky arena floating in endless blue atmosphere
- Clean, minimalist aesthetic focuses attention on gameplay
- Subtle parallax backgrounds provide depth without distraction
- Soft lighting creates pleasant competitive environment
"""

from .base_stage import Stage, Platform, PlatformType
import pygame
import numpy as np
import math

class Battlefield(Stage):
    """
    Battlefield Stage Implementation
    
    This class creates the definitive competitive platform fighter stage.
    Every measurement and positioning has been carefully calculated to
    provide the most balanced fighting experience possible.
    """
    
    def __init__(self):
        """
        Initialize the Battlefield stage with precise measurements
        
        Stage Dimensions:
        - Width: 1200 pixels (provides good camera bounds)
        - Height: 800 pixels (allows vertical gameplay without cramping)
        
        These dimensions create a 3:2 aspect ratio that works well
        for both gameplay mechanics and visual composition.
        """
        # Call parent constructor with carefully chosen dimensions
        super().__init__("Battlefield", 1200, 800)
        
        # === STAGE METADATA ===
        # These properties describe the stage for UI and selection
        self.description = "The ultimate test of skill - symmetrical platforms, no gimmicks"
        self.theme = "Floating Sky Arena"
        self.music_track = "battlefield_anthem.ogg"
        self.competitive_legal = True  # Approved for tournament play
        self.difficulty_rating = "Beginner Friendly"  # Good for learning fundamentals
        
        # === GRAVITY SETTINGS ===
        # These values fine-tune how gravity affects gameplay on this stage
        self.gravity_multiplier = 1.0      # Standard gravity (1.0 = normal)
        self.air_friction_modifier = 1.0   # Standard air resistance
        self.terminal_velocity_cap = 18.0  # Prevents infinitely fast falling
        self.platform_magnetism = 0.8      # How "sticky" platforms feel when landing
        
        # === STAGE PHYSICS PROPERTIES ===
        # These affect how the stage interacts with character physics
        self.wind_resistance = 0.0         # No wind effects (competitive purity)
        self.surface_friction = 0.15       # Ground friction for running/stopping
        self.ledge_grab_distance = 25      # How far from edge you can grab ledges
        self.platform_drop_frames = 8     # Frames needed to drop through platforms
        
        # === VISUAL EFFECTS SETTINGS ===
        # Control various atmospheric and visual elements
        self.enable_parallax = True        # Background scrolling effect
        self.cloud_animation_speed = 0.5   # How fast clouds move
        self.ambient_particle_count = 15   # Floating particles in background
        self.lighting_intensity = 0.8      # Brightness of stage lighting
        
        # Initialize all stage components
        self.setup_platforms()     # Create the platform layout
        self.setup_spawn_points()  # Define where players start
        self.setup_blast_zones()   # Set KO boundaries  
        self.setup_visuals()       # Initialize graphics and effects
        self.setup_camera_bounds() # Define camera movement limits
        
        try:
            self.background_image = pygame.image.load('assets/images/battlefield bg.png').convert()
        except pygame.error:
            self.background_image = None
            print("Warning: Could not load battlefield bg.png. Using procedural background.")

        print(f"✓ Battlefield stage initialized with {len(self.platforms)} platforms")
    
    def setup_platforms(self):
        """
        Create the iconic Battlefield platform layout
        
        Platform Design Principles:
        ===========================
        1. Main platform provides stable neutral game space
        2. Side platforms create escape routes and tech-chase opportunities  
        3. Top platform offers high-ground advantage and aerial mixups
        4. All spacing calculated for optimal character movement
        
        Measurements are based on character sizes and movement speeds
        to ensure balanced gameplay across all character archetypes.
        """
        
        # === MAIN PLATFORM (Ground Level) ===
        # This is the primary fighting surface where most neutral game occurs
        main_platform_width = 800   # Wide enough for spacing but not camping
        main_platform_height = 40   # Thick enough to feel solid
        main_platform_x = (self.width - main_platform_width) // 2  # Center horizontally
        main_platform_y = self.height - 120  # Leave room for characters below
        
        self.main_platform = Platform(
            x=main_platform_x,
            y=main_platform_y, 
            width=main_platform_width,
            height=main_platform_height,
            platform_type=PlatformType.SOLID  # Cannot pass through from any direction
        )
        
        # Add special properties for the main platform
        self.main_platform.has_ledges = True      # Enable ledge-grabbing
        self.main_platform.surface_grip = 1.0     # Full traction for running
        self.main_platform.is_main_stage = True   # Marks as primary platform
        
        self.platforms.append(self.main_platform)
        print(f"✓ Main platform created: {main_platform_width}x{main_platform_height} at ({main_platform_x}, {main_platform_y})")
        
        # === SIDE PLATFORMS (Medium Height) ===
        # These platforms create the signature triangle formation
        # Positioned to allow platform tech-chasing and escape options
        
        side_platform_width = 180    # Smaller than main for tactical positioning
        side_platform_height = 20    # Thinner since they're pass-through
        side_platform_y = main_platform_y - 120  # Lowered significantly for easier access
        
        # Left side platform
        left_platform_x = main_platform_x + 50  # Slight inset from main platform edge
        left_platform = Platform(
            x=left_platform_x,
            y=side_platform_y,
            width=side_platform_width, 
            height=side_platform_height,
            platform_type=PlatformType.PASS_THROUGH  # Can drop through by holding down
        )
        
        # Add platform-specific properties
        left_platform.drop_through_enabled = True   # Allow dropping through
        left_platform.has_ledges = True            # Enable ledge mechanics
        left_platform.platform_id = "left_side"    # For debugging/tracking
        
        self.platforms.append(left_platform)
        
        # Right side platform (mirror of left)
        right_platform_x = main_platform_x + main_platform_width - side_platform_width - 50
        right_platform = Platform(
            x=right_platform_x,
            y=side_platform_y,
            width=side_platform_width,
            height=side_platform_height, 
            platform_type=PlatformType.PASS_THROUGH
        )
        
        # Mirror properties from left platform
        right_platform.drop_through_enabled = True
        right_platform.has_ledges = True
        right_platform.platform_id = "right_side"
        
        self.platforms.append(right_platform)
        
        print(f"✓ Side platforms created at height {side_platform_y}")
        
        # === TOP PLATFORM (Highest Level) ===
        # The apex of the triangle formation
        # Creates aerial mixup opportunities and high-ground advantages
        
        top_platform_width = 160     # Smallest platform for precise positioning
        top_platform_height = 20     # Same thickness as side platforms
        top_platform_x = (self.width - top_platform_width) // 2  # Perfect center
        top_platform_y = side_platform_y - 110  # Lowered significantly for easier access
        
        top_platform = Platform(
            x=top_platform_x,
            y=top_platform_y,
            width=top_platform_width,
            height=top_platform_height,
            platform_type=PlatformType.PASS_THROUGH
        )
        
        # Top platform gets special properties for aerial gameplay
        top_platform.drop_through_enabled = True
        top_platform.has_ledges = True
        top_platform.aerial_advantage = True      # Marks as high-ground position
        top_platform.platform_id = "top_center"
        
        self.platforms.append(top_platform)
        
        print(f"✓ Top platform created at height {top_platform_y}")
        print(f"✓ All platforms positioned in balanced triangle formation")
        
        # === PLATFORM RELATIONSHIP CALCULATIONS ===
        # Store useful measurements for gameplay systems
        self.platform_heights = {
            'main': main_platform_y,
            'side': side_platform_y, 
            'top': top_platform_y
        }
        
        # Calculate distances between platforms for AI and combo systems
        self.platform_distances = {
            'main_to_side': side_platform_y - main_platform_y,  # Vertical gap
            'side_to_top': top_platform_y - side_platform_y,    # Vertical gap  
            'side_to_side': right_platform_x - (left_platform_x + side_platform_width)  # Horizontal gap
        }
    
    def setup_spawn_points(self):
        """
        Define where players spawn at match start
        
        Spawn Point Philosophy:
        ======================
        - Equal distance from stage center ensures fairness
        - Positioned on main platform for immediate ground access
        - Facing toward center creates natural engagement
        - Safe distance prevents accidental early interactions
        """
        
        # Calculate spawn positions based on main platform
        main_platform_center = self.main_platform.x + (self.main_platform.width // 2)
        spawn_distance_from_center = 250  # Distance each player spawns from center
        spawn_height_offset = -50         # Height above main platform surface
        
        # Player 1 spawn point (left side)
        player1_spawn_x = main_platform_center - spawn_distance_from_center
        player1_spawn_y = self.main_platform.y + spawn_height_offset
        
        self.add_spawn_point(player1_spawn_x, player1_spawn_y)
        
        # Player 2 spawn point (right side) 
        player2_spawn_x = main_platform_center + spawn_distance_from_center
        player2_spawn_y = self.main_platform.y + spawn_height_offset
        
        self.add_spawn_point(player2_spawn_x, player2_spawn_y)
        
        print(f"✓ Spawn points set at distance {spawn_distance_from_center} from center")
        
        # Store spawn information for respawning and camera setup
        self.spawn_info = {
            'center_x': main_platform_center,
            'center_y': player1_spawn_y,
            'distance': spawn_distance_from_center,
            'facing_inward': True  # Players start facing each other
        }
    
    def setup_blast_zones(self):
        """
        Define the KO boundaries around the stage
        
        Blast Zone Design:
        =================
        - Left/Right: Close enough for horizontal KOs but allows recovery
        - Top: High enough to prevent early vertical KOs  
        - Bottom: Low enough for spike/meteor KOs but recoverable
        
        These distances are calibrated for balanced competitive play.
        """
        
        # Horizontal blast zones (left and right KO boundaries)
        horizontal_distance = 280  # Distance from stage edge to blast zone
        self.left_blast_zone = -horizontal_distance
        self.right_blast_zone = self.width + horizontal_distance
        
        # Vertical blast zones (top and bottom KO boundaries)
        top_distance = 250        # Distance above stage to ceiling blast zone
        bottom_distance = 350     # Distance below stage to bottom blast zone
        
        self.top_blast_zone = -top_distance  
        self.bottom_blast_zone = self.height + bottom_distance
        
        print(f"✓ Blast zones set: X±{horizontal_distance}, Y+{top_distance}/-{bottom_distance}")
        
        # Store blast zone info for gameplay systems
        self.blast_zone_info = {
            'horizontal_distance': horizontal_distance,
            'top_distance': top_distance,
            'bottom_distance': bottom_distance,
            'total_width': self.right_blast_zone - self.left_blast_zone,
            'total_height': self.bottom_blast_zone - self.top_blast_zone
        }
    
    def setup_camera_bounds(self):
        """
        Define how the camera should move to follow the action
        
        Camera System:
        =============
        - Follows both players while keeping stage in view
        - Zooms smoothly to frame the action appropriately
        - Prevents showing empty space or off-stage areas
        - Maintains smooth movement for spectator experience
        """
        
        # Camera movement bounds (where camera center can go)
        camera_margin = 100  # Padding from stage edges
        
        self.camera_bounds = pygame.Rect(
            camera_margin,                    # Left bound
            camera_margin,                    # Top bound  
            self.width - (camera_margin * 2), # Width
            self.height - (camera_margin * 2) # Height
        )
        
        # Camera zoom limits
        self.min_camera_zoom = 0.7   # Zoomed out (shows more stage)
        self.max_camera_zoom = 1.3   # Zoomed in (focuses on action)
        self.default_camera_zoom = 1.0  # Standard zoom level
        
        # Camera movement smoothing
        self.camera_follow_speed = 0.05    # How quickly camera follows players
        self.camera_zoom_speed = 0.03      # How quickly camera zooms
        
        print(f"✓ Camera bounds set with {camera_margin}px margins")
    
    def setup_visuals(self):
        """
        Initialize all visual elements and atmospheric effects
        
        Visual Design Goals:
        ===================
        - Clean, uncluttered aesthetic keeps focus on gameplay
        - Subtle parallax creates depth without distraction  
        - Soft color palette is easy on eyes during long sessions
        - Minimal effects prevent performance issues
        """
        
        # === BACKGROUND LAYERS ===
        # Multiple layers create depth through parallax scrolling
        self.background_layers = [
            {
                "name": "sky_gradient",           # Base sky color
                "type": "gradient",
                "colors": [(135, 206, 235), (176, 224, 230)],  # Light blue gradient
                "scroll_speed": 0.0,              # Static background
                "opacity": 255
            },
            {
                "name": "far_clouds",             # Distant cloud layer
                "type": "clouds",
                "scroll_speed": 0.1,              # Very slow movement
                "cloud_count": 8,
                "cloud_size_range": (80, 120),
                "opacity": 60,                    # Very faint
                "color": (255, 255, 255)
            },
            {
                "name": "mid_clouds",             # Medium distance clouds
                "type": "clouds", 
                "scroll_speed": 0.2,              # Moderate movement
                "cloud_count": 5,
                "cloud_size_range": (100, 160),
                "opacity": 80,                    # Slightly more visible
                "color": (250, 250, 255)
            },
            {
                "name": "near_clouds",            # Closest cloud layer
                "type": "clouds",
                "scroll_speed": 0.4,              # Faster movement
                "cloud_count": 3,
                "cloud_size_range": (120, 200),
                "opacity": 40,                    # Semi-transparent
                "color": (245, 245, 255)
            }
        ]
        
        # === PARTICLE EFFECTS ===
        # Subtle atmospheric particles floating in the background
        self.particle_system = {
            "enabled": True,
            "max_particles": self.ambient_particle_count,
            "spawn_rate": 0.1,                # Particles per frame
            "particle_types": [
                {
                    "type": "dust_mote",
                    "size_range": (1, 3),
                    "color": (255, 255, 255, 30),  # Very faint white
                    "speed_range": (0.1, 0.5),
                    "lifetime_range": (300, 600)   # Frames before despawning
                },
                {
                    "type": "light_sparkle", 
                    "size_range": (2, 4),
                    "color": (255, 255, 200, 50),  # Faint yellow
                    "speed_range": (0.2, 0.8),
                    "lifetime_range": (180, 360)
                }
            ]
        }
        
        # === LIGHTING SYSTEM ===
        # Soft lighting that enhances visibility without being distracting
        self.lighting = {
            "ambient_light": {
                "color": (255, 255, 240),        # Warm white
                "intensity": self.lighting_intensity,
                "direction": "omnidirectional"
            },
            "sun_light": {
                "color": (255, 250, 200),        # Sunny yellow
                "intensity": 0.6,
                "angle": 45,                     # Degrees from horizontal
                "creates_shadows": False         # Disabled for clean look
            }
        }
        
        # === PLATFORM VISUAL PROPERTIES ===
        # Define how each platform type should look
        self.platform_visuals = {
            "main_platform": {
                "color": (101, 67, 33),          # Rich brown
                "edge_color": (80, 50, 20),      # Darker brown edges
                "texture": "stone_blocks",        # Visual texture identifier
                "has_grass": True,               # Green top surface
                "shadow_opacity": 120
            },
            "floating_platforms": {
                "color": (139, 139, 139),        # Medium gray
                "edge_color": (100, 100, 100),   # Darker gray edges
                "texture": "metal_grating",      # Sci-fi appearance
                "glow_intensity": 20,            # Subtle glow effect
                "shadow_opacity": 80
            }
        }
        
        # === BACKGROUND ANIMATION STATE ===
        # Track timing for animated elements
        self.animation_state = {
            "cloud_offset": 0.0,              # Current cloud scroll position
            "particle_spawn_timer": 0.0,     # When to spawn next particle
            "lighting_pulse_phase": 0.0,     # Subtle lighting animation
            "total_elapsed_time": 0.0        # For time-based effects
        }
        
        # Initialize total elapsed time for immediate use
        self.total_elapsed_time = 0.0
        
        print("✓ Visual system initialized with parallax backgrounds and particles")
    
    def update(self, delta_time):
        """
        Update all dynamic stage elements
        
        This method handles:
        - Background animation and parallax scrolling
        - Particle system updates
        - Platform state changes (if any)
        - Lighting and atmospheric effects
        
        Args:
            delta_time (float): Time in seconds since last update
        """
        
        # Call parent update for base functionality
        super().update(delta_time)
        
        # Track total elapsed time for effects
        self.animation_state["total_elapsed_time"] += delta_time
        
        # === UPDATE BACKGROUND ANIMATION ===
        # Move cloud layers based on their individual scroll speeds
        for layer in self.background_layers:
            if layer["type"] == "clouds":
                # Update cloud positions with smooth scrolling
                scroll_distance = layer["scroll_speed"] * self.cloud_animation_speed * delta_time
                self.animation_state["cloud_offset"] += scroll_distance
                
                # Wrap around when clouds move off-screen
                if self.animation_state["cloud_offset"] > self.width + 200:
                    self.animation_state["cloud_offset"] = -200
        
        # === UPDATE PARTICLE SYSTEM ===
        if self.particle_system["enabled"]:
            # Spawn new particles based on spawn rate
            self.animation_state["particle_spawn_timer"] += delta_time
            
            if self.animation_state["particle_spawn_timer"] >= self.particle_system["spawn_rate"]:
                # Reset timer and spawn particle (if under limit)
                self.animation_state["particle_spawn_timer"] = 0.0
                # TODO: Implement actual particle spawning when particle system is created
        
        # === UPDATE LIGHTING EFFECTS ===
        # Subtle pulsing of ambient light for atmosphere
        pulse_speed = 0.5  # Cycles per second
        self.animation_state["lighting_pulse_phase"] += delta_time * pulse_speed * 2 * math.pi
        
        # Keep phase in reasonable range
        if self.animation_state["lighting_pulse_phase"] > 2 * math.pi:
            self.animation_state["lighting_pulse_phase"] -= 2 * math.pi
        
        # Calculate current lighting intensity with subtle variation
        base_intensity = self.lighting_intensity
        pulse_variation = 0.05  # Small variation amount
        current_pulse = math.sin(self.animation_state["lighting_pulse_phase"]) * pulse_variation
        self.lighting["ambient_light"]["intensity"] = base_intensity + current_pulse
        
        # === UPDATE PLATFORM STATES ===
        # Update any dynamic platform properties
        for platform in self.platforms:
            # For now, platforms are static, but this is where moving platforms would update
            platform.update(delta_time)
    
    def apply_stage_gravity(self, character, delta_time):
        """
        Apply Battlefield-specific gravity effects to characters
        
        === BATTLEFIELD PHYSICS PHILOSOPHY ===
        Battlefield is designed as the "baseline" competitive stage with standard gravity.
        All physics values are balanced for competitive play:
        - Standard 1.0x gravity multiplier (no modifications)
        - Consistent platform physics across all areas
        - Predictable aerial behavior for combo consistency
        
        This stage serves as the reference point for balancing other stages.
        All custom stages should be compared against Battlefield's feel.
        
        Args:
            character: The character object to apply gravity to
            delta_time (float): Time in seconds since last frame
        """
        
        print(f"⚔️ Battlefield gravity for P{character.player_id}: on_ground={character.on_ground}, dt={delta_time:.3f}")
        
        # Get base gravity from physics manager
        base_gravity = 0.8  # Standard gravity value
        
        # Apply stage-specific gravity modifications
        stage_gravity = base_gravity * self.gravity_multiplier
        
        print(f"   Base gravity: {base_gravity}, multiplier: {self.gravity_multiplier}, stage gravity: {stage_gravity}")
        
        # === SPECIAL GRAVITY ZONES ===
        # Different areas of the stage can have slightly different gravity
        character_x = character.position[0]
        character_y = character.position[1]
        
        # Slightly reduced gravity near the top platform (encourages aerial play)
        if character_y < self.platform_heights['top'] + 50:
            aerial_gravity_reduction = 0.9  # 10% less gravity at high altitude
            stage_gravity *= aerial_gravity_reduction
            print(f"   🌟 High altitude gravity reduction: {stage_gravity}")
        
        # Standard gravity in main platform area
        elif character_y > self.platform_heights['side']:
            stage_gravity *= 1.0  # No modification
            print(f"   🏔️ Standard area gravity: {stage_gravity}")
        
        # === APPLY MODIFIED GRAVITY ===
        if not character.is_on_ground():
            print(f"   🌊 Applying gravity {stage_gravity} to airborne P{character.player_id}")
            old_vel_y = character.velocity[1]
            
            # Apply gravity acceleration
            character.velocity[1] += stage_gravity
            
            print(f"   📈 Velocity Y: {old_vel_y:.2f} -> {character.velocity[1]:.2f}")
            
            # Apply stage-specific air friction
            air_friction = 0.02 * self.air_friction_modifier
            old_vel_x = character.velocity[0]
            character.velocity[0] *= (1.0 - air_friction)
            
            print(f"   🌬️ Air friction {air_friction:.4f}: vel_x {old_vel_x:.2f} -> {character.velocity[0]:.2f}")
            
            # Enforce terminal velocity with stage modifications
            terminal_velocity = self.terminal_velocity_cap
            if character.velocity[1] > terminal_velocity:
                character.velocity[1] = terminal_velocity
                print(f"   🏁 Terminal velocity cap applied: {terminal_velocity}")
        else:
            print(f"   🏃 P{character.player_id} on ground - no gravity applied")
        
        # === PLATFORM MAGNETISM ===
        # Make platforms feel slightly "sticky" when landing for better control
        if character.is_on_ground() and hasattr(character, 'just_landed') and character.just_landed:
            old_vel_x = character.velocity[0]
            # Reduce horizontal momentum slightly when landing on platforms
            character.velocity[0] *= (1.0 - (self.platform_magnetism * 0.1))
            print(f"   🧲 Platform magnetism: vel_x {old_vel_x:.2f} -> {character.velocity[0]:.2f}")
    
    def render_background(self, screen, camera_offset):
        """
        Render the stage background with parallax scrolling effects
        
        This creates a sense of depth and atmosphere while keeping the
        visual focus on the gameplay elements.
        
        Args:
            screen: Pygame surface to render to
            camera_offset: (x, y) tuple of camera position offset
        """
        
        # === RENDER SKY GRADIENT ===
        # Create a smooth gradient from light blue to white
        if self.background_image:
            scaled_bg = pygame.transform.scale(self.background_image, screen.get_size())
            screen.blit(scaled_bg, (0, 0))
            return
            
        sky_layer = self.background_layers[0]
        
        if sky_layer["type"] == "gradient":
            # Create vertical gradient effect
            top_color = sky_layer["colors"][0]
            bottom_color = sky_layer["colors"][1]
            
            # Simple gradient fill (could be enhanced with actual gradient rendering)
            screen.fill(top_color)
            
            # Add subtle color variation across the screen
            gradient_overlay = pygame.Surface((screen.get_width(), screen.get_height()))
            gradient_overlay.fill(bottom_color)
            gradient_overlay.set_alpha(30)  # Very subtle
            screen.blit(gradient_overlay, (0, screen.get_height() // 2))
        
        # === RENDER CLOUD LAYERS ===
        # Each cloud layer moves at different speeds for parallax effect
        for layer in self.background_layers[1:]:  # Skip sky gradient
            if layer["type"] == "clouds":
                self.render_cloud_layer(screen, layer, camera_offset)
        
        # === RENDER ATMOSPHERIC PARTICLES ===
        if self.particle_system["enabled"]:
            self.render_particles(screen, camera_offset)
    
    def render_cloud_layer(self, screen, layer, camera_offset):
        """
        Render a single cloud layer with parallax scrolling
        
        Args:
            screen: Pygame surface to render to
            layer: Cloud layer configuration dictionary
            camera_offset: Camera position for parallax calculation
        """
        
        # Calculate parallax offset based on camera and layer scroll speed
        parallax_x = camera_offset[0] * layer["scroll_speed"]
        parallax_y = camera_offset[1] * layer["scroll_speed"] * 0.5  # Less vertical parallax
        
        # Add animation offset for cloud movement
        animation_offset = self.animation_state["cloud_offset"] * layer["scroll_speed"]
        
        # Calculate final cloud positions
        total_offset_x = parallax_x + animation_offset
        
        # Render clouds across the screen
        cloud_count = layer["cloud_count"]
        cloud_spacing = (screen.get_width() + 400) // cloud_count  # Extra spacing for wrap-around
        
        for i in range(cloud_count + 2):  # Extra clouds for seamless scrolling
            # Calculate cloud position
            cloud_x = (i * cloud_spacing) - 200 - total_offset_x
            cloud_y = 50 + (i * 30) % 100  # Varied height
            
            # Wrap clouds around screen
            while cloud_x > screen.get_width() + 200:
                cloud_x -= (cloud_count + 2) * cloud_spacing
            while cloud_x < -200:
                cloud_x += (cloud_count + 2) * cloud_spacing
            
            # Render cloud (simple ellipse for now, could be sprites)
            cloud_size = layer["cloud_size_range"][0] + (i * 10) % (layer["cloud_size_range"][1] - layer["cloud_size_range"][0])
            cloud_color = layer["color"]
            
            # Create cloud surface with alpha
            cloud_surface = pygame.Surface((cloud_size, cloud_size // 2), pygame.SRCALPHA)
            cloud_surface.fill((*cloud_color, layer["opacity"]))
            
            # Render cloud to screen
            screen.blit(cloud_surface, (cloud_x, cloud_y))
    
    def render_particles(self, screen, camera_offset):
        """
        Render atmospheric particles floating in the background
        
        Args:
            screen: Pygame surface to render to  
            camera_offset: Camera position for parallax calculation
        """
        # TODO: Implement particle rendering when particle system is fully created
        # For now, just render a few simple particles as placeholder
        
        particle_count = 5
        for i in range(particle_count):
            # Calculate particle position with slow parallax movement
            particle_x = (i * 200 + self.animation_state["total_elapsed_time"] * 10) % screen.get_width()
            particle_y = (i * 150 + math.sin(self.animation_state["total_elapsed_time"] + i) * 20) % screen.get_height()
            
            # Apply slight camera parallax  
            particle_x -= camera_offset[0] * 0.1
            particle_y -= camera_offset[1] * 0.1
            
            # Render small glowing dot
            particle_color = (255, 255, 255, 40)
            particle_size = 2
            
            # Create particle surface
            particle_surface = pygame.Surface((particle_size * 2, particle_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, particle_color, (particle_size, particle_size), particle_size)
            
            screen.blit(particle_surface, (particle_x, particle_y))
    
    def render_platforms(self, screen, camera_offset):
        """
        Render all platforms with enhanced visual styling
        
        This method renders platforms with proper texturing, shadows,
        and visual effects that enhance the competitive experience.
        
        Args:
            screen: Pygame surface to render to
            camera_offset: (x, y) tuple of camera position offset
        """
        
        # === RENDER PLATFORM SHADOWS FIRST ===
        # Shadows are rendered below platforms for depth
        for platform in self.platforms:
            self.render_platform_shadow(screen, platform, camera_offset)
        
        # === RENDER PLATFORMS WITH STYLING ===
        for platform in self.platforms:
            # Calculate screen position with camera offset
            screen_x = platform.x - camera_offset[0]
            screen_y = platform.y - camera_offset[1]
            
            # Determine platform visual style
            if platform == self.main_platform:
                visual_style = self.platform_visuals["main_platform"]
            else:
                visual_style = self.platform_visuals["floating_platforms"]
            
            # === RENDER PLATFORM BASE ===
            platform_rect = pygame.Rect(screen_x, screen_y, platform.width, platform.height)
            
            # Fill platform with base color
            pygame.draw.rect(screen, visual_style["color"], platform_rect)
            
            # Add edge highlights for 3D effect
            edge_color = visual_style["edge_color"]
            
            # Top edge (lighter)
            pygame.draw.line(screen, 
                           (min(255, visual_style["color"][0] + 40),
                            min(255, visual_style["color"][1] + 40), 
                            min(255, visual_style["color"][2] + 40)),
                           (screen_x, screen_y), 
                           (screen_x + platform.width, screen_y), 2)
            
            # Bottom and right edges (darker)
            pygame.draw.line(screen, edge_color,
                           (screen_x, screen_y + platform.height),
                           (screen_x + platform.width, screen_y + platform.height), 2)
            pygame.draw.line(screen, edge_color,
                           (screen_x + platform.width, screen_y),
                           (screen_x + platform.width, screen_y + platform.height), 2)
            
            # === ADD PLATFORM-SPECIFIC EFFECTS ===
            if platform == self.main_platform and visual_style.get("has_grass", False):
                # Add grass texture on top of main platform
                grass_color = (34, 139, 34)  # Forest green
                grass_rect = pygame.Rect(screen_x, screen_y - 3, platform.width, 3)
                pygame.draw.rect(screen, grass_color, grass_rect)
            
            elif platform != self.main_platform and visual_style.get("glow_intensity", 0) > 0:
                # Add subtle glow effect to floating platforms
                glow_intensity = visual_style["glow_intensity"]
                glow_color = (200, 200, 255, glow_intensity)
                
                # Create glow surface
                glow_surface = pygame.Surface((platform.width + 10, platform.height + 10), pygame.SRCALPHA)
                glow_rect = pygame.Rect(5, 5, platform.width, platform.height)
                pygame.draw.rect(glow_surface, glow_color, glow_rect)
                
                # Render glow behind platform
                screen.blit(glow_surface, (screen_x - 5, screen_y - 5))
            
            # === RENDER LEDGE INDICATORS ===
            # Show where players can grab ledges for recovery
            if hasattr(platform, 'has_ledges') and platform.has_ledges:
                ledge_color = (255, 255, 0, 100)  # Semi-transparent yellow
                ledge_size = 8
                
                # Left ledge
                left_ledge_surface = pygame.Surface((ledge_size, ledge_size), pygame.SRCALPHA)
                pygame.draw.circle(left_ledge_surface, ledge_color, 
                                 (ledge_size // 2, ledge_size // 2), ledge_size // 2)
                screen.blit(left_ledge_surface, (screen_x - ledge_size // 2, screen_y - ledge_size // 2))
                
                # Right ledge
                right_ledge_surface = pygame.Surface((ledge_size, ledge_size), pygame.SRCALPHA)
                pygame.draw.circle(right_ledge_surface, ledge_color,
                                 (ledge_size // 2, ledge_size // 2), ledge_size // 2) 
                screen.blit(right_ledge_surface, (screen_x + platform.width - ledge_size // 2, screen_y - ledge_size // 2))
    
    def render_platform_shadow(self, screen, platform, camera_offset):
        """
        Render shadow beneath a platform for visual depth
        
        Args:
            screen: Pygame surface to render to
            platform: Platform object to render shadow for
            camera_offset: Camera position offset
        """
        
        # Calculate shadow position
        shadow_offset_x = 5   # Slight horizontal offset
        shadow_offset_y = 8   # Vertical offset below platform
        
        screen_x = platform.x - camera_offset[0] + shadow_offset_x
        screen_y = platform.y - camera_offset[1] + shadow_offset_y
        
        # Determine shadow opacity based on platform type
        if platform == self.main_platform:
            shadow_opacity = self.platform_visuals["main_platform"]["shadow_opacity"]
        else:
            shadow_opacity = self.platform_visuals["floating_platforms"]["shadow_opacity"]
        
        # Create shadow surface
        shadow_surface = pygame.Surface((platform.width, platform.height), pygame.SRCALPHA)
        shadow_color = (0, 0, 0, shadow_opacity)
        pygame.draw.rect(shadow_surface, shadow_color, 
                        (0, 0, platform.width, platform.height))
        
        # Render shadow to screen
        screen.blit(shadow_surface, (screen_x, screen_y))
    
    def render_foreground(self, screen, camera_offset):
        """
        Render foreground elements that appear in front of characters
        
        Args:
            screen: Pygame surface to render to
            camera_offset: Camera position offset
        """
        
        # === RENDER LIGHTING EFFECTS ===
        # Subtle lighting overlay that enhances the atmosphere
        if self.lighting["ambient_light"]["intensity"] > 0:
            # Create light overlay surface
            light_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            
            # Calculate current light intensity (includes pulsing effect)
            current_intensity = int(self.lighting["ambient_light"]["intensity"] * 255)
            light_color = (*self.lighting["ambient_light"]["color"], max(0, min(255, current_intensity)))
            
            # Very subtle light overlay
            light_surface.fill(light_color)
            light_surface.set_alpha(10)  # Very faint
            
            screen.blit(light_surface, (0, 0))
        
        # === RENDER ATMOSPHERIC EFFECTS ===
        # Additional foreground particles or effects could go here
        # For now, keep minimal for competitive clarity
    
    def get_stage_info(self):
        """
        Get comprehensive information about the Battlefield stage
        
        Returns:
            dict: Complete stage information including layout, settings, and metadata
        """
        
        # Get base stage info from parent class
        base_info = super().get_stage_info()
        
        # Add Battlefield-specific information
        battlefield_info = {
            # === BASIC INFORMATION ===
            "description": self.description,
            "theme": self.theme,
            "music_track": self.music_track,
            "difficulty_rating": self.difficulty_rating,
            
            # === COMPETITIVE INFORMATION ===
            "competitive_legal": self.competitive_legal,
            "tournament_approved": True,
            "skill_level": "All levels",
            "character_advantages": "Balanced for all archetypes",
            
            # === LAYOUT INFORMATION ===
            "platform_layout": "Classic triangle formation",
            "platform_count": len(self.platforms),
            "has_ledges": True,
            "has_hazards": False,
            "symmetrical": True,
            
            # === TECHNICAL INFORMATION ===
            "gravity_multiplier": self.gravity_multiplier,
            "air_friction_modifier": self.air_friction_modifier,
            "terminal_velocity": self.terminal_velocity_cap,
            "surface_friction": self.surface_friction,
            
            # === VISUAL INFORMATION ===
            "parallax_backgrounds": self.enable_parallax,
            "particle_effects": self.particle_system["enabled"],
            "lighting_effects": True,
            "atmosphere": "Floating sky arena",
            
            # === GAMEPLAY METRICS ===
            "blast_zone_distances": self.blast_zone_info,
            "platform_distances": self.platform_distances,
            "spawn_point_count": len(self.spawn_points),
            
            # === RECOMMENDATIONS ===
            "recommended_for": [
                "Tournament play",
                "Skill development", 
                "All character types",
                "Learning fundamentals",
                "Competitive practice"
            ],
            
            "strategies": [
                "Control center stage for neutral game advantage",
                "Use platforms for escape routes and mixups",
                "Practice ledge-guarding from side platforms",
                "Utilize top platform for aerial advantage",
                "Master platform drop-through techniques"
            ]
        }
        
        # Merge base info with battlefield-specific info
        base_info.update(battlefield_info)
        
        return base_info 