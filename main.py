"""
Brawl Bros Game - Main Entry Point
========================================


Main entry point for the game. This file handles:
- Game initialization with pygame setup
- Main game loop with fixed timestep physics
- State management coordination
- Event handling and input processing
- Proper FPS control and performance monitoring
"""

import pygame
import sys
from src.core.game_engine import GameEngine
from src.core.state_manager import StateManager

def main():
    """
    Main function to initialize and run the game
    """
    print("Starting Super Scuffed Fighters...")
    
    # Initialize pygame
    pygame.init()
    
    # Set up display window
    screen = pygame.display.set_mode(
        (1280, 720),  # Fixed 720p resolution for consistent gameplay
        pygame.SCALED
    )
    pygame.display.set_caption("Super Scuffed Fighters")
    
    # Create game engine and initialize all systems
    game_engine = GameEngine()
    game_engine.initialize()
    
    # Create state manager (this will set up the initial game state)
    state_manager = StateManager(game_engine)
    
    # Set up clock for FPS control
    clock = pygame.time.Clock()
    target_fps = 60
    
    print("Game initialized successfully!")
    print("Controls:")
    print("Player 1: Left Joy-Con (Sideways) or WASD.")
    print("  - Joy-Con: Stick to move, 'Down' D-Pad button for attack.")
    print("  - Keyboard: WASD to move, LSHIFT for attack.")
    print("Player 2: Xbox Controller or Keyboard.")
    print("  - Controller: Left Stick to move, 'A' button for attack.")
    print("  - Keyboard: PL;' to move, RSHIFT for attack.")
    print("---")
    print("F3=Debug Mode, R=Reset Match, ESC=Menu")
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Pass events to game engine (which forwards to current state)
            game_engine.handle_event(event)
        
        # Calculate delta time for smooth animations
        delta_time = clock.tick(target_fps) / 1000.0  # Convert to seconds
        
        # Update game engine (uses fixed timestep internally)
        game_engine.update(delta_time)
        
        # Clear screen and render
        screen.fill((0, 0, 0))  # Clear with black
        game_engine.render(screen)
        
        # Present the frame
        pygame.display.flip()
    
    # Clean shutdown
    print("Shutting down...")
    game_engine.shutdown()
    pygame.quit()
    sys.exit()

main()
