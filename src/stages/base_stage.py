"""
Base Stage - Foundation for all battle arenas
==============================================

This module contains the base Stage class that all battle arenas inherit from.
Defines common properties like platforms, boundaries, and hazards.

TODO:
- Implement collision detection with platforms and boundaries
- Add dynamic camera system that follows action
- Create parallax background system
- Add stage hazards and interactive elements
- Implement ledge mechanics for recovery
- Add visual effects and atmosphere

Stage Components:
- Main platform (ground level)
- Additional platforms (for vertical gameplay)
- Blast zones (KO boundaries)
- Background layers (parallax scrolling)
- Stage hazards (optional)
- Spawn points for players
"""

import pygame
import numpy as np
from enum import Enum

class PlatformType(Enum):
    """
    Types of platforms available in stages
    
    TODO: Expand as needed for different platform behaviors
    """
    SOLID = "solid"           # Cannot pass through
    PASS_THROUGH = "pass_through"  # Can drop through by pressing down
    MOVING = "moving"         # Platforms that move
    BREAKABLE = "breakable"   # Can be destroyed
    TEMPORARY = "temporary"   # Disappears after time

class Platform:
    """
    Individual platform within a stage
    
    TODO: Implement platform collision and behaviors
    """
    
    def __init__(self, x, y, width, height, platform_type=PlatformType.SOLID):
        """
        Initialize a platform
        
        TODO:
        - Set position and dimensions
        - Define collision boundaries
        - Set platform-specific properties
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.platform_type = platform_type
        
        # Movement properties (for moving platforms)
        self.velocity = np.array([0.0, 0.0])
        self.movement_pattern = None
        
        # State properties
        self.is_active = True
        self.health = 100 if platform_type == PlatformType.BREAKABLE else -1
    
    def update(self, delta_time):
        """
        Update platform logic
        
        Args:
            delta_time (float): Time in seconds since last update
        """
        # For now, platforms are static
        # This method will be expanded for moving platforms, breakable platforms, etc.
        pass
    
    def get_rect(self):
        """
        Returns a pygame.Rect object representing the platform's boundaries.
        """
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_collision_rect(self):
        """
        Get collision rectangle for this platform
        
        Returns:
            pygame.Rect: Rectangle representing the platform's collision area
        """
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def render(self, screen, camera_offset):
        """
        Render the platform
        
        TODO:
        - Draw platform sprite or colored rectangle
        - Apply camera offset for scrolling
        - Show visual effects for special platforms
        """
        pass

class Stage:
    """
    Base class for all battle stages
    
    TODO: Implement core stage functionality
    """
    
    def __init__(self, name, width, height):
        """
        Initialize a stage
        
        TODO:
        - Set stage dimensions and boundaries
        - Initialize platform list
        - Set up background layers
        - Define spawn points and camera bounds
        """
        self.name = name
        self.width = width
        self.height = height
        
        # Stage boundaries (blast zones)
        self.left_blast_zone = -200
        self.right_blast_zone = width + 200
        self.top_blast_zone = -200
        self.bottom_blast_zone = height + 200
        
        # Platforms and collision
        self.platforms = []
        self.main_platform = None
        
        # Spawn points for players
        self.spawn_points = []
        
        # Camera and visuals
        self.camera_bounds = pygame.Rect(0, 0, width, height)
        self.background_layers = []
        
        # Stage-specific properties
        self.has_hazards = False
        self.hazards = []
        self.ambient_effects = []
    
    def add_platform(self, platform):
        """
        Add a platform to the stage
        
        TODO:
        - Add platform to platforms list
        - Validate platform placement
        - Sort platforms for efficient collision detection
        """
        pass
    
    def add_spawn_point(self, x, y):
        """
        Add a spawn point for players
        
        Args:
            x (float): X coordinate of spawn point
            y (float): Y coordinate of spawn point
        """
        self.spawn_points.append((x, y))
        print(f"✓ Added spawn point at ({x}, {y})")
    
    def check_collision(self, character_rect, character_velocity):
        """
        Check collision between character and stage elements
        
        TODO:
        - Test collision with all platforms
        - Handle different collision types (top-only, full)
        - Return collision information (normal, platform type)
        - Handle ledge detection for recovery mechanics
        """
        pass
    
    def check_blast_zones(self, character_position):
        """
        Check if character is in a blast zone (KO zone)
        
        TODO:
        - Test if character is outside stage boundaries
        - Return which blast zone was hit (left, right, top, bottom)
        - Used for determining KOs
        """
        pass
    
    def update(self, delta_time):
        """
        Update stage logic
        
        TODO:
        - Update moving platforms
        - Update stage hazards
        - Update ambient effects
        - Handle any stage-specific mechanics
        """
        pass
    
    def render_background(self, screen, camera_offset):
        """
        Render background layers with parallax scrolling
        
        TODO:
        - Render background layers at different scroll speeds
        - Apply parallax effect based on camera position
        - Handle background animation
        """
        pass
    
    def render_platforms(self, screen, camera_offset):
        """
        Render all platforms in the stage
        
        TODO:
        - Render platforms in proper order
        - Apply camera offset for scrolling
        - Show platform-specific visual effects
        """
        pass
    
    def render_foreground(self, screen, camera_offset):
        """
        Render foreground elements (in front of characters)
        
        TODO:
        - Render foreground decorations
        - Apply lighting effects
        - Show weather or atmospheric effects
        """
        pass
    
    def get_stage_info(self):
        """
        Get stage information for UI display
        
        TODO:
        - Return dict with stage properties
        - Include stage name, size, hazards info
        - Platform count and types
        """
        return {
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "platform_count": len(self.platforms),
            "has_hazards": self.has_hazards,
            "spawn_points": len(self.spawn_points)
        } 