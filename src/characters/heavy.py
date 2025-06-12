"""
Heavy Character - Powerful Tank Fighter
=======================================

A slow but incredibly powerful character with high defense and devastating attacks.
Excels at controlling space and dealing massive damage.

Character Archetype: Grappler/Tank
- High health and defense
- Slow movement but powerful attacks
- Strong grab game and command grabs
- Armor on some attacks
- Intimidating presence

TODO:
- Implement super armor system
- Create devastating grab combos
- Design area-denial special moves
- Add charging/stance mechanics
- Create ground-shaking visual effects
"""

from .base_character import Character, CharacterState
import pygame
import numpy as np

class Heavy(Character):
    """
    Heavy character - slow but devastating fighter
    
    Special Moves:
    - Side Special: Charging Ram - Armored forward charge attack
    - Up Special: Ground Pound Jump - High jump with slam landing
    - Down Special: Seismic Slam - Area-of-effect ground attack
    - Neutral Special: Power Stance - Temporary armor and damage boost
    """
    
    def __init__(self, x, y, player_id):
        """
        Initialize the Heavy character
        
        TODO:
        - Call parent constructor
        - Set heavy-specific stats (high health, low speed)
        - Initialize armor and grab systems
        - Load heavy sprites and impact effects
        """
        super().__init__(x, y, player_id, "heavy")
        
        # Heavy-specific stats
        self.max_health = 160  # Much higher health
        self.current_health = self.max_health
        self.weight = 1.8  # Very heavy, hard to knock back
        self.walk_speed = 1.5  # Very slow, deliberate movement
        self.run_speed = 3.0   # Still very slow
        self.jump_strength = 16.0  # Higher jump to compensate for weight
        self.air_speed = 2.5   # Poor air mobility
        
        # Heavy-specific mechanics
        self.has_super_armor = False
        self.armor_timer = 0.0
        self.power_stance_active = False
        self.power_stance_timer = 0.0
        self.power_stance_duration = 5.0
        self.damage_multiplier = 1.0  # For armor stance damage reduction
        self.grab_range = 1.5  # Extended grab range
        
        # Special move properties
        self.charging_ram_speed = 8
        self.charging_ram_damage = 20
        self.charging_ram_armor_frames = 30
        self.ground_pound_height = 400
        self.ground_pound_damage = 25
        self.ground_pound_radius = 150
        self.seismic_slam_damage = 22
        self.seismic_slam_range = 200
        
        self.is_ground_pounding = False
        self.ground_pound_attack_data = None

        # Cooldown for Up Special
        self.up_special_cooldown = 0
        self.up_special_cooldown_duration = 600  # 10 seconds at 60fps
        
        # Character name and description
        self.name = "Heavy"
        self.description = "Massive fighter with devastating power and iron defense"
    
    def perform_attack(self, direction):
        """
        Heavy-specific attack implementation with powerful, slow attacks
        """
        if not self.can_act or self.is_attacking:
            return
        
        print(f"Heavy performing {direction} attack!")
        
        self.is_attacking = True
        self.attack_state_frames = 0
        self.can_act = False
        
        # Heavy-specific attacks - slow but devastating
        if direction == 'neutral':
            # Heavy punch with armor
            self.change_state(CharacterState.LIGHT_ATTACK)
            self.current_attack = {
                'type': 'heavy_punch',
                'startup_frames': 8,
                'active_frames': 6,
                'recovery_frames': 18,
                'damage': 18,
                'knockback': 9,
                'range': 75,
                'has_armor': True,
                'armor_frames': 10  # Armor during startup
            }
        elif direction == 'side':
            # Devastating hammer slam (now a body slam)
            self.change_state(CharacterState.HEAVY_ATTACK)
            self.current_attack = {
                'type': 'hammer_slam',
                'startup_frames': 12,
                'active_frames': 25, # Long active time for slide
                'recovery_frames': 30,
                'damage': 18, # Base damage
                'knockback': 8, # Base knockback
                'range': 0, # No hitbox created
                'has_armor': True,
                'armor_frames': 40,
                'is_body_slam': True # New property for physics manager
            }
        elif direction == 'up':
            # Ground pound with shockwave
            if self.up_special_cooldown > 0:
                print("Ground pound is on cooldown!")
                return
            
            self.velocity[1] = -self.jump_strength * 1.2  # A bit higher than a normal jump
            self.on_ground = False
            self.is_ground_pounding = True
            self.change_state(CharacterState.UP_SPECIAL)
            self.current_attack = {
                'type': 'ground_pound',
                'startup_frames': 5, # Quick startup
                'active_frames': 30, # Long active to allow for jump
                'recovery_frames': 30,
                'damage': 26,
                'knockback': 12,
                'range': 120,  # Wide area
                'has_shockwave': True
            }
            self.ground_pound_attack_data = self.current_attack.copy()
            self.up_special_cooldown = self.up_special_cooldown_duration # Start cooldown
        elif direction == 'down':
            # Armor stance (damage reduction + super armor)
            self.change_state(CharacterState.DOWN_SPECIAL)
            self.current_attack = {
                'type': 'armor_stance',
                'startup_frames': 10,
                'active_frames': 8,
                'recovery_frames': 12,
                'damage': 0,
                'knockback': 0,
                'range': 0,
                'is_stance': True,
                'stance_duration': 240  # 4 seconds
            }
        
        # Apply armor if attack has it
        if self.current_attack.get('has_armor', False):
            self.activate_super_armor(self.current_attack['armor_frames'])
        
        self.attack_hitbox_created = False
    
    def activate_super_armor(self, duration):
        """
        Activate super armor for the Heavy
        """
        self.has_super_armor = True
        self.armor_timer = duration
        print(f"Heavy activated super armor for {duration} frames!")
    
    def create_attack_hitbox(self):
        """
        Heavy-specific hitbox creation with area effects
        """
        if not self.current_attack:
            return
        
        attack_type = self.current_attack['type']
        
        if attack_type == 'armor_stance':
            # Apply armor stance buff
            self.apply_armor_stance()
        elif attack_type == 'hammer_slam':
            # No hitbox is created for the body slam.
            # Collision is handled in the physics manager.
            self.attack_hitbox_created = True
            return
        else:
            # Regular melee attacks but larger
            hitbox_range = self.current_attack.get('range', 75)
            hitbox_offset_x = hitbox_range if self.facing_right else -hitbox_range
            hitbox_offset_y = -50

            if attack_type == 'hammer_slam':
                hitbox_offset_x = 0
                hitbox_offset_y = -self.height / 2
            
            hitbox_x = self.position[0] + hitbox_offset_x
            hitbox_y = self.position[1] + hitbox_offset_y
            
            # Create large hitbox
            hitbox = {
                'x': hitbox_x,
                'y': hitbox_y,
                'width': 70,  # Larger than other characters
                'height': 60,
                'damage': self.current_attack['damage'],
                'knockback': self.current_attack['knockback'],
                'knockback_angle': self.get_heavy_knockback_angle(),
                'owner': self,
                'frames_remaining': self.current_attack['active_frames'],
                'attack_type': attack_type
            }
            
            self.active_hitboxes.append(hitbox)
            print(f"Created {attack_type} hitbox!")
    
    def create_ground_pound_hitbox(self):
        """
        Create ground pound area effect
        """
        if not self.ground_pound_attack_data:
            return

        # Large circular area around Heavy
        hitbox = {
            'x': self.position[0],
            'y': self.position[1] - 20,
            'width': 120,
            'height': 80,
            'damage': self.ground_pound_attack_data['damage'],
            'knockback': self.ground_pound_attack_data['knockback'],
            'knockback_angle': 45,  # Upward angle
            'owner': self,
            'frames_remaining': 10, # Short duration shockwave
            'attack_type': 'ground_pound',
            'is_area_attack': True
        }
        
        self.active_hitboxes.append(hitbox)
        self.ground_pound_attack_data = None
        print("Heavy created ground pound shockwave!")
    
    def apply_armor_stance(self):
        """
        Apply armor stance buff
        """
        self.power_stance_active = True
        self.power_stance_timer = self.current_attack['stance_duration']
        self.damage_multiplier = 0.5  # Take half damage
        self.has_super_armor = True
        self.armor_timer = self.current_attack['stance_duration']
        
        print("Heavy entered armor stance!")
    
    def get_heavy_knockback_angle(self):
        """
        Get knockback angle for Heavy attacks
        """
        attack_type = self.current_attack['type']
        
        if attack_type == 'ground_pound':
            return -60  # Strong upward
        elif attack_type == 'hammer_slam':
            return -20  # Slight upward
        else:
            return 0    # Horizontal
    
    def update(self, delta_time, player_input, stage):
        """
        Override update to handle armor and stance mechanics
        """
        # Update cooldowns
        if self.up_special_cooldown > 0:
            self.up_special_cooldown -= 1
        
        # Handle super armor timer
        if self.has_super_armor and self.armor_timer > 0:
            self.armor_timer -= 1
            if self.armor_timer <= 0:
                self.has_super_armor = False
                print("Heavy super armor ended")
        
        # Handle power stance timer
        if self.power_stance_active and self.power_stance_timer > 0:
            self.power_stance_timer -= 1
            if self.power_stance_timer <= 0:
                self.end_power_stance()
        
        # Handle ground pound landing
        if self.is_ground_pounding and self.on_ground:
            self.create_ground_pound_hitbox()
            self.is_ground_pounding = False
            self.end_attack()
        
        # Handle body slam attack movement
        if self.is_attacking and self.current_attack and self.current_attack.get('is_body_slam'):
            slide_speed = 9.0
            self.velocity[0] = slide_speed if self.facing_right else -slide_speed

            # --- New: Cancel slide on direction change ---
            horizontal_input = player_input.get_horizontal_axis()
            if (self.facing_right and horizontal_input < -0.5) or \
               (not self.facing_right and horizontal_input > 0.5):
                print("Body slam cancelled by changing direction!")
                self.velocity[0] = 0
                self.end_attack()

        # Handle sliding attack (old logic, can be removed or kept for other moves)
        if self.is_attacking and self.current_attack and self.current_attack.get('has_slide'):
            slide_speed = 5.0
            self.velocity[0] = slide_speed if self.facing_right else -slide_speed

        # Call parent update
        super().update(delta_time, player_input, stage)
    
    def end_power_stance(self):
        """
        End the power stance effect
        """
        self.power_stance_active = False
        self.damage_multiplier = 1.0
        self.has_super_armor = False
        
        print("Heavy armor stance ended")
    
    def end_attack(self):
        """
        Custom end_attack to handle ground pound.
        """
        if self.is_ground_pounding:
            # Don't end the attack if we are waiting to land for the ground pound.
            return
        super().end_attack()
    
    def take_damage(self, damage, knockback_vector, attacker):
        """
        Override damage handling for super armor
        """
        if self.has_super_armor:
            # Take damage but no knockback or hitstun
            self.damage_percent += damage * self.damage_multiplier
            
            # Visual effects but no knockback
            self.hit_flash_timer = 0.1
            
            print(f"Heavy absorbed hit with super armor! {damage * self.damage_multiplier:.1f} damage")
        else:
            # Normal damage handling
            super().take_damage(damage, knockback_vector, attacker)
    
    def render(self, screen, camera_offset=(0, 0)):
        """
        Override render to show Heavy-specific effects
        """
        # Call parent render
        super().render(screen, camera_offset)
        
        screen_x = self.position[0] - camera_offset[0]
        screen_y = self.position[1] - camera_offset[1]
        
        # Super armor visual effect
        if self.has_super_armor:
            # Draw armor glow around character
            armor_rect = pygame.Rect(
                screen_x - self.width // 2 - 5,
                screen_y - self.height - 5,
                self.width + 10,
                self.height + 10
            )
            pygame.draw.rect(screen, (255, 255, 255), armor_rect, 3)  # Gold outline
        
        # Power stance visual effect
        if self.power_stance_active:
            # Draw energy aura
            for i in range(3):
                aura_rect = pygame.Rect(
                    screen_x - self.width // 2 - (i * 3),
                    screen_y - self.height - (i * 3),
                    self.width + (i * 6),
                    self.height + (i * 6)
                )
                pygame.draw.rect(screen, (255, 100, 100, 100 - i * 30), aura_rect, 2)
        
        # Ground pound shockwave effect
        for hitbox in self.active_hitboxes:
            if hitbox.get('attack_type') == 'ground_pound':
                # Draw expanding shockwave rings
                import math
                for i in range(3):
                    radius = 40 + (self.attack_state_frames * 5) + (i * 20)
                    if radius < 100:
                        pygame.draw.circle(screen, (139, 69, 19, 150 - i * 50), 
                                         (int(screen_x), int(screen_y)), int(radius), 3) 