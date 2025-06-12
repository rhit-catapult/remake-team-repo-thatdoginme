"""
Base Character - Foundation for all fighters
=============================================

This module contains the base Character class that all fighters inherit from.
Defines common properties, methods, and behaviors shared by all characters.

Key Features for Smooth Movement:
- Acceleration/deceleration-based movement (no instant velocity changes)
- Frame-based animation system with interpolation
- State machine for seamless action transitions
- Input buffering for responsive controls
- Physics-based momentum conservation
"""

import pygame
import numpy as np
from enum import Enum
import os

class CharacterState(Enum):
    """
    All possible character states for animation and behavior
    """
    IDLE = "idle"
    WALKING = "walking"
    RUNNING = "running"
    JUMPING = "jumping"
    FALLING = "falling"
    LANDING = "landing"
    CROUCHING = "crouching"
    
    # Attack states
    LIGHT_ATTACK = "light_attack"
    HEAVY_ATTACK = "heavy_attack"
    SIDE_SPECIAL = "side_special"
    UP_SPECIAL = "up_special"
    DOWN_SPECIAL = "down_special"
    NEUTRAL_SPECIAL = "neutral_special"
    
    # Defensive states
    BLOCKING = "blocking"
    HIT_STUN = "hit_stun"
    KNOCKDOWN = "knockdown"
    
    # Grab system
    GRABBING = "grabbing"
    GRABBED = "grabbed"

