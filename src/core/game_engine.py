"""
Game Engine - Core game management system
==========================================

This module contains the main GameEngine class that coordinates all game systems.
The engine handles the main game loop, system updates, and overall game state.

Key Features:
- Fixed timestep physics for consistent gameplay
- State management integration
- System coordination (physics, graphics, audio, input)
- Performance monitoring and optimization
"""

import pygame
import time
from src.core.state_manager import StateManager, GameStateType
from src.input.input_manager import InputManager
from src.physics.physics_manager import PhysicsManager

class GameEngine:
    """
    Main game engine that coordinates all game systems
    """
    
    def __init__(self):
        """
        Initialize the game engine with all subsystems
        """
        # Core systems
        self.input_manager = InputManager()
        self.physics_manager = PhysicsManager()
        self.state_manager = None  # Will be set by main.py
        
        # Timing and performance
        self.target_fps = 60
        self.fixed_timestep = 1.0 / 60.0  # 60 FPS fixed timestep
        self.accumulator = 0.0
        self.current_time = time.time()
        
        # Debug information
        self.debug_mode = False
        self.frame_count = 0
        self.fps_counter = 0
        self.last_fps_time = time.time()
        
        # Screen dimensions (will be set during initialization)
        self.screen_width = 1280
        self.screen_height = 720
    
    def initialize(self):
        """
        Initialize all game systems
        """
        # Initialize pygame subsystems
        pygame.mixer.init()  # Audio system
        pygame.font.init()   # Font system
        
        # Initialize input system
        self.input_manager.update()
        
        print("Game Engine initialized successfully")
        
    def set_state_manager(self, state_manager):
        """
        Set the state manager (called from main.py)
        """
        self.state_manager = state_manager
        
    def update(self, delta_time):
        """
        Update all game systems with fixed timestep
        """
        # Update input system
        self.input_manager.update()
        
        # Fixed timestep update for consistent physics
        self.accumulator += delta_time
        
        while self.accumulator >= self.fixed_timestep:
            # Update state manager with fixed timestep
            if self.state_manager:
                self.state_manager.update(self.fixed_timestep)
            
            # Update physics with fixed timestep
            # Physics manager update will be called by gameplay state
            
            self.accumulator -= self.fixed_timestep
        
        # Update FPS counter
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.last_fps_time >= 1.0:
            self.fps_counter = self.frame_count
            self.frame_count = 0
            self.last_fps_time = current_time
    
    def render(self, screen):
        """
        Render all game systems
        """
        if self.state_manager:
            self.state_manager.render(screen)
        
        # Render debug information if enabled
        if self.debug_mode:
            self.render_debug_info(screen)
    
    def handle_event(self, event):
        """
        Handle pygame events
        """
        # Pass events to input manager
        self.input_manager.handle_event(event)
        
        # Handle debug toggle
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F3:
                self.debug_mode = not self.debug_mode
        
        # Pass events to state manager
        if self.state_manager:
            self.state_manager.handle_event(event)
    
    def render_debug_info(self, screen):
        """
        Render debug information overlay
        """
        font = pygame.font.Font(None, 24)
        
        # FPS display
        fps_text = font.render(f"FPS: {self.fps_counter}", True, (255, 255, 0))
        screen.blit(fps_text, (10, 10))
        
        # Current state display
        if self.state_manager and self.state_manager.current_state:
            state_text = font.render(f"State: {self.state_manager.current_state_type.value}", True, (255, 255, 0))
            screen.blit(state_text, (10, 35))
        
        # Input display for both players
        if hasattr(self.state_manager, 'current_state') and hasattr(self.state_manager.current_state, 'characters'):
            y_offset = 60
            for i in range(2):
                player_id = i + 1
                input_str = self.input_manager.get_input_display_string(player_id)
                input_text = font.render(f"P{player_id}: {input_str}", True, (255, 255, 0))
                screen.blit(input_text, (10, y_offset))
                y_offset += 25
    
    def get_input_manager(self):
        """
        Get the input manager instance
        """
        return self.input_manager
    
    def get_physics_manager(self):
        """
        Get the physics manager instance
        """
        return self.physics_manager
    
    def shutdown(self):
        """
        Clean shutdown of all game systems
        """
        # Clean up pygame systems
        pygame.mixer.quit()
        pygame.quit()
        
        print("Game Engine shutdown complete") 