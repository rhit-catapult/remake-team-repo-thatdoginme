"""
State Manager - Game State Management System
=============================================

Manages different game states (Menu, Character Select, Gameplay, Pause, etc.)
Uses the State pattern to handle transitions and state-specific logic.

Features:
- Clean state transitions with proper initialization/cleanup
- State stack for pause/resume functionality  
- State-specific input processing and rendering
- Automatic state management for different game phases
"""

import pygame
from enum import Enum
from src.characters.warrior import Warrior
from src.characters.speedster import Speedster
from src.characters.heavy import Heavy
import os
import random

class GameStateType(Enum):
    """
    Enumeration of all possible game states
    """
    MAIN_MENU = "main_menu"
    CHARACTER_SELECT = "character_select"
    STAGE_SELECT = "stage_select"
    VERSUS_SCREEN = "versus_screen"
    GAMEPLAY = "gameplay"
    WIN_SCREEN = "win_screen"
    PAUSE = "pause"
    RESULTS = "results"
    OPTIONS = "options"

class GameState:
    """
    Base class for all game states
    """
    
    def __init__(self, state_manager):
        """
        Initialize the game state
        """
        self.state_manager = state_manager
        self.game_engine = state_manager.game_engine
    
    def enter(self):
        """
        Called when entering this state
        """
        pass
    
    def exit(self):
        """
        Called when leaving this state
        """
        pass
    
    def handle_event(self, event):
        """
        Handle pygame events for this state
        """
        return False
    
    def update(self, delta_time):
        """
        Update state logic
        """
        pass
    
    def render(self, screen):
        """
        Render this state to the screen
        """
        pass

