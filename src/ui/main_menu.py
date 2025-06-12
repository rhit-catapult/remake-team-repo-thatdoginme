"""
Main Menu - Game's primary navigation interface
===============================================

The main menu provides access to all game modes and options.
Features an attractive interface with smooth animations.

Menu Options:
- Play (goes to character select)
- Options (settings and configuration)
- Quit (exit game)

TODO:
- Implement smooth menu navigation with keyboard/controller
- Add background animations and effects
- Create attractive button styling
- Add menu music and sound effects
- Implement smooth transitions to other states
"""

import pygame
from src.core.state_manager import GameState, GameStateType
from enum import Enum

class MenuOption(Enum):
    """
    Available menu options
    
    TODO: Expand as needed for additional features
    """
    PLAY = 0
    OPTIONS = 1
    QUIT = 2

class MainMenuState(GameState):
    """
    Main menu game state
    
    TODO: Implement full menu functionality with animations
    """
    
    def __init__(self, state_manager):
        """
        Initialize the main menu
        
        TODO:
        - Call parent constructor
        - Set up menu options and layout
        - Initialize fonts and graphics
        - Set up background elements
        """
        super().__init__(state_manager)
        
        self.selected_option = MenuOption.PLAY
        self.menu_options = list(MenuOption)
        
        # Menu styling (TODO: Load from theme/config)
        self.title_font = None  # TODO: Load large font for title
        self.menu_font = None   # TODO: Load medium font for options
        
        # Colors (TODO: Load from theme system)
        self.background_color = (20, 20, 40)
        self.title_color = (255, 255, 255)
        self.selected_color = (255, 200, 0)
        self.normal_color = (200, 200, 200)
        
        # Animation properties
        self.title_pulse_timer = 0.0
        self.menu_slide_offset = 0.0
        self.background_scroll = 0.0
        
        # Button layout
        self.button_spacing = 80
        self.button_start_y = 400
    
    def enter(self):
        """
        Called when entering main menu state
        
        TODO:
        - Initialize fonts if not already loaded
        - Start background music
        - Reset animation timers
        - Set up initial menu state
        """
        # TODO: Load fonts
        # self.title_font = pygame.font.Font("assets/fonts/title.ttf", 72)
        # self.menu_font = pygame.font.Font("assets/fonts/menu.ttf", 48)
        
        # TODO: Start background music
        # pygame.mixer.music.load("assets/audio/menu_theme.ogg")
        # pygame.mixer.music.play(-1)  # Loop indefinitely
        
        # Reset animations
        self.title_pulse_timer = 0.0
        self.menu_slide_offset = 0.0
        self.background_scroll = 0.0
    
    def exit(self):
        """
        Called when leaving main menu state
        
        TODO:
        - Stop background music
        - Clean up any resources
        """
        # TODO: Stop music
        # pygame.mixer.music.stop()
        pass
    
    def handle_event(self, event):
        """
        Handle main menu input events
        
        TODO:
        - Handle up/down navigation
        - Handle selection (Enter/Space)
        - Handle escape key
        - Support both keyboard and controller input
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.navigate_up()
                return True
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.navigate_down()
                return True
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.select_option()
                return True
            elif event.key == pygame.K_ESCAPE:
                self.selected_option = MenuOption.QUIT
                self.select_option()
                return True
        
        return False
    
    def navigate_up(self):
        """
        Navigate to previous menu option
        
        TODO:
        - Move selection up with wrapping
        - Play navigation sound effect
        - Trigger animation
        """
        current_index = self.selected_option.value
        new_index = (current_index - 1) % len(self.menu_options)
        self.selected_option = MenuOption(new_index)
        
        # TODO: Play sound effect
        # self.play_sound("menu_navigate.wav")
    
    def navigate_down(self):
        """
        Navigate to next menu option
        
        TODO:
        - Move selection down with wrapping
        - Play navigation sound effect
        - Trigger animation
        """
        current_index = self.selected_option.value
        new_index = (current_index + 1) % len(self.menu_options)
        self.selected_option = MenuOption(new_index)
        
        # TODO: Play sound effect
        # self.play_sound("menu_navigate.wav")
    
    def select_option(self):
        """
        Select the current menu option
        
        TODO:
        - Play selection sound
        - Trigger transition to appropriate state
        - Handle each menu option appropriately
        """
        # TODO: Play selection sound
        # self.play_sound("menu_select.wav")
        
        if self.selected_option == MenuOption.PLAY:
            # Transition to character select
            self.state_manager.change_state(GameStateType.CHARACTER_SELECT)
        elif self.selected_option == MenuOption.OPTIONS:
            # Transition to options menu
            self.state_manager.push_state(GameStateType.OPTIONS)
        elif self.selected_option == MenuOption.QUIT:
            # Exit the game
            # TODO: Implement proper game shutdown
            pygame.event.post(pygame.event.Event(pygame.QUIT))
    
    def update(self, delta_time):
        """
        Update main menu animations and logic
        
        TODO:
        - Update title pulsing animation
        - Update background scrolling
        - Update menu slide animations
        - Handle any particle effects
        """
        # Update animations
        self.title_pulse_timer += delta_time
        self.background_scroll += delta_time * 10  # Slow background movement
        
        # TODO: Update particle systems
        # TODO: Update any other visual effects
    
    def render(self, screen):
        """
        Render the main menu
        
        TODO:
        - Render animated background
        - Render game title with pulsing effect
        - Render menu options with highlighting
        - Add visual effects and polish
        """
        screen_width, screen_height = screen.get_size()
        
        # Clear screen with background color
        screen.fill(self.background_color)
        
        # TODO: Render animated background
        # self.render_background(screen)
        
        # Render game title
        self.render_title(screen, screen_width, screen_height)
        
        # Render menu options
        self.render_menu_options(screen, screen_width, screen_height)
        
        # TODO: Render additional effects
        # self.render_particles(screen)
    
    def render_title(self, screen, screen_width, screen_height):
        """
        Render the game title with effects
        
        TODO:
        - Render title text with pulsing animation
        - Add glow or shadow effects
        - Position centered at top of screen
        """
        # TODO: Create title surface with proper font
        # For now, use placeholder
        title_text = "SUPER SCUFFED FIGHTERS"
        
        # TODO: Calculate pulsing scale based on timer
        # pulse_scale = 1.0 + 0.1 * math.sin(self.title_pulse_timer * 2)
        
        # TODO: Render with proper font and effects
        # title_surface = self.title_font.render(title_text, True, self.title_color)
        # title_rect = title_surface.get_rect(center=(screen_width // 2, 150))
        # screen.blit(title_surface, title_rect)
    
    def render_menu_options(self, screen, screen_width, screen_height):
        """
        Render menu options with selection highlighting
        
        TODO:
        - Render each menu option
        - Highlight selected option
        - Add hover effects and animations
        """
        option_names = {
            MenuOption.PLAY: "PLAY",
            MenuOption.OPTIONS: "OPTIONS", 
            MenuOption.QUIT: "QUIT"
        }
        
        for i, option in enumerate(self.menu_options):
            # Calculate position
            y_pos = self.button_start_y + (i * self.button_spacing)
            
            # Choose color based on selection
            if option == self.selected_option:
                color = self.selected_color
                # TODO: Add selection visual effects
            else:
                color = self.normal_color
            
            # TODO: Render with proper font
            # text_surface = self.menu_font.render(option_names[option], True, color)
            # text_rect = text_surface.get_rect(center=(screen_width // 2, y_pos))
            # screen.blit(text_surface, text_rect)
            
            # TODO: Add selection indicator (arrow, glow, etc.)
    
    def render_background(self, screen):
        """
        Render animated background
        
        TODO:
        - Render scrolling background elements
        - Add particle effects
        - Create depth with parallax layers
        """
        # TODO: Implement animated background
        # Could include:
        # - Scrolling starfield
        # - Floating particles
        # - Geometric patterns
        # - Fighter silhouettes
        pass 