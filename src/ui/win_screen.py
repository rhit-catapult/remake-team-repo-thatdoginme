"""
Win Screen - Match Results Display
==================================

Post-match screen displaying the winner and match statistics.
Features victory animations, match results, and options to continue.

Features:
- Winner announcement with character display
- Match statistics and performance metrics
- Options to rematch or return to character select
- Celebration effects and animations

Controls:
- Space - Rematch (same characters, same stage)
- R - Return to character select
- ESC - Return to main menu
"""

import pygame
from src.core.state_manager import GameState, GameStateType
from enum import Enum
import os

class WinScreenState(GameState):
    """
    Win screen displaying match results
    """
    
    def __init__(self, state_manager):
        """
        Initialize win screen
        """
        super().__init__(state_manager)
        
        # Match results data
        self.winner = None           # 1 or 2
        self.loser = None           # 1 or 2  
        self.winner_character = None
        self.loser_character = None
        self.match_time = 0
        self.winner_damage = 0
        self.loser_damage = 0
        
        # Load background
        try:
            self.background_image = pygame.image.load('assets/images/configselect.png').convert()
            self.background_image = pygame.transform.scale(self.background_image, (1280, 720))
        except pygame.error:
            self.background_image = None
            print("Warning: Could not load configselect.png for win screen.")
        
        # Load character portraits
        self.character_portraits = {}
        char_names = ["Warrior", "Speedster", "Heavy"]
        for name in char_names:
            path = os.path.join('assets', 'images', 'portraits', f'{name}.png')
            if os.path.exists(path):
                self.character_portraits[name] = pygame.image.load(path).convert_alpha()
            else:
                self.character_portraits[name] = None
        
        # Animation state
        self.animation_timer = 0.0
        self.celebration_particles = []
        
        # Colors
        self.winner_color = (255, 215, 0)      # Gold
        self.loser_color = (150, 150, 150)     # Gray
        self.background_color = (15, 20, 35)
        self.particle_colors = [(255, 255, 100), (255, 200, 100), (255, 150, 100)]
        
        # Fonts
        self.title_font = pygame.font.Font(None, 96)
        self.winner_font = pygame.font.Font(None, 64)
        self.info_font = pygame.font.Font(None, 32)
        self.stat_font = pygame.font.Font(None, 24)
        self.hint_font = pygame.font.Font(None, 20)

        # Load victory sound
        try:
            self.victory_sound = pygame.mixer.Sound(os.path.join('assets', 'audio', 'battle end.mp3'))
        except pygame.error:
            self.victory_sound = None
            print("Warning: Could not load battle end.mp3")
    
    def enter(self):
        """
        Called when entering win screen
        """
        # Get match results from state manager
        if hasattr(self.state_manager, 'match_results'):
            results = self.state_manager.match_results
            self.winner = results.get('winner')
            self.loser = results.get('loser')
            self.winner_character = results.get('winner_character')
            self.loser_character = results.get('loser_character')
            self.match_time = results.get('match_time', 0)
            self.winner_damage = results.get('winner_damage', 0)
            self.loser_damage = results.get('loser_damage', 0)
        
        # Reset animation
        self.animation_timer = 0.0
        self.celebration_particles = []
        
        # Generate celebration particles
        for _ in range(50):
            self.add_celebration_particle()
        
        # Play victory music
        if self.victory_sound:
            self.victory_sound.play(loops=-1) # Loop indefinitely

        print(f"Win screen: Player {self.winner} wins!")
    
    def exit(self):
        """
        Called when leaving win screen
        """
        # Stop victory music
        if self.victory_sound:
            self.victory_sound.stop()
            
        print("Exiting win screen")
    
    def add_celebration_particle(self):
        """
        Add a celebration particle effect
        """
        import random
        particle = {
            'x': random.randint(0, 1280),
            'y': random.randint(-100, -20),
            'vx': random.uniform(-2, 2),
            'vy': random.uniform(2, 6),
            'color': random.choice(self.particle_colors),
            'size': random.randint(3, 8),
            'life': random.uniform(3.0, 6.0)
        }
        self.celebration_particles.append(particle)
    
    def handle_event(self, event):
        """
        Handle win screen input events
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Rematch with same settings
                print("Starting rematch...")
                self.state_manager.change_state(GameStateType.GAMEPLAY)
                return True
            elif event.key == pygame.K_r:
                # Return to character select
                print("Returning to character select...")
                self.state_manager.change_state(GameStateType.CHARACTER_SELECT)
                return True
            elif event.key == pygame.K_ESCAPE:
                # Return to main menu
                print("Returning to main menu...")
                self.state_manager.change_state(GameStateType.MAIN_MENU)
                return True
        
        return False
    
    def update(self, delta_time):
        """
        Update win screen animations
        """
        self.animation_timer += delta_time
        
        # Update celebration particles
        for particle in self.celebration_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= delta_time
            
            # Remove dead particles
            if particle['life'] <= 0 or particle['y'] > 720:
                self.celebration_particles.remove(particle)
        
        # Add new particles occasionally
        if len(self.celebration_particles) < 30 and self.animation_timer < 10.0:
            import random
            if random.random() < 0.3:  # 30% chance per frame
                self.add_celebration_particle()
    
    def render(self, screen):
        """
        Render the win screen
        """
        if self.background_image:
            screen.blit(self.background_image, (0, 0))
        else:
            screen.fill(self.background_color)
        
        # Render celebration particles
        self.render_particles(screen)
        
        # Render main victory message
        self.render_victory_message(screen)
        
        # Render character displays
        self.render_character_displays(screen)
        
        # Render match statistics
        self.render_match_stats(screen)
        
        # Render control hints
        self.render_control_hints(screen)
    
    def render_particles(self, screen):
        """
        Render celebration particle effects
        """
        for particle in self.celebration_particles:
            # Fade particles based on remaining life
            alpha = min(255, int(particle['life'] * 100))
            color = (*particle['color'], alpha)
            
            # Create surface for alpha blending
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2))
            particle_surface.set_alpha(alpha)
            particle_surface.fill(particle['color'])
            
            screen.blit(particle_surface, (particle['x'] - particle['size'], particle['y'] - particle['size']))
    
    def render_victory_message(self, screen):
        """
        Render main victory announcement
        """
        if self.winner:
            # Victory title
            victory_text = self.title_font.render("VICTORY!", True, self.winner_color)
            victory_rect = victory_text.get_rect(center=(640, 120))
            screen.blit(victory_text, victory_rect)
            
            # Winner announcement
            winner_text = self.winner_font.render(f"Player {self.winner} Wins!", True, self.winner_color)
            winner_rect = winner_text.get_rect(center=(640, 200))
            screen.blit(winner_text, winner_rect)
            
            # Character name
            if self.winner_character:
                char_text = self.info_font.render(f"Playing as {self.winner_character}", True, (255, 255, 255))
                char_rect = char_text.get_rect(center=(640, 240))
                screen.blit(char_text, char_rect)
    
    def render_character_displays(self, screen):
        """
        Render character display panels for winner and loser
        """
        # Winner panel (left side, larger)
        self.render_character_panel(screen, self.winner, self.winner_character, 
                                  200, 300, 300, 200, self.winner_color, "WINNER")
        
        # Loser panel (right side, smaller)
        self.render_character_panel(screen, self.loser, self.loser_character,
                                  780, 320, 250, 160, self.loser_color, "DEFEATED")
    
    def render_character_panel(self, screen, player, character, x, y, width, height, color, status):
        """
        Render individual character panel
        """
        if not player or not character:
            return
        
        # Panel background
        panel_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, (40, 45, 60), panel_rect)
        pygame.draw.rect(screen, color, panel_rect, 3)
        
        # Character portrait
        portrait = self.character_portraits.get(character)
        if portrait:
            target_width = width - 40
            target_height = height - 80
            original_width, original_height = portrait.get_size()

            if original_height > 0 and target_height > 0:
                original_aspect = original_width / original_height
                target_aspect = target_width / target_height

                if original_aspect > target_aspect:
                    # Image is wider than target: scale by height
                    new_height = target_height
                    new_width = int(new_height * original_aspect)
                    scaled_portrait = pygame.transform.scale(portrait, (new_width, new_height))
                    crop_x = (new_width - target_width) // 2
                    crop_y = 0
                else:
                    # Image is taller than target: scale by width
                    new_width = target_width
                    new_height = int(new_width / original_aspect)
                    scaled_portrait = pygame.transform.scale(portrait, (new_width, new_height))
                    crop_x = 0
                    crop_y = (new_height - target_height) // 2
                
                crop_area = pygame.Rect(crop_x, crop_y, target_width, target_height)
                cropped_portrait = scaled_portrait.subsurface(crop_area)
                dest_rect = cropped_portrait.get_rect(center=(x + width // 2, y + (height - 60) // 2))
                screen.blit(cropped_portrait, dest_rect)
            else:
                # Fallback to scaling if dimensions are unusual
                portrait_scaled = pygame.transform.scale(portrait, (target_width, target_height))
                portrait_rect = portrait_scaled.get_rect(center=(x + width // 2, y + (height - 60) // 2))
                screen.blit(portrait_scaled, portrait_rect)
        else:
            # Character portrait (colored rectangle)
            portrait_rect = pygame.Rect(x + 20, y + 20, width - 40, height - 80)
            character_colors = {
                "Warrior": (200, 150, 100),
                "Speedster": (255, 255, 100), 
                "Heavy": (150, 100, 200)
            }
            portrait_color = character_colors.get(character, (150, 150, 150))
            pygame.draw.rect(screen, portrait_color, portrait_rect)
            pygame.draw.rect(screen, color, portrait_rect, 2)
        
        # Character name
        name_text = self.info_font.render(character, True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(x + width // 2, y + height - 40))
        screen.blit(name_text, name_rect)
        
        # Status
        status_text = self.stat_font.render(status, True, color)
        status_rect = status_text.get_rect(center=(x + width // 2, y + height - 15))
        screen.blit(status_text, status_rect)
    
    def render_match_stats(self, screen):
        """
        Render match statistics
        """
        # Stats panel
        stats_rect = pygame.Rect(400, 520, 480, 120)
        pygame.draw.rect(screen, (30, 35, 50), stats_rect)
        pygame.draw.rect(screen, (255, 255, 255), stats_rect, 2)
        
        # Title
        stats_title = self.info_font.render("Match Statistics", True, (255, 255, 255))
        stats_title_rect = stats_title.get_rect(center=(640, 540))
        screen.blit(stats_title, stats_title_rect)
        
        # Statistics
        stats = [
            f"Match Time: {self.format_time(self.match_time)}",
            f"Winner Final Damage: {self.winner_damage:.0f}%",
            f"Loser Final Damage: {self.loser_damage:.0f}%"
        ]
        
        for i, stat in enumerate(stats):
            stat_text = self.stat_font.render(stat, True, (200, 200, 200))
            screen.blit(stat_text, (420, 570 + i * 20))
    
    def format_time(self, seconds):
        """
        Format time in MM:SS format
        """
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def render_control_hints(self, screen):
        """
        Render control hints
        """
        hints = [
            "Space - Rematch",
            "R - Character Select", 
            "ESC - Main Menu"
        ]
        
        # Center the hints at the bottom
        hint_y = 660
        for i, hint in enumerate(hints):
            text = self.hint_font.render(hint, True, (180, 180, 180))
            text_rect = text.get_rect(center=(640, hint_y + i * 22))
            screen.blit(text, text_rect) 