class GameplayState(GameState):
    """
    Main gameplay state where the fighting happens
    """
    
    def __init__(self, state_manager):
        """
        Initialize gameplay state
        """
        super().__init__(state_manager)
        
        # Characters will be set when entering based on selections
        self.characters = []
        self.player1_character = None
        self.player2_character = None
        
        # Stage configuration
        self.current_stage = "plains"  # Default stage
        self.stage_bounds = pygame.Rect(0, 0, 1280, 720)
        self.fall_zones = {"left": -200, "right": 1480}  # Boundaries for falling off stage
        
        # Camera system
        self.camera_x = 0
        self.camera_y = 0
        
        # Game timer
        self.match_timer = 180.0  # 3 minutes
        self.match_start_time = 0.0
        
        # Respawn system
        self.respawn_timer = {}  # Player respawn timers
        self.respawn_positions = {1: (300, 400), 2: (900, 400)}  # Respawn positions
        
        self.ko_particles = []

        # Load death sound effects
        try:
            self.fall_sound = pygame.mixer.Sound('assets/audio/fall.mp3')
            self.rare_fall_sound = pygame.mixer.Sound('assets/audio/rare fall.mp3')
            print("✓ Death sound effects loaded successfully")
        except pygame.error as e:
            self.fall_sound = None
            self.rare_fall_sound = None
            print(f"Warning: Could not load death sound effects: {e}")

        print("Gameplay state initialized")
    
    def enter(self):
        """
        Called when entering gameplay
        """
        print("Entering gameplay state")
        
        # Set up stage first so spawn points exist
        self.setup_stage()
        
        # Create characters based on selections (now using stage spawn points)
        self.create_characters_from_selection()
        
        # Reset match state
        self.match_timer = 180.0
        self.match_start_time = 0.0
        self.respawn_timer = {}
        
        # Set up respawn positions from stage spawn points
        if hasattr(self, 'stage_object') and len(self.stage_object.spawn_points) >= 2:
            self.respawn_positions = {
                1: self.stage_object.spawn_points[0],
                2: self.stage_object.spawn_points[1]
            }
            print(f"🏁 Respawn positions set from stage: P1={self.respawn_positions[1]}, P2={self.respawn_positions[2]}")
        else:
            # Fallback respawn positions
            self.respawn_positions = {
                1: (300, 500),
                2: (900, 500)
            }
            print(f"⚠️ Using fallback respawn positions")
        
        # Reset character states
        if self.player1_character and self.player2_character:
            self.player1_character.damage_percent = 0.0
            self.player2_character.damage_percent = 0.0
            self.player1_character.lives = 3
            self.player2_character.lives = 3
            self.player1_character.velocity = [0, 0]
            self.player2_character.velocity = [0, 0]
            # Ensure characters start on ground (they should be at spawn points which are on platforms)
            self.player1_character.on_ground = True
            self.player2_character.on_ground = True
    
    def create_characters_from_selection(self):
        """
        Create character instances based on player selections
        """
        # Use selections from state manager, or defaults
        if hasattr(self.state_manager, 'selected_characters'):
            selections = self.state_manager.selected_characters
            p1_class = selections['player1']['class']
            p2_class = selections['player2']['class']
        else:
            # Default characters for testing
            p1_class = Warrior
            p2_class = Speedster
        
        # Use spawn points from the stage instead of hardcoded positions
        if hasattr(self, 'stage_object') and len(self.stage_object.spawn_points) >= 2:
            spawn1_x, spawn1_y = self.stage_object.spawn_points[0]
            spawn2_x, spawn2_y = self.stage_object.spawn_points[1]
            print(f"🎯 Using stage spawn points: P1 at ({spawn1_x}, {spawn1_y}), P2 at ({spawn2_x}, {spawn2_y})")
        else:
            # Fallback to default positions if stage doesn't have spawn points
            spawn1_x, spawn1_y = 300, 500
            spawn2_x, spawn2_y = 900, 500
            print(f"⚠️ Using fallback spawn points: P1 at ({spawn1_x}, {spawn1_y}), P2 at ({spawn2_x}, {spawn2_y})")
        
        # Create character instances
        self.player1_character = p1_class(spawn1_x, spawn1_y, 1)
        self.player2_character = p2_class(spawn2_x, spawn2_y, 2)
        self.characters = [self.player1_character, self.player2_character]
        
        print(f"Created characters: P1={self.player1_character.name}, P2={self.player2_character.name}")
    
    def setup_stage(self):
        """
        Configure stage using proper Stage objects with full physics and rendering
        """
        # Import stage classes
        from src.stages import Battlefield, Plains
        
        # Determine which stage to create
        if hasattr(self.state_manager, 'selected_stage'):
            stage_info = self.state_manager.selected_stage
            stage_type = stage_info['type']
        else:
            stage_type = "plains"  # Default
        
        # Create the actual Stage object
        if stage_type == "battlefield":
            self.stage_object = Battlefield()
            print(f"✓ Created Battlefield stage with {len(self.stage_object.platforms)} platforms")
        elif stage_type == "plains":
            self.stage_object = Plains()
            print(f"✓ Created Plains stage with {len(self.stage_object.platforms)} platforms")
        else:
            # Fallback to Plains
            self.stage_object = Plains()
            print(f"✓ Created default Plains stage")
        
        # Store stage info for legacy compatibility
        self.current_stage = stage_type
        self.stage_bounds = pygame.Rect(0, 0, self.stage_object.width, self.stage_object.height)
        
        # Update fall zones from stage blast zones
        self.fall_zones = {
            "left": self.stage_object.left_blast_zone,
            "right": self.stage_object.right_blast_zone
        }
        
        print(f"Stage setup: {self.current_stage} with blast zones at {self.fall_zones}")
    
    def reset_character_positions(self):
        """
        Reset characters to starting positions
        """
        self.player1_character.position[0] = self.respawn_positions[1][0]
        self.player1_character.position[1] = self.respawn_positions[1][1]
        self.player2_character.position[0] = self.respawn_positions[2][0]
        self.player2_character.position[1] = self.respawn_positions[2][1]
        
        # Reset velocities
        self.player1_character.velocity = [0, 0]
        self.player2_character.velocity = [0, 0]
        
        # Clear any ongoing states
        self.player1_character.is_in_hitstun = False
        self.player2_character.is_in_hitstun = False
    
    def exit(self):
        """
        Called when leaving gameplay
        """
        print("Exiting gameplay state")
    
    def handle_event(self, event):
        """
        Handle gameplay-specific events
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Reset match
                self.respawn_timer = {}
                self.reset_character_positions()
                print("Match reset!")
                return True
            elif event.key == pygame.K_F3:
                # Toggle debug mode
                self.game_engine.debug_mode = not self.game_engine.debug_mode
                print(f"Debug mode: {self.game_engine.debug_mode}")
                return True
            elif event.key == pygame.K_ESCAPE:
                # Return to menu
                self.state_manager.change_state(GameStateType.MAIN_MENU)
                return True
            elif event.key == pygame.K_t:
                # DEBUG: Test KO particles manually
                print("🎆 MANUAL KO PARTICLE TEST!")
                test_position = [640, 360]  # Center of screen
                self.trigger_ko_effect("bottom", test_position)
                return True
        
        return False
    
    def update(self, delta_time):
        """
        Update gameplay logic
        """
        # Update match timer
        self.match_timer = max(0, self.match_timer - delta_time)
        self.match_start_time += delta_time
        
        # Get input for both players
        input_manager = self.game_engine.get_input_manager()
        player1_input = input_manager.get_player_input(1)
        player2_input = input_manager.get_player_input(2)
        
        # Check for respawning players
        self.update_respawn_timers(delta_time)
        
        # Update characters with their inputs (only if not respawning)
        if 1 not in self.respawn_timer:
            self.player1_character.update(delta_time, player1_input, self.stage_object)
        if 2 not in self.respawn_timer:
            self.player2_character.update(delta_time, player2_input, self.stage_object)
        
        # Update physics manager with proper stage object
        physics_manager = self.game_engine.get_physics_manager()
        stage_to_pass = getattr(self, 'stage_object', self.stage_bounds)
        k_o_d_players = physics_manager.update(delta_time, self.characters, stage_to_pass)
        
        # Handle KOs from blast zones
        for player_id, ko_info in k_o_d_players.items():
            self.ko_player(player_id, ko_info)
        
        # Check for damage-based KOs
        if 1 not in self.respawn_timer and self.player1_character.damage_percent >= 300:
            self.ko_player(1)
        if 2 not in self.respawn_timer and self.player2_character.damage_percent >= 300:
            self.ko_player(2)
        
        # Update stage dynamics (weather, animations, etc.)
        if hasattr(self, 'stage_object'):
            self.stage_object.update(delta_time)
        
        # Update KO particles
        self.update_ko_particles(delta_time)
        
        # Simple camera following
        self.update_camera()
        
        # Check for match end conditions
        self.check_match_end()
    
    def update_respawn_timers(self, delta_time):
        """
        Update respawn timers for KO'd players
        """
        for player in list(self.respawn_timer.keys()):
            self.respawn_timer[player] -= delta_time
            if self.respawn_timer[player] <= 0:
                # Respawn the player
                self.respawn_player(player)
                del self.respawn_timer[player]
    
    def check_match_end(self):
        """
        Check for match end conditions
        """
        winner = None
        winner_character = None
        loser_character = None
        
        # Check for life-based KO
        if self.player1_character.lives <= 0:
            winner = 2
            winner_character = self.player2_character.name
            loser_character = self.player1_character.name
        elif self.player2_character.lives <= 0:
            winner = 1
            winner_character = self.player1_character.name
            loser_character = self.player2_character.name
        
        # Check timer-based win (lowest damage wins)
        elif self.match_timer <= 0:
            if self.player1_character.damage_percent < self.player2_character.damage_percent:
                winner = 1
                winner_character = self.player1_character.name
                loser_character = self.player2_character.name
            elif self.player2_character.damage_percent < self.player1_character.damage_percent:
                winner = 2
                winner_character = self.player2_character.name
                loser_character = self.player1_character.name
            else:
                # It's a tie - for now, just declare player 1 winner
                winner = 1
                winner_character = self.player1_character.name
                loser_character = self.player2_character.name
        
        # If we have a winner, transition to win screen
        if winner:
            self.transition_to_win_screen(winner, winner_character, loser_character)
    
    def transition_to_win_screen(self, winner, winner_character, loser_character):
        """
        Transition to win screen with match results
        """
        # Store match results in state manager
        self.state_manager.match_results = {
            'winner': winner,
            'loser': 3 - winner,  # Other player
            'winner_character': winner_character,
            'loser_character': loser_character,
            'match_time': self.match_start_time,
            'winner_damage': self.player2_character.damage_percent if winner == 1 else self.player1_character.damage_percent,
            'loser_damage': self.player1_character.damage_percent if winner == 1 else self.player2_character.damage_percent
        }
        
        print(f"Match ended! Winner: Player {winner} ({winner_character})")
        self.state_manager.change_state(GameStateType.WIN_SCREEN)
    
    def update_camera(self):
        """
        Update camera to follow the action
        """
        # Simple camera that follows the midpoint between characters
        if self.player1_character and self.player2_character:
            midpoint_x = (self.player1_character.position[0] + self.player2_character.position[0]) / 2
            
            # Keep camera centered on the action
            self.camera_x = midpoint_x - 640  # Half screen width
            
            # Clamp camera to stage bounds
            self.camera_x = max(0, min(self.camera_x, self.stage_bounds.width - 1280))
    
    def render(self, screen):
        """
        Render the gameplay scene
        """
        # Render stage background
        self.render_stage_background(screen)
        
        # Render characters
        camera_offset = (self.camera_x, self.camera_y)
        if 1 not in self.respawn_timer:
            self.player1_character.render(screen, camera_offset)
        if 2 not in self.respawn_timer:
            self.player2_character.render(screen, camera_offset)
        
        # Render respawn indicators
        self.render_respawn_indicators(screen)
        
        # Render UI
        self.render_ui(screen)
        
        # Render all visual effects on top of everything else
        self.render_visual_effects(screen, camera_offset)
    
    def render_stage_background(self, screen):
        """
        Render stage background using proper Stage objects with full visual systems
        """
        camera_offset = (self.camera_x, self.camera_y)
        
        # Use the modern stage object if available
        if hasattr(self, 'stage_object'):
            # Render background layers (sky, mountains, etc.)
            self.stage_object.render_background(screen, camera_offset)
            
            # Render platforms with full styling
            self.stage_object.render_platforms(screen, camera_offset)
            
            # NOTE: Foreground effects are now rendered in render_visual_effects instead
            
        else:
            # Fallback to legacy rendering for compatibility
            self.render_legacy_stage_background(screen)
    
    def render_legacy_stage_background(self, screen):
        """
        Legacy stage rendering for backwards compatibility
        """
        if self.current_stage == "battlefield":
            # Darker background for battlefield
            screen.fill((100, 120, 200))
            
            # Draw platforms
            # Main platform
            main_platform = pygame.Rect(240, 500, 800, 40)
            pygame.draw.rect(screen, (80, 80, 160), main_platform)
            
            # Side platforms
            left_platform = pygame.Rect(150, 400, 300, 30)
            right_platform = pygame.Rect(830, 400, 300, 30)
            pygame.draw.rect(screen, (60, 60, 140), left_platform)
            pygame.draw.rect(screen, (60, 60, 140), right_platform)
            
            # Fall zones indicators (remove these since we want proper blast zones)
            # pygame.draw.rect(screen, (255, 100, 100), pygame.Rect(0, 0, 100, 720), 3)
            # pygame.draw.rect(screen, (255, 100, 100), pygame.Rect(1180, 0, 100, 720), 3)
        else:
            # Plains background
            screen.fill((135, 206, 235))
            
            # Draw simple ground
            ground_rect = pygame.Rect(0, 500, 1280, 220)
            pygame.draw.rect(screen, (34, 139, 34), ground_rect)
    
    def render_respawn_indicators(self, screen):
        """
        Render indicators for respawning players
        """
        font = pygame.font.Font(None, 36)
        
        for player, timer in self.respawn_timer.items():
            # Show floating indicator where player will respawn
            pos = self.respawn_positions[player]
            respawn_text = font.render(f"P{player} Respawning: {timer:.1f}s", True, (255, 255, 100))
            text_rect = respawn_text.get_rect(center=(pos[0], pos[1] - 50))
            screen.blit(respawn_text, text_rect)
            
            # Draw a circle at respawn position
            pygame.draw.circle(screen, (255, 255, 100), (int(pos[0]), int(pos[1])), 30, 3)
    
    def render_ui(self, screen):
        """
        Render gameplay UI elements with Smash Bros style damage percentages
        """
        font = pygame.font.Font(None, 48)
        small_font = pygame.font.Font(None, 24)
        large_font = pygame.font.Font(None, 72)
        
        # Player 1 damage percentage (bottom left)
        p1_damage_text = large_font.render(f"{int(self.player1_character.damage_percent)}%", True, (255, 255, 255))
        p1_damage_shadow = large_font.render(f"{int(self.player1_character.damage_percent)}%", True, (0, 0, 0))
        screen.blit(p1_damage_shadow, (52, 642))  # Shadow offset
        screen.blit(p1_damage_text, (50, 640))
        
        # Player 1 lives
        p1_lives_text = small_font.render(f"Lives: {self.player1_character.lives}", True, (255, 255, 255))
        screen.blit(p1_lives_text, (50, 690))
        
        # Player 2 damage percentage (bottom right)
        p2_damage_text = large_font.render(f"{int(self.player2_character.damage_percent)}%", True, (255, 255, 255))
        p2_damage_shadow = large_font.render(f"{int(self.player2_character.damage_percent)}%", True, (0, 0, 0))
        p2_rect = p2_damage_text.get_rect()
        screen.blit(p2_damage_shadow, (1280 - p2_rect.width - 48, 642))  # Shadow offset
        screen.blit(p2_damage_text, (1280 - p2_rect.width - 50, 640))
        
        # Player 2 lives
        p2_lives_text = small_font.render(f"Lives: {self.player2_character.lives}", True, (255, 255, 255))
        p2_lives_rect = p2_lives_text.get_rect()
        screen.blit(p2_lives_text, (1280 - p2_lives_rect.width - 50, 690))
        
        # Character names
        p1_name = small_font.render(self.player1_character.name, True, (100, 150, 255))
        p2_name = small_font.render(self.player2_character.name, True, (255, 100, 100))
        screen.blit(p1_name, (50, 620))
        screen.blit(p2_name, (1280 - 250, 620))
        
        # Match timer (center top)
        timer_text = font.render(f"Time: {int(self.match_timer)}", True, (255, 255, 255))
        timer_shadow = font.render(f"Time: {int(self.match_timer)}", True, (0, 0, 0))
        timer_rect = timer_text.get_rect(center=(640, 30))
        shadow_rect = timer_shadow.get_rect(center=(642, 32))
        screen.blit(timer_shadow, shadow_rect)
        screen.blit(timer_text, timer_rect)
        
        # Stage name
        stage_text = small_font.render(f"Stage: {self.current_stage.title()}", True, (200, 200, 200))
        screen.blit(stage_text, (10, 10))
        
        # Control hints (only in debug mode)
        if self.game_engine.debug_mode:
            instructions = [
                "Player 1: WASD to move, Left Shift+direction = attack types",
                "Player 2: PL;' to move, Right Shift+direction = attack types",
                "Attack types: No dir=Neutral, Side=Strong, Up=Launcher, Down=Spike",
                "R=Reset, F3=Debug, ESC=Menu"
            ]
            for i, instruction in enumerate(instructions):
                text = small_font.render(instruction, True, (255, 255, 0))
                screen.blit(text, (10, 720 - 80 + i * 20))

    def ko_player(self, player, ko_info=None):
        """
        KO a player, decrement their lives, and set them up for respawn.
        """
        character_to_ko = self.player1_character if player == 1 else self.player2_character
        
        # Avoid multiple KOs in the same frame
        if player in self.respawn_timer:
            return

        print(f"Player {player} has been KO'd!")
        character_to_ko.lose_life()
        
        if ko_info:
            self.trigger_ko_effect(ko_info["direction"], ko_info["position"])

        # Check for game over
        if character_to_ko.lives <= 0:
            self.check_match_end()
            return

        # Set respawn timer (2 seconds)
        self.respawn_timer[player] = 2.0
        
        # Move player off-screen immediately
        if player == 1:
            self.player1_character.position[0] = -500
            self.player1_character.position[1] = 300
        else:
            self.player2_character.position[0] = 1780
            self.player2_character.position[1] = 300
    
    def respawn_player(self, player):
        """
        Respawn a player at their spawn position
        """
        print(f"Player {player} respawned!")
        
        pos = self.respawn_positions[player]
        if player == 1:
            self.player1_character.position[0] = pos[0]
            self.player1_character.position[1] = pos[1] 
            self.player1_character.velocity = [0, 0]
            self.player1_character.is_in_hitstun = False
        else:
            self.player2_character.position[0] = pos[0]
            self.player2_character.position[1] = pos[1]
            self.player2_character.velocity = [0, 0]
            self.player2_character.is_in_hitstun = False

    def trigger_ko_effect(self, direction, position):
        """Spawns a burst of 'confetti' particles from the direction of the KO."""
        particle_count = 50
        
        # Play death sound effect
        self.play_death_sound()
        
        for _ in range(particle_count):
            if direction == 'bottom':
                # Spawn from bottom of screen, moving upward
                x = position[0] + random.uniform(-100, 100)  # Around the KO position
                y = position[1] + random.uniform(50, 100)   # Below the KO position
                vx = random.uniform(-8, 8)
                vy = random.uniform(-25, -15)  # Much faster upward movement
            elif direction == 'top':
                # Spawn from top of screen, moving downward
                x = position[0] + random.uniform(-100, 100)
                y = position[1] - random.uniform(50, 100)   # Above the KO position
                vx = random.uniform(-8, 8)
                vy = random.uniform(15, 25)   # Much faster downward movement
            elif direction == 'left':
                # Spawn from left side, moving right and upward
                x = position[0] - random.uniform(50, 100)   # Left of KO position
                y = position[1] + random.uniform(-100, 100)
                vx = random.uniform(10, 20)   # Much faster rightward movement
                vy = random.uniform(-15, -5)  # Strong upward component
            elif direction == 'right':
                # Spawn from right side, moving left and upward
                x = position[0] + random.uniform(50, 100)   # Right of KO position
                y = position[1] + random.uniform(-100, 100)
                vx = random.uniform(-20, -10)  # Much faster leftward movement
                vy = random.uniform(-15, -5)   # Strong upward component
            
            # Generate red and white colors only
            color_choice = random.choice(['red', 'white'])
            if color_choice == 'red':
                color = (random.randint(180, 255), random.randint(0, 60), random.randint(0, 60))  # Various reds
            else:
                color = (random.randint(240, 255), random.randint(240, 255), random.randint(240, 255))  # Various whites
            
            self.ko_particles.append({
                'pos': [x, y],
                'vel': [vx, vy],
                'lifetime': random.randint(120, 180),  # Even longer lifetime for higher velocities
                'color': color,
                'size': random.randint(6, 12)
            })

    def play_death_sound(self):
        """Play death sound effect when a player is KO'd."""
        if self.fall_sound is None:
            return  # No sound files loaded
        
        # 1 in 75 chance to play rare fall sound
        if random.randint(1, 75) == 1 and self.rare_fall_sound:
            print("🎵 Playing rare fall sound!")
            self.rare_fall_sound.play()
        else:
            self.fall_sound.play()

    def update_ko_particles(self, delta_time):
        """Update the position and lifetime of KO particles."""
        for p in self.ko_particles[:]:
            p['pos'][0] += p['vel'][0]
            p['pos'][1] += p['vel'][1]
            p['vel'][1] += 0.2  # Stronger gravity for more dramatic arcs
            p['lifetime'] -= 1
            if p['lifetime'] <= 0:
                self.ko_particles.remove(p)

    def render_ko_particles(self, screen, camera_offset):
        """Render the KO particles."""
        for p in self.ko_particles:
            pos_x = p['pos'][0] - camera_offset[0]
            pos_y = p['pos'][1] - camera_offset[1]
            # Simple, clean particle rendering
            pygame.draw.circle(screen, p['color'], (int(pos_x), int(pos_y)), p['size'])

    def render_visual_effects(self, screen, camera_offset):
        """
        Renders all particle effects and other visual overlays.
        This is called last to ensure effects appear on top of game elements.
        """
        # Render stage-specific foreground effects (e.g., snow) AND KO particles together
        if hasattr(self, 'stage_object') and hasattr(self.stage_object, 'render_foreground'):
            # Pass KO particles to the stage so they can be rendered alongside snow
            self.stage_object.ko_particles_from_game = self.ko_particles
            self.stage_object.render_foreground(screen, camera_offset)
        
        # ALSO render KO particles here as backup
        self.render_ko_particles(screen, camera_offset)

