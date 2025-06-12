"""
Stage Select - Battle Arena Selection Interface
===============================================

Stage selection screen where Player 1 chooses the battle arena.
Features stage previews, descriptions, and selection controls.

Features:
- Stage preview images and descriptions
- Player 1 only controls (WASD + Space to select)
- Stage-specific information and hazard warnings
- Key hints for controls

Controls:
- Player 1: WASD to move cursor, Space to select
- ESC to go back to character select

Available Stages:
- Snowdin: A snowy castle with multiple platforms for vertical combat.
- Battlefield: Platform stage with hazards and ledges
"""

import pygame
from src.core.state_manager import GameState, GameStateType
from enum import Enum

class StageSelectState(GameState):
    """
    Stage selection screen controlled by Player 1
    """
    
    def __init__(self, state_manager):
        """
        Initialize stage select screen
        """
        super().__init__(state_manager)
        
        # Available stages
        self.stages = [
            {
                "name": "Snowdin",
                "description": "A snowy castle with multiple platforms for vertical combat.",
                "features": ["Multiple platforms", "No hazards", "Castle theme"],
                "difficulty": "Intermediate",
                "type": "plains",
                "icon": "assets/images/plains icon.png"
            },
            {
                "name": "Battlefield", 
                "description": "Classic platform stage with ledges and hazards",
                "features": ["Multiple platforms", "Ledge grabbing", "Fall-off zones"],
                "difficulty": "Intermediate",
                "type": "battlefield",
                "icon": "assets/images/battlefield icon.png"
            }
        ]
        
        # Selection state
        self.current_selection = 0
        self.confirmed_selection = None
        self.transition_timer = 0.0
        
        # Joystick navigation helpers
        self.last_joy_move_time = 0
        self.joy_move_delay = 200 # milliseconds
        
        # Visual properties
        self.stage_box_width = 400
        self.stage_box_height = 300
        self.stage_spacing = 100
        self.grid_start_x = 640 - (len(self.stages) * (self.stage_box_width + self.stage_spacing) - self.stage_spacing) // 2
        self.grid_y = 150
        
        # Load stage icons
        for stage in self.stages:
            if "icon" in stage:
                try:
                    stage["icon_surface"] = pygame.image.load(stage["icon"]).convert_alpha()
                except pygame.error:
                    stage["icon_surface"] = None
                    print(f"Warning: Could not load icon for {stage['name']}")
        
        # Load background
        try:
            self.background_image = pygame.image.load('assets/images/configselect.png').convert()
            self.background_image = pygame.transform.scale(self.background_image, (1280, 720))
        except pygame.error:
            self.background_image = None
            print("Warning: Could not load configselect.png for stage select.")
        
        # Colors
        self.selection_color = (255, 200, 0)  # Gold
        self.confirmed_color = (100, 255, 100)  # Green
        self.background_color = (20, 25, 40)
        
        # Fonts
        self.title_font = pygame.font.Font(None, 64)
        self.stage_font = pygame.font.Font(None, 36)
        self.info_font = pygame.font.Font(None, 24)
        self.hint_font = pygame.font.Font(None, 20)
    
    def enter(self):
        """
        Called when entering stage select
        """
        self.current_selection = 0
        self.confirmed_selection = None
        self.transition_timer = 0.0
        print("Entering stage select screen")
    
    def exit(self):
        """
        Called when leaving stage select
        """
        print("Exiting stage select screen")
    
    def handle_event(self, event):
        """
        Handle stage select input events
        """
        if self.confirmed_selection is not None:
            return False

        input_manager = self.game_engine.get_input_manager()

        # --- Handle Keyboard Input (Player 1 Only) ---
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a or event.key == pygame.K_f:
                self.move_cursor(-1)
            elif event.key == pygame.K_d or event.key == pygame.K_j:
                self.move_cursor(1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE or event.key == pygame.K_LSHIFT:
                self.confirm_selection()
            elif event.key == pygame.K_ESCAPE:
                self.state_manager.change_state(GameStateType.CHARACTER_SELECT)
            return True

        # --- Handle Joystick Input (Player 1 Only) ---
        player_id = input_manager.get_player_id_from_joystick(event.instance_id) if hasattr(event, 'instance_id') else None
        
        if player_id != 1:
            return False

        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 1: # P1 Attack button
                self.confirm_selection()
                return True

        if event.type == pygame.JOYAXISMOTION:
            if event.axis == 0: # Horizontal axis for L Joy-Con
                current_time = pygame.time.get_ticks()
                if current_time - self.last_joy_move_time > self.joy_move_delay:
                    if event.value < -0.5: # Left
                        self.move_cursor(-1)
                        self.last_joy_move_time = current_time
                    elif event.value > 0.5: # Right
                        self.move_cursor(1)
                        self.last_joy_move_time = current_time
                    return True

        return False

    def move_cursor(self, direction):
        """Move the selection cursor."""
        self.current_selection = (self.current_selection + direction) % len(self.stages)
        self.play_navigate_sound()

    def confirm_selection(self):
        """Confirm the stage selection."""
        self.confirmed_selection = self.current_selection
        self.transition_timer = 1.0
        self.play_confirm_sound()
        print(f"Selected stage: {self.stages[self.confirmed_selection]['name']}")
    
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
        Update stage select logic
        """
        if self.confirmed_selection is not None:
            self.transition_timer -= delta_time
            if self.transition_timer <= 0:
                # Store stage selection and proceed to the versus screen
                self.state_manager.selected_stage = self.stages[self.confirmed_selection]
                self.state_manager.change_state(GameStateType.VERSUS_SCREEN)
    
    def render(self, screen):
        """
        Render the stage select screen
        """
        if self.background_image:
            screen.blit(self.background_image, (0, 0))
        else:
            screen.fill(self.background_color)
        
        # Render title
        title_text = self.title_font.render("SELECT STAGE", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(640, 60))
        screen.blit(title_text, title_rect)
        
        # Render stage boxes
        for i, stage in enumerate(self.stages):
            self.render_stage_box(screen, stage, i)
        
        # Render selection cursor
        self.render_selection_cursor(screen)
        
        # Render stage details
        self.render_stage_details(screen)
        
        # Render control hints
        self.render_control_hints(screen)
        
        # Render transition overlay
        if self.confirmed_selection is not None:
            self.render_transition_overlay(screen)
    
    def render_stage_box(self, screen, stage, index):
        """
        Render individual stage selection box
        """
        box_x = self.grid_start_x + index * (self.stage_box_width + self.stage_spacing)
        box_y = self.grid_y
        
        # Stage box background
        box_rect = pygame.Rect(box_x, box_y, self.stage_box_width, self.stage_box_height)
        pygame.draw.rect(screen, (50, 55, 70), box_rect)
        pygame.draw.rect(screen, (255, 255, 255), box_rect, 2)
        
        # Stage preview (large colored area representing the stage)
        preview_rect = pygame.Rect(box_x + 20, box_y + 20, 360, 180)
        
        if "icon_surface" in stage and stage["icon_surface"]:
            # Use icon if available
            scaled_icon = pygame.transform.scale(stage["icon_surface"], (preview_rect.width, preview_rect.height))
            screen.blit(scaled_icon, preview_rect.topleft)
        else:
            # Fallback to colored box
            stage_colors = {
                "Snowdin": (180, 220, 255),      # Light blue for snow
                "Battlefield": (100, 100, 200)  # Blue battlefield
            }
            preview_color = stage_colors.get(stage["name"], (150, 150, 150))
            pygame.draw.rect(screen, preview_color, preview_rect)
        
        pygame.draw.rect(screen, (255, 255, 255), preview_rect, 2)
        
        # Draw stage-specific preview elements ONLY if no icon is loaded
        if not stage.get("icon_surface"):
            if stage["name"] == "Snowdin":
                # Simple flat ground
                ground_rect = pygame.Rect(box_x + 20, box_y + 170, 360, 30)
                pygame.draw.rect(screen, (80, 160, 80), ground_rect)
            elif stage["name"] == "Battlefield":
                # Multiple platforms
                main_platform = pygame.Rect(box_x + 100, box_y + 170, 200, 20)
                left_platform = pygame.Rect(box_x + 40, box_y + 120, 100, 15)
                right_platform = pygame.Rect(box_x + 260, box_y + 120, 100, 15)
                
                pygame.draw.rect(screen, (80, 80, 160), main_platform)
                pygame.draw.rect(screen, (60, 60, 140), left_platform)
                pygame.draw.rect(screen, (60, 60, 140), right_platform)
        
        # Stage name
        name_text = self.stage_font.render(stage["name"], True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(box_x + self.stage_box_width // 2, box_y + 220))
        screen.blit(name_text, name_rect)
        
        # Difficulty indicator
        difficulty_text = self.info_font.render(f"Difficulty: {stage['difficulty']}", True, (200, 200, 200))
        difficulty_rect = difficulty_text.get_rect(center=(box_x + self.stage_box_width // 2, box_y + 250))
        screen.blit(difficulty_text, difficulty_rect)
    
    def render_selection_cursor(self, screen):
        """
        Render selection cursor around current stage
        """
        if self.confirmed_selection is None:
            cursor_x = self.grid_start_x + self.current_selection * (self.stage_box_width + self.stage_spacing)
            cursor_rect = pygame.Rect(cursor_x - 5, self.grid_y - 5, self.stage_box_width + 10, self.stage_box_height + 10)
            pygame.draw.rect(screen, self.selection_color, cursor_rect, 5)
        else:
            # Show confirmed selection
            cursor_x = self.grid_start_x + self.confirmed_selection * (self.stage_box_width + self.stage_spacing)
            cursor_rect = pygame.Rect(cursor_x - 5, self.grid_y - 5, self.stage_box_width + 10, self.stage_box_height + 10)
            pygame.draw.rect(screen, self.confirmed_color, cursor_rect, 8)
    
    def render_stage_details(self, screen):
        """
        Render detailed information about the selected stage
        """
        selected_index = self.confirmed_selection if self.confirmed_selection is not None else self.current_selection
        stage = self.stages[selected_index]
        
        # Details panel
        panel_rect = pygame.Rect(100, 500, 1080, 170)
        pygame.draw.rect(screen, (40, 45, 60), panel_rect)
        pygame.draw.rect(screen, (255, 255, 255), panel_rect, 2)
        
        # Stage name and description
        name_text = self.stage_font.render(stage["name"], True, (255, 255, 255))
        screen.blit(name_text, (120, 520))
        
        desc_text = self.info_font.render(stage["description"], True, (200, 200, 200))
        screen.blit(desc_text, (120, 550))
        
        # Features list
        features_title = self.info_font.render("Features:", True, (255, 255, 255))
        screen.blit(features_title, (120, 580))
        
        for i, feature in enumerate(stage["features"]):
            feature_text = self.hint_font.render(f"• {feature}", True, (180, 180, 180))
            screen.blit(feature_text, (130, 605 + i * 18))
        
        # Show selected characters
        if hasattr(self.state_manager, 'selected_characters'):
            chars = self.state_manager.selected_characters
            char_info = self.info_font.render(
                f"P1: {chars['player1']['name']} vs P2: {chars['player2']['name']}", 
                True, (150, 150, 255)
            )
            char_rect = char_info.get_rect()
            screen.blit(char_info, (1280 - char_rect.width - 120, 520))
    
    def render_control_hints(self, screen):
        """
        Render control hints
        """
        hints = [
            "Player 1 Controls:",
            "F/J - Select stage",
            "Space - Confirm",
            "ESC - Back to character select"
        ]
        
        for i, hint in enumerate(hints):
            color = self.selection_color if i == 0 else (180, 180, 180)
            text = self.hint_font.render(hint, True, color)
            screen.blit(text, (20, 20 + i * 22))
    
    def render_transition_overlay(self, screen):
        """
        Render transition overlay when stage is confirmed
        """
        overlay = pygame.Surface((1280, 720))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Confirmation message
        stage_name = self.stages[self.confirmed_selection]['name']
        confirm_text = self.title_font.render(f"STAGE SELECTED: {stage_name.upper()}", True, self.confirmed_color)
        confirm_rect = confirm_text.get_rect(center=(640, 300))
        screen.blit(confirm_text, confirm_rect)
        
        # Starting message
        start_text = self.stage_font.render("Starting battle...", True, (255, 255, 255))
        start_rect = start_text.get_rect(center=(640, 360))
        screen.blit(start_text, start_rect) 