class Character:
    """
    Base class for all playable characters with smooth movement physics
    
    === COMPLETED SYSTEMS ===
    ✅ Movement physics with acceleration/deceleration (FIXED slow movement bug)
    ✅ Ground and air state management (FIXED stuck in midair bug)
    ✅ Jumping with coyote time and variable height
    ✅ Basic attack framework with frame data and hitbox creation
    ✅ Damage percentage system with knockback scaling (Smash Bros style)
    ✅ State machine for animations and behavior transitions
    ✅ Comprehensive debug output for troubleshooting physics issues
    ✅ KO and respawn system integration
    
    === TODO SYSTEMS ===
    - Complete attack hitbox/hurtbox collision detection with other players
    - Character-specific moves and stats (different character classes)
    - Advanced techniques (wavedashing, L-canceling, DI, etc.)
    - Grab system implementation (throw combos)
    - Shield/blocking mechanics with shield break
    - Multiple character classes with unique abilities and movesets
    - Sprite-based rendering system (currently using colored rectangles)
    - Sound effect integration for movement and attacks
    """
    
    def __init__(self, x, y, player_id, character_name="fighter"):
        """
        Initialize a character with smooth physics system
        """
        # Position and physics
        self.position = np.array([float(x), float(y)])
        self.velocity = np.array([0.0, 0.0])
        self.acceleration = np.array([0.0, 0.0])
        self.facing_right = True if player_id == 1 else False
        
        # === MOVEMENT PHYSICS CONSTANTS ===
        # These values were tuned to fix the "extremely slow movement" bug
        # Original values were too small (walk=3.0, run=6.0, accel=0.4)
        # The debug system revealed input was working but movement was imperceptible
        
        self.max_walk_speed = 8.0       # Base walking speed (increased from 3.0 for visibility)
        self.max_run_speed = 12.0       # Running speed when holding direction (increased from 6.0)  
        self.ground_acceleration = 1.2  # How quickly we reach max speed (increased from 0.4)
        self.ground_deceleration = 1.8  # How quickly we stop when no input (increased from 0.6)
        self.air_acceleration = 0.6     # Air control strength (increased from 0.2)
        self.air_deceleration = 0.3     # Air momentum preservation (increased from 0.1)
        
        # NOTE: These speeds work with the 60fps normalization in physics_manager.py
        # Movement formula: velocity * 60 * delta_time = pixels_per_frame
        self.jump_strength = 15.0
        self.short_hop_strength = 8.0   # For light jump inputs
        
        # Character stats (Smash Bros style - damage goes UP from 0%)
        self.lives = 3
        self.damage_percent = 0.0  # Starts at 0%, goes up when hit
        self.max_damage_percent = 999.0  # Theoretical max (usually KO'd before this)
        self.weight = 1.0  # Affects knockback and fall speed
        
        # Ground and collision state
        self.on_ground = True
        self.can_jump = True
        self.coyote_time = 0.0  # Brief time after leaving ground where you can still jump
        self.coyote_time_max = 0.1  # 6 frames at 60fps
        
        # State management
        self.current_state = CharacterState.IDLE
        self.previous_state = CharacterState.IDLE
        self.state_timer = 0.0
        self.can_act = True
        self.can_cancel = False  # For combo canceling
        
        # Combat properties
        self.is_attacking = False
        self.attack_state_frames = 0  # Current frame of attack
        self.hit_stun_timer = 0.0
        self.invincibility_timer = 0.0
        self.active_hitboxes = []
        self.current_attack = None  # Stores current attack data
        self.attack_hitbox_created = False  # Track if hitbox was created this attack
        
        # Animation system for smooth visuals
        self.animation_frame = 0.0  # Float for smooth interpolation
        self.animation_speed = 0.2   # Animation playback speed
        self.sprite_scale = 1.0      # For hit effects, etc.
        
        # Input buffering for responsive controls
        self.input_buffer = []
        self.buffer_time = 6  # frames to buffer inputs
        
        # Visual effects
        self.hit_flash_timer = 0.0
        self.screen_shake_intensity = 0.0
        
        # KO and respawn system
        self.is_ko = False
        self.ko_direction = None
        self.respawn_invincibility = 0
        
        self.player_id = player_id
        
        # Size for collision (will be overridden by sprites later)
        self.width = 60
        self.height = 80

        # Sprite management
        self.character_name = character_name.lower()
        self.sprites = {}
        self._load_sprites()
    
    def _load_sprites(self):
        """
        Load character sprites from assets folder
        """
        # The character select screen uses "Warrior", but the assets folder is "fighter sprites"
        # We'll handle that mapping here for now.
        asset_name = self.character_name
        if self.character_name == "warrior":
            asset_name = "fighter" # Remap "warrior" to "fighter" for assets
        
        sprite_path = os.path.join('assets', 'images', f'{asset_name} sprites')

        # Idle
        idle_path = os.path.join(sprite_path, f'{asset_name}-idle.png')
        if os.path.exists(idle_path):
            self.sprites['idle'] = [pygame.image.load(idle_path).convert_alpha()]
        else:
            self.sprites['idle'] = []

        # Walking
        self.sprites['walking'] = []
        for frame in ['a', 'b', 'c', 'd']:
            frame_path = os.path.join(sprite_path, f'{asset_name}-walking-{frame}.png')
            if os.path.exists(frame_path):
                self.sprites['walking'].append(pygame.image.load(frame_path).convert_alpha())

        # Landing and Hit Stun (b and d frames of walking)
        self.sprites['landing'] = []
        self.sprites['hit_stun'] = []
        landing_hit_frames = ['b', 'd']
        for frame in landing_hit_frames:
            frame_path = os.path.join(sprite_path, f'{asset_name}-walking-{frame}.png')
            if os.path.exists(frame_path):
                img = pygame.image.load(frame_path).convert_alpha()
                self.sprites['landing'].append(img)
                self.sprites['hit_stun'].append(img)

        # Running
        self.sprites['running'] = []
        for frame in ['a', 'b', 'c', 'd', 'e', 'f']:
            frame_path = os.path.join(sprite_path, f'{asset_name}-running-{frame}.png')
            if os.path.exists(frame_path):
                self.sprites['running'].append(pygame.image.load(frame_path).convert_alpha())

        # Jumping
        self.sprites['jumping'] = []
        # Look for the special jumping sprites
        jumping_sprite_names = ["GIMMEHEADTOP.png", "TOPHEADGIMME.png", "GIMMETOPHEAD.png"]
        for js_name in jumping_sprite_names:
            frame_path = os.path.join(sprite_path, js_name)
            if os.path.exists(frame_path):
                self.sprites['jumping'].append(pygame.image.load(frame_path).convert_alpha())
                break # Found one, no need to check others

        # No Weapon (for attacks)
        no_weapon_path = os.path.join(sprite_path, f'{asset_name}-no-weapon.png')
        if os.path.exists(no_weapon_path):
            self.sprites['no-weapon'] = [pygame.image.load(no_weapon_path).convert_alpha()]
        else:
            self.sprites['no-weapon'] = []
    
    def update(self, delta_time, player_input, stage):
        """
        Main update loop with smooth physics and responsive controls
        """
        # Update timers
        self.state_timer += delta_time
        self.hit_stun_timer = max(0, self.hit_stun_timer - delta_time)
        self.invincibility_timer = max(0, self.invincibility_timer - delta_time)
        self.coyote_time = max(0, self.coyote_time - delta_time)
        self.respawn_invincibility = max(0, self.respawn_invincibility - 1)  # Frame-based timer
        
        # Update visual effects
        self.hit_flash_timer = max(0, self.hit_flash_timer - delta_time)
        self.screen_shake_intensity *= 0.9  # Decay screen shake
        
        # Process input only if we can act (not in hitstun, etc.)
        if self.can_act and self.hit_stun_timer <= 0:
            self.handle_input(player_input)
        
        # Update physics
        self.update_physics(delta_time)
        
        # Update animations
        self.update_animations(delta_time)
        
        # Handle state transitions
        self.update_state_machine(delta_time)
        
        # Update attack frames
        if self.is_attacking:
            self.attack_state_frames += 1
            self.update_attack_timing()
    
    def handle_input(self, player_input):
        """
        Process player input with smooth movement and Smash-style attacks
        """
        print(f"🎮 Input P{self.player_id}: Processing input, on_ground={self.on_ground}")
        
        # Movement input with smooth acceleration
        horizontal_input = 0.0
        if player_input.is_pressed('left'):
            horizontal_input -= 1.0
            if self.facing_right:
                self.facing_right = False
            print(f"   ⬅️ Left input: {horizontal_input}")
        if player_input.is_pressed('right'):
            horizontal_input += 1.0
            if not self.facing_right:
                self.facing_right = True
            print(f"   ➡️ Right input: {horizontal_input}")
        
        print(f"   🏃 Total horizontal input: {horizontal_input}, facing_right: {self.facing_right}")
        
        # Apply movement based on ground state
        if self.on_ground:
            print(f"   🌍 Applying ground movement")
            self.apply_ground_movement(horizontal_input)
        else:
            print(f"   🌊 Applying air movement")
            self.apply_air_movement(horizontal_input)
        
        # Jumping with coyote time and short hops
        if player_input.was_just_pressed('up'):
            print(f"   🚀 Jump input detected")
            if self.on_ground or self.coyote_time > 0:
                # Short hop if released quickly, full jump if held
                jump_power = self.short_hop_strength if not player_input.is_pressed('up') else self.jump_strength
                print(f"   🚀 Jumping with power: {jump_power}")
                self.velocity[1] = -jump_power
                self.on_ground = False
                self.can_jump = False
                self.coyote_time = 0
                self.change_state(CharacterState.JUMPING)
        
        # Variable jump height - cut jump short if button released
        if not player_input.is_pressed('up') and self.velocity[1] < 0 and self.current_state == CharacterState.JUMPING:
            print(f"   ✂️ Cutting jump short")
            self.velocity[1] *= 0.5  # Cut jump height
        
        # Crouching
        if player_input.is_pressed('down') and self.on_ground:
            if self.current_state != CharacterState.CROUCHING:
                print(f"   ⬇️ Entering crouch")
                self.change_state(CharacterState.CROUCHING)
        elif self.current_state == CharacterState.CROUCHING:
            print(f"   ⬆️ Exiting crouch")
            self.change_state(CharacterState.IDLE)
        
        # Smash-style attack system (one button + direction)
        if player_input.was_just_pressed('attack'):
            attack_direction = player_input.get_attack_direction()
            print(f"   ⚔️ Attack input: {attack_direction}")
            self.perform_attack(attack_direction)
    
    def apply_ground_movement(self, horizontal_input):
        """
        Apply smooth ground movement with acceleration/deceleration
        
        === DEBUG SYSTEM EXPLANATION ===
        This method was heavily debugged to fix the "extremely slow movement" issue.
        The extensive print statements help track:
        1. Input values (horizontal_input)
        2. Current velocity and target speeds  
        3. Acceleration calculations and state changes
        4. Whether characters properly transition between idle/walking/running
        
        The debug output revealed that input was working but movement speeds were too small.
        """
        print(f"   🚶 Ground movement P{self.player_id}: input={horizontal_input}, vel_x={self.velocity[0]:.2f}")
        print(f"      MAX SPEEDS: walk={self.max_walk_speed}, run={self.max_run_speed}")
        print(f"      ACCELERATIONS: ground={self.ground_acceleration}, decel={self.ground_deceleration}")
        
        if horizontal_input != 0:
            # === MOVEMENT WITH INPUT ===
            # Calculate target speed based on input direction (-1 for left, +1 for right)
            target_speed = horizontal_input * self.max_walk_speed
            print(f"      🎯 Target walk speed: {target_speed}")
            
            # === RUNNING SYSTEM ===
            # Upgrade to running speed if already moving fast in same direction
            if abs(self.velocity[0]) > self.max_walk_speed * 0.8 and horizontal_input * self.velocity[0] > 0:
                target_speed = horizontal_input * self.max_run_speed
                print(f"      🏃 Target run speed: {target_speed}")
            
            # === SMOOTH ACCELERATION ===
            # Gradually change velocity towards target instead of instant changes
            speed_diff = target_speed - self.velocity[0]
            acceleration = self.ground_acceleration if abs(speed_diff) > 0.1 else self.ground_deceleration
            old_vel = self.velocity[0]
            self.velocity[0] += np.sign(speed_diff) * min(abs(speed_diff), acceleration)
            
            print(f"      📈 Speed diff: {speed_diff:.2f}, accel: {acceleration:.2f}, vel: {old_vel:.2f} -> {self.velocity[0]:.2f}")
            print(f"      📊 ABS VELOCITY: {abs(self.velocity[0])}")
            
            # === ANIMATION STATE UPDATES ===
            # Change visual state based on movement speed
            if abs(self.velocity[0]) > self.max_walk_speed * 1.2:
                print(f"      🏃 CHANGING TO RUNNING")
                self.change_state(CharacterState.RUNNING)
            elif abs(self.velocity[0]) > 0.5:
                print(f"      🚶 CHANGING TO WALKING")
                self.change_state(CharacterState.WALKING)
        else:
            # === NO INPUT - DECELERATION ===
            print(f"      ⏸️ No input - decelerating")
            # Gradually slow down when no input (creates smooth stopping)
            if abs(self.velocity[0]) > 0.1:
                old_vel = self.velocity[0]
                self.velocity[0] *= (1.0 - self.ground_deceleration)
                print(f"      📉 Decel: {old_vel:.2f} -> {self.velocity[0]:.2f}")
            else:
                # Stop completely when velocity is very small
                self.velocity[0] = 0
                if self.current_state in [CharacterState.WALKING, CharacterState.RUNNING]:
                    self.change_state(CharacterState.IDLE)
    
    def apply_air_movement(self, horizontal_input):
        """
        Apply smooth air movement with momentum conservation
        """
        if horizontal_input != 0:
            target_speed = horizontal_input * self.max_walk_speed * 0.8  # Reduced air speed
            speed_diff = target_speed - self.velocity[0]
            
            # Less air control for more realistic physics
            self.velocity[0] += np.sign(speed_diff) * min(abs(speed_diff), self.air_acceleration)
        else:
            # Very slow air deceleration to maintain momentum
            if abs(self.velocity[0]) > 0.1:
                self.velocity[0] *= (1.0 - self.air_deceleration)
    
    def update_physics(self, delta_time):
        """
        Update character physics - position updates are now handled by physics manager
        NOTE: Gravity and collision are now handled by the physics manager and stage system
        """
        print(f"📍 Character P{self.player_id} internal physics: on_ground={self.on_ground}, state={self.current_state}")
        
        # The physics manager now handles all position updates and gravity
        # This method is kept for any character-specific physics that don't involve position
        
        # Update coyote time for more forgiving jumping
        if not self.on_ground and self.coyote_time > 0:
            self.coyote_time -= delta_time
            if self.coyote_time <= 0:
                self.coyote_time = 0
                print(f"   ⏰ P{self.player_id} coyote time expired")
        
        # Handle landing state if character is now on ground
        if self.on_ground and self.current_state == CharacterState.FALLING:
            print(f"   🛬 P{self.player_id} landing from fall")
            self.change_state(CharacterState.LANDING)
            self.can_jump = True
    
    def change_state(self, new_state):
        """
        Change character state with proper transitions and animation resets
        """
        if new_state == self.current_state:
            return
        
        # Store previous state for combo/cancel checking
        self.previous_state = self.current_state
        self.current_state = new_state
        self.state_timer = 0.0
        self.animation_frame = 0.0
        
        # State-specific initialization
        if new_state == CharacterState.LANDING:
            # Brief landing lag
            self.can_act = False
            # Auto-transition to idle after short time
            if self.state_timer > 0.2:
                self.change_state(CharacterState.IDLE)
        elif new_state in [CharacterState.IDLE, CharacterState.WALKING, CharacterState.RUNNING]:
            self.can_act = True
            self.is_attacking = False
            self.attack_state_frames = 0
        elif new_state == CharacterState.FALLING:
            self.on_ground = False
    
    def perform_attack(self, direction):
        """
        Execute attack based on direction (Smash-style)
        """
        if not self.can_act or self.is_attacking:
            return
        
        print(f"Player {self.player_id} performing {direction} attack!")  # Debug
        
        self.is_attacking = True
        self.attack_state_frames = 0
        self.can_act = False
        
        # Set attack properties based on direction
        if direction == 'neutral':
            self.change_state(CharacterState.LIGHT_ATTACK)
            self.current_attack = {
                'type': 'neutral',
                'startup_frames': 6,
                'active_frames': 4,
                'recovery_frames': 8,
                'damage': 8,
                'knockback': 5
            }
        elif direction == 'side':
            self.change_state(CharacterState.HEAVY_ATTACK)
            self.current_attack = {
                'type': 'side',
                'startup_frames': 8,
                'active_frames': 5,
                'recovery_frames': 12,
                'damage': 12,
                'knockback': 8
            }
        elif direction == 'up':
            self.change_state(CharacterState.UP_SPECIAL)
            self.current_attack = {
                'type': 'up',
                'startup_frames': 10,
                'active_frames': 6,
                'recovery_frames': 15,
                'damage': 10,
                'knockback': 12
            }
        elif direction == 'down':
            self.change_state(CharacterState.DOWN_SPECIAL)
            self.current_attack = {
                'type': 'down',
                'startup_frames': 12,
                'active_frames': 3,
                'recovery_frames': 20,
                'damage': 15,
                'knockback': 10
            }
        
        # Store attack data for frame timing
        self.attack_hitbox_created = False
    
    def take_damage(self, damage, knockback_vector, attacker):
        """
        Handle taking damage with Smash Bros style percentage and scaling knockback
        """
        if self.invincibility_timer > 0 or self.respawn_invincibility > 0:
            return  # Invincible (either hit invincibility or respawn invincibility)
        
        # Apply damage (increase percentage)
        self.damage_percent += damage
        
        # Scale knockback based on damage percentage (like Smash Bros)
        # Base knockback scaling
        damage_multiplier = 1.0 + (self.damage_percent / 70.0)

        # Exponential scaling for high damage percentages
        if self.damage_percent > 100:
            # This will make knockback much stronger at higher percents
            high_percent_scaler = ((self.damage_percent - 80) / 50.0) ** 1.5
            damage_multiplier += high_percent_scaler

        scaled_knockback = [knockback_vector[0] * damage_multiplier / self.weight,
                           knockback_vector[1] * damage_multiplier / self.weight]
        self.velocity[0] += scaled_knockback[0]
        self.velocity[1] += scaled_knockback[1]
        
        # Enter hitstun (also scales with damage)
        hitstun_duration = (damage + self.damage_percent * 0.02) * 0.01
        self.hit_stun_timer = hitstun_duration
        self.can_act = False
        
        # Visual effects
        self.hit_flash_timer = 0.2
        self.screen_shake_intensity = damage * 0.5
        
        # Brief invincibility
        self.invincibility_timer = 0.3
        
        self.change_state(CharacterState.HIT_STUN)
        
        print(f"Player {self.player_id} took {damage} damage! Now at {self.damage_percent:.0f}%")
    
    def lose_life(self):
        """
        Called when a character is KO'd. Decrements lives and resets damage.
        """
        self.lives -= 1
        self.damage_percent = 0.0
        print(f"Player {self.player_id} lost a life! {self.lives} remaining.")
    
    def update_animations(self, delta_time):
        """
        Update animation frames for smooth visual feedback
        """
        self.animation_frame += self.animation_speed * 60 * delta_time
        
        # Loop animation based on state
        max_frames = self.get_animation_frame_count(self.current_state)
        if max_frames > 0 and self.animation_frame >= max_frames:
            if self.current_state in [CharacterState.IDLE, CharacterState.WALKING, CharacterState.RUNNING]:
                self.animation_frame = 0  # Loop these animations
            else:
                self.animation_frame = max_frames - 1  # Hold last frame
    
    def get_animation_frame_count(self, state):
        """
        Get number of animation frames for a state
        """
        if state in [CharacterState.IDLE, CharacterState.CROUCHING]:
            return len(self.sprites.get('idle', []))
        if state == CharacterState.WALKING:
            return len(self.sprites.get('walking', []))
        if state == CharacterState.RUNNING:
            # Fallback to walking animation if no running animation exists
            running_sprites = self.sprites.get('running', [])
            if running_sprites:
                return len(running_sprites)
            return len(self.sprites.get('walking', []))
        if state in [CharacterState.JUMPING, CharacterState.FALLING]:
            return len(self.sprites.get('jumping', []))
        if state in [CharacterState.LANDING, CharacterState.HIT_STUN]:
            return len(self.sprites.get('landing', []))
        
        # For attacks, we use the single 'no-weapon' sprite
        attack_states = [
            CharacterState.LIGHT_ATTACK, CharacterState.HEAVY_ATTACK,
            CharacterState.SIDE_SPECIAL, CharacterState.UP_SPECIAL,
            CharacterState.DOWN_SPECIAL, CharacterState.NEUTRAL_SPECIAL
        ]
        if state in attack_states:
            return 1 # Just one "no-weapon" frame

        frame_counts = {
        }
        return frame_counts.get(state, 1)
    
    def update_state_machine(self, delta_time):
        """
        Handle automatic state transitions
        """
        # Auto-transition from landing to idle
        if self.current_state == CharacterState.LANDING and self.state_timer > 0.2:
            self.change_state(CharacterState.IDLE)
            self.can_act = True
        
        # Transition from jumping to falling
        if self.current_state == CharacterState.JUMPING and self.velocity[1] > 0:
            self.change_state(CharacterState.FALLING)
        
        # End hitstun
        if self.current_state == CharacterState.HIT_STUN and self.hit_stun_timer <= 0:
            self.can_act = True
            if self.on_ground:
                self.change_state(CharacterState.IDLE)
            else:
                self.change_state(CharacterState.FALLING)
    
    def render(self, screen, camera_offset=(0, 0)):
        """
        Render character with smooth animations and effects
        """
        # Apply camera offset
        screen_x = self.position[0] - camera_offset[0]
        screen_y = self.position[1] - camera_offset[1]
        
        # Calculate sprite flipping
        flip_horizontal = not self.facing_right
        
        # Select the correct sprite sheet
        sprite_sheet = None
        is_attack_state = self.current_state in [
            CharacterState.LIGHT_ATTACK, CharacterState.HEAVY_ATTACK,
            CharacterState.SIDE_SPECIAL, CharacterState.UP_SPECIAL,
            CharacterState.DOWN_SPECIAL, CharacterState.NEUTRAL_SPECIAL
        ]

        if is_attack_state and 'no-weapon' in self.sprites and self.sprites['no-weapon']:
            sprite_sheet = self.sprites['no-weapon']
        elif self.current_state in [CharacterState.IDLE, CharacterState.CROUCHING] and 'idle' in self.sprites:
            sprite_sheet = self.sprites['idle']
        elif self.current_state == CharacterState.WALKING and 'walking' in self.sprites:
            sprite_sheet = self.sprites['walking']
        elif self.current_state == CharacterState.RUNNING:
            if 'running' in self.sprites and self.sprites['running']:
                sprite_sheet = self.sprites['running']
            elif 'walking' in self.sprites and self.sprites['walking']: # Fallback to walking
                sprite_sheet = self.sprites['walking']
        elif self.current_state in [CharacterState.JUMPING, CharacterState.FALLING]:
            if 'jumping' in self.sprites and self.sprites['jumping']:
                sprite_sheet = self.sprites['jumping']
        elif self.current_state == CharacterState.LANDING:
            if 'landing' in self.sprites and self.sprites['landing']:
                sprite_sheet = self.sprites['landing']
        elif self.current_state == CharacterState.HIT_STUN:
            if 'hit_stun' in self.sprites and self.sprites['hit_stun']:
                sprite_sheet = self.sprites['hit_stun']

        # Get current animation frame
        if sprite_sheet:
            frame_index = int(self.animation_frame) % len(sprite_sheet)
            image = sprite_sheet[frame_index]
            
            # Flip and scale
            image = pygame.transform.flip(image, flip_horizontal, False)
            image = pygame.transform.scale(image, (self.width, self.height))

            # Hit flash effect
            if self.hit_flash_timer > 0:
                flash_image = image.copy()
                flash_image.fill((255, 100, 100, 128), special_flags=pygame.BLEND_RGBA_MULT)
                image.blit(flash_image, (0, 0))

            # Center the sprite on the character's position
            rect = image.get_rect(center=(screen_x, screen_y - self.height / 2))
            screen.blit(image, rect)

        else:
             # Fallback to rectangle rendering if no sprite is found
            color_mod = (255, 255, 255) if self.hit_flash_timer <= 0 else (255, 200, 200)
            character_rect = pygame.Rect(
                screen_x - self.width // 2,
                screen_y - self.height,
                self.width,
                self.height
            )
            pygame.draw.rect(screen, color_mod, character_rect)

        # Direction indicator
        # face_color = (0, 255, 0) if self.facing_right else (255, 0, 0)
        # face_rect = pygame.Rect(
        #     screen_x + (10 if self.facing_right else -20),
        #     screen_y - self.height + 10,
        #     10, 10
        # )
        # pygame.draw.rect(screen, face_color, face_rect)
        
        # Debug: Show velocity as arrow
        # if abs(self.velocity[0]) > 0.1 or abs(self.velocity[1]) > 0.1:
        #     end_x = screen_x + self.velocity[0] * 3
        #     end_y = screen_y + self.velocity[1] * 3
        #     pygame.draw.line(screen, (255, 255, 0), 
        #                    (screen_x, screen_y), (end_x, end_y), 2)
        
        # Debug: Show attack hitboxes
        for hitbox in self.active_hitboxes:
            hitbox_rect = pygame.Rect(
                hitbox['x'] - camera_offset[0] - hitbox['width'] // 2,
                hitbox['y'] - camera_offset[1] - hitbox['height'] // 2,
                hitbox['width'],
                hitbox['height']
            )
            pygame.draw.rect(screen, (255, 0, 0), hitbox_rect, 3)  # Red hitbox
        
        # Debug: Show attack state
        if self.is_attacking and self.current_attack:
            attack_text = f"{self.current_attack['type']} F{self.attack_state_frames}"
            # This would need a font, but we'll add it to debug info later
    
    def get_collision_rect(self):
        """
        Get collision rectangle for physics
        """
        return pygame.Rect(
            self.position[0] - self.width // 2,
            self.position[1] - self.height,
            self.width,
            self.height
        )
    
    def is_on_ground(self):
        """
        Check if character is on ground
        """
        return self.on_ground
    
    def get_hurtboxes(self):
        """
        Get current vulnerability hurtboxes
        """
        # Simple single hurtbox for now
        return [pygame.Rect(
            self.position[0] - self.width // 2,
            self.position[1] - self.height,
            self.width,
            self.height
        )]
    
    def get_character_specific_stats(self):
        """
        Return character stats for UI display
        """
        return {
            "name": "Base Character",
            "health": f"{self.damage_percent:.0f}%",
            "state": self.current_state.value,
            "on_ground": self.on_ground,
            "velocity": f"({self.velocity[0]:.1f}, {self.velocity[1]:.1f})"
        }
    
    def update_attack_timing(self):
        """
        Handle attack frame timing and hitbox creation
        """
        if not self.current_attack:
            return
        
        startup = self.current_attack['startup_frames']
        active = self.current_attack['active_frames']
        recovery = self.current_attack['recovery_frames']
        
        # Check which phase we're in
        if self.attack_state_frames < startup:
            # Startup phase - no hitbox yet
            pass
        elif self.attack_state_frames < startup + active:
            # Active phase - create hitbox if not already created
            if not self.attack_hitbox_created:
                self.create_attack_hitbox()
                self.attack_hitbox_created = True
        elif self.attack_state_frames >= startup + active + recovery:
            # End attack
            self.end_attack()
    
    def create_attack_hitbox(self):
        """
        Create hitbox for the current attack
        """
        if not self.current_attack:
            return
        
        # Calculate hitbox position based on attack type and facing direction
        hitbox_offset_x = 60 if self.facing_right else -60
        hitbox_offset_y = -40
        
        # Different hitbox positions for different attacks
        if self.current_attack['type'] == 'up':
            hitbox_offset_x = 0
            hitbox_offset_y = -80
        elif self.current_attack['type'] == 'down':
            hitbox_offset_x = 0
            hitbox_offset_y = -10
        
        hitbox_x = self.position[0] + hitbox_offset_x
        hitbox_y = self.position[1] + hitbox_offset_y
        
        # Create hitbox data
        hitbox = {
            'x': hitbox_x,
            'y': hitbox_y,
            'width': 50,
            'height': 50,
            'damage': self.current_attack['damage'],
            'knockback': self.current_attack['knockback'],
            'knockback_angle': self.get_knockback_angle(),
            'owner': self,
            'frames_remaining': self.current_attack['active_frames']
        }
        
        self.active_hitboxes.append(hitbox)
        print(f"Created {self.current_attack['type']} attack hitbox!")  # Debug
    
    def get_knockback_angle(self):
        """
        Get knockback angle based on attack type
        """
        if self.current_attack['type'] == 'up':
            return -75  # Upward angle
        elif self.current_attack['type'] == 'down':
            return 45   # Downward angle
        else:
            return 0    # Horizontal
    
    def end_attack(self):
        """
        End the current attack and return to normal state
        """
        self.is_attacking = False
        self.can_act = True
        self.current_attack = None
        self.attack_hitbox_created = False
        
        # Return to appropriate state
        if self.on_ground:
            self.change_state(CharacterState.IDLE)
        else:
            self.change_state(CharacterState.FALLING)
        
        print(f"Player {self.player_id} attack ended")  # Debug 