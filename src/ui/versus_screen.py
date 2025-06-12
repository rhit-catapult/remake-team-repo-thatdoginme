"""
Versus Screen - Pre-match matchup display
===========================================

A screen that appears before a match, showcasing the two characters
who are about to fight. It's designed to build anticipation.

Features:
- Displays both player characters with their names.
- A classic "VS" graphic in the center.
- Fades in and out for a smooth transition.
- Automatically proceeds to the game after a set time.
"""

import pygame
from src.core.state_manager import GameState, GameStateType
import os

class VersusScreenState(GameState):
    """
    Shows the two selected characters facing off.
    """

    def __init__(self, state_manager):
        """
        Initialize the versus screen.
        """
        super().__init__(state_manager)
        self.transition_duration = 4.0  # seconds
        self.timer = 0.0

        # Fonts
        self.title_font = pygame.font.Font(None, 128)
        self.player_font = pygame.font.Font(None, 64)
        self.char_name_font = pygame.font.Font(None, 48)

        # Colors
        self.background_color = (10, 10, 20)
        self.p1_color = (0, 150, 255)
        self.p2_color = (255, 50, 50)
        self.text_color = (255, 255, 255)
        self.vs_color = (255, 200, 0)

        # Character data
        self.p1_char = None
        self.p2_char = None
        
        # Load background
        try:
            self.background_image = pygame.image.load('assets/images/configselect.png').convert()
            self.background_image = pygame.transform.scale(self.background_image, (1280, 720))
        except pygame.error:
            self.background_image = None
            print("Warning: Could not load configselect.png for versus screen.")

        # Load versus music
        try:
            self.versus_music = pygame.mixer.Sound(os.path.join('assets', 'audio', 'versus.mp3'))
        except pygame.error:
            self.versus_music = None
            print("Warning: Could not load versus.mp3")

        # Load character portraits
        self.character_portraits = {}
        char_names = ["Warrior", "Speedster", "Heavy"]
        for name in char_names:
            path = os.path.join('assets', 'images', 'portraits', f'{name}.png')
            if os.path.exists(path):
                self.character_portraits[name] = pygame.image.load(path).convert_alpha()
            else:
                self.character_portraits[name] = None

    def enter(self):
        """
        Called when entering the versus screen.
        """
        self.timer = self.transition_duration
        if hasattr(self.state_manager, 'selected_characters'):
            self.p1_char = self.state_manager.selected_characters.get('player1')
            self.p2_char = self.state_manager.selected_characters.get('player2')
        
        if self.versus_music:
            self.versus_music.play()
            
        print("Entering Versus Screen")

    def exit(self):
        """
        Called when leaving the versus screen.
        """
        if self.versus_music:
            self.versus_music.stop()
            
        print("Exiting Versus Screen")

    def update(self, delta_time):
        """
        Update the timer and transition to gameplay when it's done.
        """
        self.timer -= delta_time
        if self.timer <= 0:
            self.state_manager.change_state(GameStateType.GAMEPLAY)

    def render(self, screen):
        """
        Render the versus screen.
        """
        if self.background_image:
            screen.blit(self.background_image, (0, 0))
        else:
            screen.fill(self.background_color)

        # --- Player 1 Display (Left) ---
        self.render_player_display(screen, "Player 1", self.p1_char, 320, self.p1_color, "left")

        # --- Player 2 Display (Right) ---
        self.render_player_display(screen, "Player 2", self.p2_char, 960, self.p2_color, "right")

        # --- VS Text ---
        vs_text = self.title_font.render("VS", True, self.vs_color)
        vs_rect = vs_text.get_rect(center=(640, 360))
        screen.blit(vs_text, vs_rect)
        
    def render_player_display(self, screen, player_text, char_data, x_center, color, side):
        """
        Renders the display for a single player.
        """
        if not char_data:
            return

        # Player Title
        player_title = self.player_font.render(player_text, True, color)
        player_rect = player_title.get_rect(center=(x_center, 150))
        screen.blit(player_title, player_rect)
        
        # Character Name
        char_name = self.char_name_font.render(char_data['name'], True, self.text_color)
        char_name_rect = char_name.get_rect(center=(x_center, 220))
        screen.blit(char_name, char_name_rect)

        # Character "Fighting Stance" Image
        portrait = self.character_portraits.get(char_data['name'])
        if portrait:
            image_width, image_height = 300, 300
            
            # Flip player 2's portrait
            if side == 'right':
                portrait = pygame.transform.flip(portrait, True, False)

            portrait_scaled = pygame.transform.scale(portrait, (image_width, image_height))
            portrait_rect = portrait_scaled.get_rect(center=(x_center, 420))
            screen.blit(portrait_scaled, portrait_rect)
            
            # Outline
            pygame.draw.rect(screen, color, portrait_rect, 5, border_radius=15)
        else:
            # Placeholder if image is missing
            image_width, image_height = 300, 300
            image_rect = pygame.Rect(0, 0, image_width, image_height)
            image_rect.center = (x_center, 420)
            
            character_colors = {
                "Warrior": (200, 150, 100),
                "Speedster": (255, 255, 100),
                "Heavy": (150, 100, 200)
            }
            char_color = character_colors.get(char_data['name'], (150, 150, 150))

            pygame.draw.rect(screen, char_color, image_rect, border_radius=15)
            pygame.draw.rect(screen, color, image_rect, 5, border_radius=15) 