class SimpleMenuState(GameState):
    """
    Simple menu state 
    """
    
    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.selected_option = 0
        self.menu_options = ["Start Game", "Quit"]
        
        # Load background and define button styles
        try:
            self.background_image = pygame.image.load('assets/images/splash.png')
            self.background_image = pygame.transform.scale(self.background_image, (1280, 720))
        except pygame.error:
            self.background_image = None
            print("Warning: Could not load splash.png. Using solid color background.")

        self.button_color = (40, 40, 80, 180) # Semi-transparent dark blue
        self.highlight_color = (80, 80, 150, 220) # Brighter, more opaque blue
        self.border_color = (255, 255, 0) # Yellow border for highlight
        self.button_width = 300
        self.button_height = 60

        # Load title music
        try:
            self.title_music = pygame.mixer.Sound(os.path.join('assets', 'audio', 'title.mp3'))
        except pygame.error:
            self.title_music = None
            print("Warning: Could not load title.mp3")

    def enter(self):
        """Called when entering this state."""
        if self.title_music:
            self.title_music.play(loops=-1)

    def exit(self):
        """Called when leaving this state."""
        if self.title_music:
            self.title_music.stop()

    def handle_event(self, event):
        # Handle Keyboard Input
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                return True
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                return True
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.select_option()
                return True
        
        # Handle Joystick Input
        if event.type == pygame.JOYBUTTONDOWN:
            # P1 Attack button confirms selection
            if event.button == 3: # Corresponds to dpad_right on L Joy-Con
                self.select_option()
                return True
        
        if event.type == pygame.JOYAXISMOTION:
            # P1 Vertical stick navigates menu
            if event.axis == 1 and abs(event.value) > 0.5:
                if event.value < -0.5: # Up
                    self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                elif event.value > 0.5: # Down
                    self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                return True
                
        return False

    def select_option(self):
        """Action when a menu option is selected."""
        if self.selected_option == 0:  # Start Game
            self.state_manager.change_state(GameStateType.CHARACTER_SELECT)
        elif self.selected_option == 1:  # Quit
            pygame.event.post(pygame.event.Event(pygame.QUIT))
    
    def render(self, screen):
        # Draw background
        if self.background_image:
            screen.blit(self.background_image, (0, 0))
        else:
            screen.fill((20, 20, 40)) # Fallback color
        
        font = pygame.font.Font(None, 72)
        menu_font = pygame.font.Font(None, 48)
        
        # Title
        title = font.render("SUPER SCUFFED FIGHTERS", True, (255, 255, 255))
        title_shadow = font.render("SUPER SCUFFED FIGHTERS", True, (0, 0, 0))
        title_rect = title.get_rect(center=(640, 200))
        screen.blit(title_shadow, (title_rect.x + 3, title_rect.y + 3))
        screen.blit(title, title_rect)
        
        # Menu options as buttons
        for i, option in enumerate(self.menu_options):
            button_rect = pygame.Rect(
                (1280 - self.button_width) / 2, 
                350 + i * 80, 
                self.button_width, 
                self.button_height
            )
            
            # Create a surface for the button with per-pixel alpha
            button_surface = pygame.Surface((self.button_width, self.button_height), pygame.SRCALPHA)

            if i == self.selected_option:
                # Draw highlighted button
                pygame.draw.rect(button_surface, self.highlight_color, button_surface.get_rect(), border_radius=10)
                pygame.draw.rect(button_surface, self.border_color, button_surface.get_rect(), 3, border_radius=10)
                text_color = (255, 255, 255)
            else:
                # Draw normal button
                pygame.draw.rect(button_surface, self.button_color, button_surface.get_rect(), border_radius=10)
                text_color = (200, 200, 200)

            # Render text on the button
            text = menu_font.render(option, True, text_color)
            text_rect = text.get_rect(center=(self.button_width / 2, self.button_height / 2))
            button_surface.blit(text, text_rect)

            # Blit the button surface onto the screen
            screen.blit(button_surface, button_rect.topleft)
        
        # Instructions
        instruction_font = pygame.font.Font(None, 24)
        instructions = "Use W/S or Arrow Keys to navigate, Enter/Space to select"
        instr_text = instruction_font.render(instructions, True, (220, 220, 220))
        instr_shadow = instruction_font.render(instructions, True, (0, 0, 0))
        instr_rect = instr_text.get_rect(center=(640, 550))
        screen.blit(instr_shadow, (instr_rect.x + 1, instr_rect.y + 1))
        screen.blit(instr_text, instr_rect)

