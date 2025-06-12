"""
Warrior Character - Balanced Fighter
====================================

A well-rounded character with balanced stats and versatile moveset.
Good for beginners with reliable attacks and movement options.

Character Archetype: All-arounder
- Balanced speed, power, and defense
- Reliable special moves
- Good recovery options
- Moderate learning curve

TODO:
- Implement character-specific stats and abilities
- Create unique special move set
- Design signature combos and movement options
- Add character-specific animations and effects
"""

from .base_character import Character, CharacterState
import pygame
import numpy as np

class Warrior(Character):
    """
    Warrior character - balanced all-around fighter
    
    Special Moves:
    - Side Special: Sword Dash - Forward dash with sword strike
    - Up Special: Rising Slash - Upward sword attack with recovery
    - Down Special: Ground Slam - Powerful downward attack
    - Neutral Special: Energy Projectile - Ranged attack option
    """
    
    def __init__(self, x, y, player_id):
        """
        Initialize the Warrior character
        
        TODO:
        - Call parent constructor
        - Set warrior-specific stats
        - Initialize special move properties
        - Load warrior sprites and animations
        """
        super().__init__(x, y, player_id, "warrior")
        
        # Warrior-specific stats
        self.max_health = 120  # Slightly above average
        self.current_health = self.max_health
        self.weight = 1.0  # Balanced weight
        self.walk_speed = 3.5
        self.run_speed = 6.5
        self.jump_strength = 16.0
        self.air_speed = 4.0
        
        # Special move properties
        self.sword_dash_distance = 200
        self.sword_dash_damage = 12
        self.rising_slash_height = 250
        self.rising_slash_damage = 15
        self.ground_slam_damage = 18
        self.energy_projectile_speed = 8
        self.energy_projectile_damage = 8
        
        # Character name and description
        self.name = "Warrior"
        self.description = "A balanced fighter with sword techniques and energy attacks"
    
    def perform_side_special(self, direction):
        """
        Sword Dash - Forward dash attack
        
        TODO:
        - Change to attacking state
        - Apply forward momentum
        - Create hitbox during dash
        - Add invincibility frames at start
        - Play dash animation and sound effect
        """
        pass
    
    def perform_up_special(self):
        """
        Rising Slash - Recovery and attack move
        
        TODO:
        - Apply upward velocity for recovery
        - Create upward-angled hitbox
        - Enter special fall state after peak
        - Play rising slash animation
        - Can be used for recovery when off-stage
        """
        pass
    
    def perform_down_special(self):
        """
        Ground Slam - Powerful downward attack
        
        TODO:
        - If in air: fast downward movement with landing hitbox
        - If on ground: charged ground pound with shockwave
        - High damage but long recovery time
        - Create screen shake effect on hit
        """
        pass
    
    def perform_neutral_special(self):
        """
        Energy Projectile - Ranged attack
        
        TODO:
        - Create projectile object moving forward
        - Projectile travels across screen
        - Can be reflected by some attacks
        - Moderate damage, good for zoning
        """
        pass
    
    def get_character_specific_stats(self):
        """
        Return character-specific information for UI display
        
        TODO:
        - Return dict with character stats
        - Include move descriptions
        - Special properties and abilities
        """
        return {
            "name": self.name,
            "description": self.description,
            "archetype": "All-Arounder",
            "difficulty": "Beginner",
            "stats": {
                "speed": 7,
                "power": 7,
                "defense": 8,
                "recovery": 7
            },
            "special_moves": {
                "side": "Sword Dash",
                "up": "Rising Slash", 
                "down": "Ground Slam",
                "neutral": "Energy Projectile"
            }
        }
    
    def perform_attack(self, direction):
        """
        Warrior-specific attack implementation with unique movesets
        """
        if not self.can_act or self.is_attacking:
            return
        
        print(f"Warrior performing {direction} attack!")
        
        self.is_attacking = True
        self.attack_state_frames = 0
        self.can_act = False
        
        # Warrior-specific attacks with unique properties
        if direction == 'neutral':
            # Quick sword slash
            self.change_state(CharacterState.LIGHT_ATTACK)
            self.current_attack = {
                'type': 'sword_slash',
                'startup_frames': 5,
                'active_frames': 4,
                'recovery_frames': 6,
                'damage': 7,
                'knockback': 4,
                'range': 70
            }
        elif direction == 'side':
            # Powerful sword thrust
            self.velocity[0] = 0  # Stop movement to prevent sliding
            self.change_state(CharacterState.HEAVY_ATTACK)
            self.current_attack = {
                'type': 'sword_thrust',
                'startup_frames': 12,
                'active_frames': 6,
                'recovery_frames': 18,
                'damage': 15,
                'knockback': 10,
                'range': 90
            }
        elif direction == 'up':
            # Rising slash (good for anti-air)
            self.change_state(CharacterState.UP_SPECIAL)
            self.current_attack = {
                'type': 'rising_slash',
                'startup_frames': 8,
                'active_frames': 8,
                'recovery_frames': 20,
                'damage': 16,
                'knockback': 15,
                'range': 60,
                'launches_upward': True
            }
        elif direction == 'down':
            # Energy projectile (longer duration attack)
            self.change_state(CharacterState.DOWN_SPECIAL)
            self.current_attack = {
                'type': 'energy_projectile',
                'startup_frames': 20,  # Longer startup for projectile
                'active_frames': 5,    # Brief moment to create projectile
                'recovery_frames': 25, # Can't act while projectile is out
                'damage': 10,
                'knockback': 8,
                'range': 300,
                'is_projectile': True
            }
        
        self.attack_hitbox_created = False
    
    def create_attack_hitbox(self):
        """
        Warrior-specific hitbox creation with different properties per attack
        """
        if not self.current_attack:
            return
        
        attack_type = self.current_attack['type']
        
        if attack_type == 'energy_projectile':
            # Create a projectile instead of a normal hitbox
            self.create_projectile()
        else:
            # Normal melee attacks
            hitbox_range = self.current_attack.get('range', 60)
            hitbox_offset_x = hitbox_range if self.facing_right else -hitbox_range
            hitbox_offset_y = -40
            
            # Different hitbox positions for different attacks
            if attack_type == 'rising_slash':
                hitbox_offset_x = 20 if self.facing_right else -20
                hitbox_offset_y = -100
            elif attack_type == 'sword_thrust':
                hitbox_offset_y = -50
            
            hitbox_x = self.position[0] + hitbox_offset_x
            hitbox_y = self.position[1] + hitbox_offset_y
            
            # Create melee hitbox
            hitbox = {
                'x': hitbox_x,
                'y': hitbox_y,
                'width': 60,
                'height': 50,
                'damage': self.current_attack['damage'],
                'knockback': self.current_attack['knockback'],
                'knockback_angle': self.get_warrior_knockback_angle(),
                'owner': self,
                'frames_remaining': self.current_attack['active_frames'],
                'attack_type': attack_type
            }
            
            self.active_hitboxes.append(hitbox)
            print(f"Created {attack_type} hitbox!")
    
    def create_projectile(self):
        """
        Create a projectile for the Warrior's energy attack
        """
        projectile_speed = 8
        direction = 1 if self.facing_right else -1
        
        # Create projectile data
        projectile = {
            'x': self.position[0] + (40 * direction),
            'y': self.position[1] - 40,
            'width': 30,
            'height': 20,
            'damage': self.current_attack['damage'],
            'knockback': self.current_attack['knockback'],
            'knockback_angle': 0,
            'owner': self,
            'velocity_x': projectile_speed * direction,
            'velocity_y': 0,
            'lifetime': 60,  # 60 frames = 1 second
            'is_projectile': True,
            'attack_type': 'energy_projectile'
        }
        
        self.active_hitboxes.append(projectile)
        print(f"Warrior fired energy projectile!")
    
    def get_warrior_knockback_angle(self):
        """
        Get knockback angle for Warrior attacks
        """
        attack_type = self.current_attack['type']
        
        if attack_type == 'rising_slash':
            return -80  # Sharp upward
        elif attack_type == 'sword_thrust':
            return -10  # Slightly upward
        else:
            return 0    # Horizontal
    
    def update(self, delta_time, player_input, stage):
        """
        Override update to handle projectiles
        """
        # Call parent update
        super().update(delta_time, player_input, stage)
        
        # Update projectiles
        self.update_projectiles(delta_time)
    
    def update_projectiles(self, delta_time):
        """
        Update any active projectiles
        """
        projectiles_to_remove = []
        
        for hitbox in self.active_hitboxes:
            if hitbox.get('is_projectile', False):
                # Move projectile
                hitbox['x'] += hitbox['velocity_x']
                hitbox['y'] += hitbox['velocity_y']
                
                # Decrease lifetime
                hitbox['lifetime'] -= 1
                
                # Remove if lifetime expired or off-screen
                if hitbox['lifetime'] <= 0 or hitbox['x'] < -100 or hitbox['x'] > 1380:
                    projectiles_to_remove.append(hitbox)
        
        # Remove expired projectiles
        for projectile in projectiles_to_remove:
            if projectile in self.active_hitboxes:
                self.active_hitboxes.remove(projectile)
    
    def render(self, screen, camera_offset=(0, 0)):
        """
        Override render to show Warrior-specific visuals
        """
        # Call parent render
        super().render(screen, camera_offset)
        
        # Render projectiles with special effects
        for hitbox in self.active_hitboxes:
            if hitbox.get('is_projectile', False):
                proj_x = hitbox['x'] - camera_offset[0] - hitbox['width'] // 2
                proj_y = hitbox['y'] - camera_offset[1] - hitbox['height'] // 2
                
                # Energy projectile visual (glowing effect)
                for i in range(3):
                    pygame.draw.ellipse(screen, (0, 100 + i * 50, 255 - i * 30), 
                                      (proj_x - i, proj_y - i, 
                                       hitbox['width'] + i * 2, hitbox['height'] + i * 2)) 