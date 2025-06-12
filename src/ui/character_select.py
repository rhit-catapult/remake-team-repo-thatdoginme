"""
Character Select - Two-Player Fighter Selection Interface
=========================================================

Character selection screen where both players choose their fighters.
Features character portraits, stats display, and smooth selection animations.

Features:
- Two-player simultaneous character selection
- Red (Player 1) and Blue (Player 2) selection cursors
- Character preview with stats and descriptions
- Key hints for both players
- Confirmation system before proceeding

Controls:
- Player 1: WASD to move cursor, Q to select/confirm
- Player 2: IJKL to move cursor, U to select/confirm
"""

import pygame
from src.core.state_manager import GameState, GameStateType
from src.characters.warrior import Warrior
from src.characters.speedster import Speedster
from src.characters.heavy import Heavy
from enum import Enum
from src.input.input_manager import InputManager
import os

class SelectionState(Enum):
    """
    Current state of character selection process
    """
    SELECTING = "selecting"
    BOTH_CONFIRMED = "both_confirmed"
    TRANSITIONING = "transitioning"

class CharacterSelectState(GameState):
    """
    Two-player character selection screen
    """
    
    def __init__(self, state_manager):
        """
        Initialize character select screen
        """
        super().__init__(state_manager)
        
        # Available characters
        self.characters = [
            {"name": "Warrior", "class": Warrior, "archetype": "Balanced", "difficulty": "Beginner"},
            {"name": "Speedster", "class": Speedster, "archetype": "Rushdown", "difficulty": "Advanced"}, 
            {"name": "Heavy", "class": Heavy, "archetype": "Grappler", "difficulty": "Intermediate"}
        ]
        
        # Load character portraits
        self.character_portraits = {}
        for char in self.characters:
            char_name = char["name"]
            path = os.path.join('assets', 'images', 'portraits', f'{char_name}.png')
            if os.path.exists(path):
                self.character_portraits[char_name] = pygame.image.load(path).convert_alpha()
            else:
                self.character_portraits[char_name] = None # Placeholder

        # Player selections
        self.player1_cursor = 0  # Current cursor position
        self.player2_cursor = 0
        self.player1_selection = None  # Confirmed selection
        self.player2_selection = None
        
        # Selection state
        self.current_state = SelectionState.SELECTING
        self.transition_timer = 0.0
        
        # Visual properties
        self.character_box_width = 200
        self.character_box_height = 250
        self.character_spacing = 50
        self.grid_start_x = 640 - (len(self.characters) * (self.character_box_width + self.character_spacing) - self.character_spacing) // 2
        self.grid_y = 200
        
        # Load background
        try:
            self.background_image = pygame.image.load('assets/images/configselect.png').convert()
            self.background_image = pygame.transform.scale(self.background_image, (1280, 720))
        except pygame.error:
            self.background_image = None
            print("Warning: Could not load configselect.png for character select.")
        
        # Joystick navigation helpers
        self.last_joy_move_time = 0
        self.joy_move_delay = 200 # milliseconds
        
        # Colors
        self.player1_color = (255, 100, 100)  # Red
        self.player2_color = (100, 150, 255)  # Blue
        self.confirmed_color = (100, 255, 100)  # Green
        self.background_color = (30, 30, 50)
        
        # Fonts
        self.title_font = pygame.font.Font(None, 64)
        self.character_font = pygame.font.Font(None, 32)
        self.info_font = pygame.font.Font(None, 24)
        self.hint_font = pygame.font.Font(None, 20)
    
    def enter(self):
        """
        Called when entering character select
        """
        # Reset selections
        self.player1_cursor = 0
        self.player2_cursor = 0
        self.player1_selection = None
        self.player2_selection = None
        self.current_state = SelectionState.SELECTING
        
        print("Entering character select screen")
    
    def exit(self):
        """
        Called when leaving character select
        """
        print("Exiting character select screen")
    
    def handle_event(self, event):
        """
        Handle character select input events
        """
        if self.current_state != SelectionState.SELECTING:
            return False

        input_manager = self.game_engine.get_input_manager()

        # --- Handle Keyboard Input ---
        if event.type == pygame.KEYDOWN:
            # Player 1 controls
            if event.key == pygame.K_a: self.move_cursor(1, -1)
            elif event.key == pygame.K_d: self.move_cursor(1, 1)
            elif event.key == pygame.K_LSHIFT: self.confirm_selection(1)
            
            # Player 2 controls
            elif event.key == pygame.K_l: self.move_cursor(2, -1)
            elif event.key == pygame.K_QUOTE: self.move_cursor(2, 1)
            elif event.key == pygame.K_RSHIFT: self.confirm_selection(2)
            
            # Global
            elif event.key == pygame.K_ESCAPE:
                self.state_manager.change_state(GameStateType.MAIN_MENU)
            
            return True

        # --- Handle Joystick Input ---
        player_id = input_manager.get_player_id_from_joystick(event.instance_id) if hasattr(event, 'instance_id') else None
        
        if player_id is None:
            return False

        if event.type == pygame.JOYBUTTONDOWN:
            # Player 1 (Joy-Con) uses button 1; Player 2 (Xbox) uses button 0
            attack_button = 1 if player_id == 1 else 0
            if event.button == attack_button:
                self.confirm_selection(player_id)
                return True
        
        if event.type == pygame.JOYAXISMOTION:
            # Both controllers use axis 0 for left/right navigation
            if event.axis == 0:
                current_time = pygame.time.get_ticks()
                if current_time - self.last_joy_move_time > self.joy_move_delay:
                    if event.value < -0.5: # Left
                        self.move_cursor(player_id, -1)
                        self.last_joy_move_time = current_time
                    elif event.value > 0.5: # Right
                        self.move_cursor(player_id, 1)
                        self.last_joy_move_time = current_time
                    return True

        return False

    def move_cursor(self, player, direction):
        """Move a player's cursor."""
        if player == 1 and self.player1_selection is None:
            self.player1_cursor = (self.player1_cursor + direction) % len(self.characters)
            self.play_navigate_sound()
        elif player == 2 and self.player2_selection is None:
            self.player2_cursor = (self.player2_cursor + direction) % len(self.characters)
            self.play_navigate_sound()

    def confirm_selection(self, player):
        """Confirm a player's selection."""
        if player == 1 and self.player1_selection is None:
            self.player1_selection = self.player1_cursor
            self.play_confirm_sound()
            print(f"Player 1 selected {self.characters[self.player1_selection]['name']}")
        elif player == 2 and self.player2_selection is None:
            self.player2_selection = self.player2_cursor
            self.play_confirm_sound()
            print(f"Player 2 selected {self.characters[self.player2_selection]['name']}")
        
        self.check_both_selected()
    
    def check_both_selected(self):
        """
        Check if both players have selected and proceed
        """
        if self.player1_selection is not None and self.player2_selection is not None:
            self.current_state = SelectionState.BOTH_CONFIRMED
            self.transition_timer = 1.0  # 1 second delay before transition
            print("Both players selected! Proceeding to stage select...")
    
    def play_navigate_sound(self):
        """
        Play navigation sound effect
        """
        # TODO: Add sound effect
        pass
    
    def play_confirm_sound(self):
        """
        Play confirmation sound effect
        """
        # TODO: Add sound effect
        pass
    
    def update(self, delta_time):
        """
        Update character select logic
        """
        if self.current_state == SelectionState.BOTH_CONFIRMED:
            self.transition_timer -= delta_time
            if self.transition_timer <= 0:
                # Store selections in state manager for later use
                self.state_manager.selected_characters = {
                    'player1': self.characters[self.player1_selection],
                    'player2': self.characters[self.player2_selection]
                }
                # Proceed to stage select
                self.state_manager.change_state(GameStateType.STAGE_SELECT)
    
    def render(self, screen):
        """
        Render the character select screen
        """
        if self.background_image:
            screen.blit(self.background_image, (0, 0))
        else:
            screen.fill(self.background_color)
        
        # Render title
        title_text = self.title_font.render("SELECT YOUR FIGHTER", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(640, 80))
        screen.blit(title_text, title_rect)
        
        # Render character boxes
        for i, character in enumerate(self.characters):
            self.render_character_box(screen, character, i)
        
        # Render player cursors
        self.render_player_cursors(screen)
        
        # Render player info panels
        self.render_player_panels(screen)
        
        # Render controls hints
        self.render_control_hints(screen)
        
        # Render transition state
        if self.current_state == SelectionState.BOTH_CONFIRMED:
            self.render_transition_overlay(screen)
    
    def render_character_box(self, screen, character, index):
        """
        Render individual character selection box
        """
        box_x = self.grid_start_x + index * (self.character_box_width + self.character_spacing)
        box_y = self.grid_y
        
        # Character box background
        box_rect = pygame.Rect(box_x, box_y, self.character_box_width, self.character_box_height)
        pygame.draw.rect(screen, (60, 60, 80), box_rect)
        pygame.draw.rect(screen, (255, 255, 255), box_rect, 2)
        
        # Character portrait
        portrait = self.character_portraits.get(character["name"])
        if portrait:
            # Scale portrait to fit the box
            portrait_scaled = pygame.transform.scale(portrait, (150, 120))
            portrait_rect = portrait_scaled.get_rect(center=(box_x + self.character_box_width // 2, box_y + 80))
            screen.blit(portrait_scaled, portrait_rect)
        else:
            # Character portrait placeholder (large colored rectangle)
            portrait_rect = pygame.Rect(box_x + 25, box_y + 20, 150, 120)
            character_colors = {
                "Warrior": (200, 150, 100),
                "Speedster": (255, 255, 100), 
                "Heavy": (150, 100, 200)
            }
            portrait_color = character_colors.get(character["name"], (150, 150, 150))
            pygame.draw.rect(screen, portrait_color, portrait_rect)
            pygame.draw.rect(screen, (255, 255, 255), portrait_rect, 2)
        
        # Character name
        name_text = self.character_font.render(character["name"], True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(box_x + self.character_box_width // 2, box_y + 160))
        screen.blit(name_text, name_rect)
        
        # Character archetype
        archetype_text = self.info_font.render(character["archetype"], True, (200, 200, 200))
        archetype_rect = archetype_text.get_rect(center=(box_x + self.character_box_width // 2, box_y + 185))
        screen.blit(archetype_text, archetype_rect)
        
        # Character difficulty
        difficulty_text = self.info_font.render(f"Difficulty: {character['difficulty']}", True, (150, 150, 150))
        difficulty_rect = difficulty_text.get_rect(center=(box_x + self.character_box_width // 2, box_y + 210))
        screen.blit(difficulty_text, difficulty_rect)
    
    def render_player_cursors(self, screen):
        """
        Render selection cursors for both players
        """
        # Player 1 cursor (Red)
        if self.player1_selection is None:
            p1_box_x = self.grid_start_x + self.player1_cursor * (self.character_box_width + self.character_spacing)
            p1_cursor_rect = pygame.Rect(p1_box_x - 5, self.grid_y - 5, self.character_box_width + 10, self.character_box_height + 10)
            pygame.draw.rect(screen, self.player1_color, p1_cursor_rect, 4)
        else:
            # Show confirmed selection
            p1_box_x = self.grid_start_x + self.player1_selection * (self.character_box_width + self.character_spacing)
            p1_cursor_rect = pygame.Rect(p1_box_x - 5, self.grid_y - 5, self.character_box_width + 10, self.character_box_height + 10)
            pygame.draw.rect(screen, self.confirmed_color, p1_cursor_rect, 6)
        
        # Player 2 cursor (Blue)
        if self.player2_selection is None:
            p2_box_x = self.grid_start_x + self.player2_cursor * (self.character_box_width + self.character_spacing)
            p2_cursor_rect = pygame.Rect(p2_box_x - 8, self.grid_y - 8, self.character_box_width + 16, self.character_box_height + 16)
            pygame.draw.rect(screen, self.player2_color, p2_cursor_rect, 4)
        else:
            # Show confirmed selection  
            p2_box_x = self.grid_start_x + self.player2_selection * (self.character_box_width + self.character_spacing)
            p2_cursor_rect = pygame.Rect(p2_box_x - 8, self.grid_y - 8, self.character_box_width + 16, self.character_box_height + 16)
            pygame.draw.rect(screen, self.confirmed_color, p2_cursor_rect, 6)
    
    def render_player_panels(self, screen):
        """
        Render information panels for both players
        """
        # Player 1 panel (left side)
        self.render_player_panel(screen, 1, 50, 500, self.player1_cursor, self.player1_selection)
        
        # Player 2 panel (right side)
        self.render_player_panel(screen, 2, 1280 - 350, 500, self.player2_cursor, self.player2_selection)
    
    def render_player_panel(self, screen, player, x, y, cursor_pos, selection):
        """
        Render information panel for a specific player
        """
        # Panel background
        panel_rect = pygame.Rect(x, y, 300, 180)
        pygame.draw.rect(screen, (40, 40, 60), panel_rect)
        pygame.draw.rect(screen, (255, 255, 255), panel_rect, 2)
        
        # Player title
        color = self.player1_color if player == 1 else self.player2_color
        if selection is not None:
            color = self.confirmed_color
            
        title_text = self.character_font.render(f"Player {player}", True, color)
        screen.blit(title_text, (x + 10, y + 10))
        
        # Status
        if selection is not None:
            status_text = self.info_font.render("READY!", True, self.confirmed_color)
            character_name = self.characters[selection]['name']
            selected_text = self.info_font.render(f"Selected: {character_name}", True, (255, 255, 255))
            screen.blit(selected_text, (x + 10, y + 40))
        else:
            status_text = self.info_font.render("Selecting...", True, (200, 200, 200))
            current_char = self.characters[cursor_pos]['name']
            preview_text = self.info_font.render(f"Preview: {current_char}", True, (150, 150, 150))
            screen.blit(preview_text, (x + 10, y + 40))
        
        screen.blit(status_text, (x + 10, y + 65))
        
        # Character stats preview
        char_index = selection if selection is not None else cursor_pos
        character = self.characters[char_index]
        
        stats_title = self.info_font.render("Stats:", True, (255, 255, 255))
        screen.blit(stats_title, (x + 10, y + 95))
        
        # Mock stats based on character
        if character['name'] == 'Warrior':
            stats = ["Speed: 3/5", "Power: 3/5", "Defense: 3/5"]
        elif character['name'] == 'Speedster':
            stats = ["Speed: 5/5", "Power: 2/5", "Defense: 2/5"]
        else:  # Heavy
            stats = ["Speed: 1/5", "Power: 4/5", "Defense: 5/5"]
        
        for i, stat in enumerate(stats):
            stat_text = self.hint_font.render(stat, True, (200, 200, 200))
            screen.blit(stat_text, (x + 15, y + 115 + i * 18))

    def render_control_hints(self, screen):
        """
        Render control hints for both players
        """
        myinputmanager = InputManager()
        # Player 1 controls (left side)
        p1_hints = [
            "Player 1 Controls:",
            f"{(pygame.key.name(myinputmanager.player1_keys['up'])).upper()}{pygame.key.name(myinputmanager.player1_keys['left']).upper()}{pygame.key.name(myinputmanager.player1_keys['down']).upper()}{pygame.key.name(myinputmanager.player1_keys['right']).upper()} - Move",
            f"{(pygame.key.name(myinputmanager.player1_keys['attack']).upper())} - Select/Confirm; Attack",
            "ESC - Back to menu"
        ]
        
        for i, hint in enumerate(p1_hints):
            color = self.player1_color if i == 0 else (180, 180, 180)
            text = self.hint_font.render(hint, True, color)
            screen.blit(text, (20, 20 + i * 22))
        
        # Player 2 controls (right side)
        p2_hints = [
            "Player 2 Controls:",
            f"{(pygame.key.name(myinputmanager.player2_keys['up'])).upper()}{pygame.key.name(myinputmanager.player2_keys['left']).upper()}{pygame.key.name(myinputmanager.player2_keys['down']).upper()}{pygame.key.name(myinputmanager.player2_keys['right']).upper()} - Move",
            f"{(pygame.key.name(myinputmanager.player2_keys['attack']).upper())} - Select/Confirm; Attack",
            "ESC - Back to menu"
        ]
        
        for i, hint in enumerate(p2_hints):
            color = self.player2_color if i == 0 else (180, 180, 180)
            text = self.hint_font.render(hint, True, color)
            text_rect = text.get_rect()
            screen.blit(text, (1280 - text_rect.width - 20, 20 + i * 22))
    
    def render_transition_overlay(self, screen):
        """
        Render transition overlay when both players are ready
        """
        overlay = pygame.Surface((1280, 720))
        overlay.set_alpha(100)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Ready message
        ready_text = self.title_font.render("BOTH PLAYERS READY!", True, self.confirmed_color)
        ready_rect = ready_text.get_rect(center=(640, 300))
        screen.blit(ready_text, ready_rect)
        
        # Countdown or transition message
        transition_text = self.character_font.render("Proceeding to stage select...", True, (255, 255, 255))
        transition_rect = transition_text.get_rect(center=(640, 360))
        screen.blit(transition_text, transition_rect) 