class StateManager:
    """
    Manages game states and transitions between them
    """
    
    def __init__(self, game_engine):
        """
        Initialize the state manager
        """
        self.game_engine = game_engine
        game_engine.set_state_manager(self)
        
        # State management
        self.states = {}
        self.current_state = None
        self.current_state_type = None
        
        # Game data storage
        self.selected_characters = None
        self.selected_stage = None
        self.match_results = None
        
        # Load shared music
        try:
            self.config_music = pygame.mixer.Sound(os.path.join('assets', 'audio', 'game config.mp3'))
            self.is_config_music_playing = False
        except pygame.error:
            self.config_music = None
            print("Warning: Could not load game config.mp3")

        # Import and create all states
        self.create_all_states()
        
        # Start with menu
        self.change_state(GameStateType.MAIN_MENU)
    
    def create_all_states(self):
        """
        Create all game state instances
        """
        # Import UI states here to avoid circular imports
        from src.ui.character_select import CharacterSelectState
        from src.ui.stage_select import StageSelectState
        from src.ui.versus_screen import VersusScreenState
        from src.ui.win_screen import WinScreenState
        
        # Create all states
        self.states[GameStateType.MAIN_MENU] = SimpleMenuState(self)
        self.states[GameStateType.CHARACTER_SELECT] = CharacterSelectState(self)
        self.states[GameStateType.STAGE_SELECT] = StageSelectState(self)
        self.states[GameStateType.VERSUS_SCREEN] = VersusScreenState(self)
        self.states[GameStateType.GAMEPLAY] = GameplayState(self)
        self.states[GameStateType.WIN_SCREEN] = WinScreenState(self)
    
    def change_state(self, state_type):
        """
        Change to a completely new state
        """
        # --- Music Control Logic ---
        # Stop config music if leaving a config screen for gameplay or main menu
        if self.config_music and self.is_config_music_playing:
            if state_type == GameStateType.VERSUS_SCREEN or state_type == GameStateType.MAIN_MENU:
                self.config_music.stop()
                self.is_config_music_playing = False
                print("Stopped config music.")

        if self.current_state:
            self.current_state.exit()
        
        self.current_state_type = state_type
        self.current_state = self.states[state_type]
        self.current_state.enter()
        
        # Start config music if entering the config screens
        if self.config_music and not self.is_config_music_playing:
            if state_type == GameStateType.CHARACTER_SELECT:
                self.config_music.play(loops=-1)
                self.is_config_music_playing = True
                print("Started config music.")

        print(f"State changed to: {state_type.value}")
    
    def handle_event(self, event):
        """
        Forward events to current state
        """
        if self.current_state:
            return self.current_state.handle_event(event)
        return False
    
    def update(self, delta_time):
        """
        Update current state
        """
        if self.current_state:
            self.current_state.update(delta_time)
    
    def render(self, screen):
        """
        Render current state
        """
        if self.current_state:
            self.current_state.render(screen) 