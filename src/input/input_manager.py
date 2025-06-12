"""
Input Manager - Player Input Handling System
=============================================

Handles all player input including keyboard controls for both players.
Supports configurable key mappings and input buffering for fighting game mechanics.

Player Controls (Smash-style):
- Player 1: WASD movement + Q for attack (direction + Q = different attacks)
- Player 2: IJKL movement + U for attack (direction + U = different attacks)

Attack Types:
- No direction + Attack = Neutral attack
- Side + Attack = Side attack
- Up + Attack = Up attack  
- Down + Attack = Down attack

Key Features:
- Input buffering for frame-perfect combo execution
- "Just pressed" and "just released" detection
- Smooth input handling for responsive movement
- Directional attack detection like Smash Bros

TODO:
- Implement input buffering for combo execution
- Add input recording for replay system
- Handle simultaneous inputs properly
- Add configurable key bindings
- Implement input lag compensation
- Add gamepad support for future expansion

Fighting Game Input Concepts:
- Input buffering: Allow inputs to be registered slightly before they can be executed
- Input priority: Handle conflicting inputs (e.g., left+right pressed simultaneously)
- Special move detection: Quarter circle, half circle, and charge motions
"""

import pygame
from enum import Enum

# Define constants for Joy-Con button mappings to make code more readable
# These may need adjustment depending on the OS and Pygame/SDL version
JOYCON_L_BUTTON_MAP = {
    "dpad_up": 0,
    "dpad_down": 1,
    "dpad_left": 2,
    "dpad_right": 3,
    "sl": 4,
    "sr": 5,
    "minus": 8,
    "stick": 10,
    "capture": 13,
    "l": 14,
    "zl": 15,
}

AXIS_THRESHOLD = 0.5  # Deadzone for analog sticks

class InputAction(Enum):
    """
    All possible input actions in the game
    """
    # Movement
    MOVE_LEFT = "left"
    MOVE_RIGHT = "right"
    JUMP = "up"
    CROUCH = "down"
    
    # Attacks (Smash-style)
    ATTACK = "attack"
    
    # System actions
    PAUSE = "pause"
    GRAB = "grab"

class PlayerInput:
    """
    Represents the current input state for a single player with buffering
    """
    
    def __init__(self):
        """
        Initialize player input state with buffering system
        """
        # Current frame input states
        self.current_inputs = {}
        self.previous_inputs = {}
        
        # Initialize all inputs to False
        for action in ['left', 'right', 'up', 'down', 'attack', 'grab']:
            self.current_inputs[action] = False
            self.previous_inputs[action] = False
        
        # Input buffer for frame-perfect inputs (stores last 6 frames)
        self.input_buffer = []
        self.buffer_size = 6
        
        # Direction input for analog-style movement
        self.horizontal_axis = 0.0  # -1.0 to 1.0
        self.vertical_axis = 0.0    # -1.0 to 1.0
        self.joystick = None
    
    def update(self, key_states, key_mapping):
        """
        Update input state based on current key presses
        """
        # Store previous frame inputs
        self.previous_inputs = self.current_inputs.copy()
        
        # Update current inputs based on key states
        self.current_inputs['left'] = key_states[key_mapping['left']]
        self.current_inputs['right'] = key_states[key_mapping['right']]
        self.current_inputs['up'] = key_states[key_mapping['up']]
        self.current_inputs['down'] = key_states[key_mapping['down']]
        self.current_inputs['attack'] = key_states[key_mapping['attack']]
        self.current_inputs['grab'] = key_states[key_mapping['grab']]
        
        # Update directional axes for smooth movement
        self.horizontal_axis = 0.0
        if self.current_inputs['left']:
            self.horizontal_axis -= 1.0
        if self.current_inputs['right']:
            self.horizontal_axis += 1.0
        
        self.vertical_axis = 0.0
        if self.current_inputs['up']:
            self.vertical_axis -= 1.0
        if self.current_inputs['down']:
            self.vertical_axis += 1.0
        
        # Add current frame to input buffer
        self.input_buffer.append(self.current_inputs.copy())
        if len(self.input_buffer) > self.buffer_size:
            self.input_buffer.pop(0)
    
    def update_from_joystick(self, joy_mapping, axis_map={'h': 0, 'v': 1}):
        """
        Update input state based on current joystick state
        """
        if not self.joystick:
            return

        self.previous_inputs = self.current_inputs.copy()

        # Update directional axes from joystick based on user logs.
        # Axis 0 is horizontal, Axis 1 is vertical.
        self.horizontal_axis = self.joystick.get_axis(0)
        self.vertical_axis = self.joystick.get_axis(1)

        # Apply deadzone
        if abs(self.horizontal_axis) < AXIS_THRESHOLD:
            self.horizontal_axis = 0.0
        if abs(self.vertical_axis) < AXIS_THRESHOLD:
            self.vertical_axis = 0.0

        # Update current inputs from joystick axes
        self.current_inputs['left'] = self.horizontal_axis < -AXIS_THRESHOLD
        self.current_inputs['right'] = self.horizontal_axis > AXIS_THRESHOLD
        self.current_inputs['up'] = self.vertical_axis < -AXIS_THRESHOLD
        self.current_inputs['down'] = self.vertical_axis > AXIS_THRESHOLD
        
        # Update buttons from joystick
        self.current_inputs['attack'] = self.joystick.get_button(joy_mapping['attack'])
        self.current_inputs['grab'] = self.joystick.get_button(joy_mapping['grab'])

        # Add current frame to input buffer
        self.input_buffer.append(self.current_inputs.copy())
        if len(self.input_buffer) > self.buffer_size:
            self.input_buffer.pop(0)

    def assign_joystick(self, joystick):
        self.joystick = joystick

    def unassign_joystick(self):
        self.joystick = None
    
    def is_pressed(self, action):
        """
        Check if an action is currently pressed
        """
        result = self.current_inputs.get(action, False)
        if result:  # Only print when keys are actually pressed to avoid spam
            print(f"🔑 Input detected: {action} = {result}")
        return result
    
    def was_just_pressed(self, action):
        """
        Check if an action was pressed this frame (rising edge)
        """
        current = self.current_inputs.get(action, False)
        previous = self.previous_inputs.get(action, False)
        return current and not previous
    
    def was_just_released(self, action):
        """
        Check if an action was released this frame (falling edge)
        """
        current = self.current_inputs.get(action, False)
        previous = self.previous_inputs.get(action, False)
        return not current and previous
    
    def get_attack_direction(self):
        """
        Get the direction for attack input (like Smash Bros)
        Returns: 'neutral', 'side', 'up', 'down', or special versions
        """
        is_special = self.is_pressed('grab') # Using 'grab' as the special button

        if self.is_pressed('up'):
            return 'up_special' if is_special else 'up'
        elif self.is_pressed('down'):
            return 'down_special' if is_special else 'down'
        elif self.is_pressed('left') or self.is_pressed('right'):
            return 'side_special' if is_special else 'side'
        else:
            return 'neutral_special' if is_special else 'neutral'
    
    def was_pressed_in_buffer(self, action, frames_back=None):
        """
        Check if an action was pressed within the input buffer window
        """
        if frames_back is None:
            frames_back = self.buffer_size
        
        frames_to_check = min(frames_back, len(self.input_buffer))
        for i in range(frames_to_check):
            frame_inputs = self.input_buffer[-(i+1)]
            if frame_inputs.get(action, False):
                return True
        return False
    
    def get_horizontal_axis(self):
        """
        Get horizontal input as a float (-1.0 to 1.0)
        """
        return self.horizontal_axis
    
    def get_vertical_axis(self):
        """
        Get vertical input as a float (-1.0 to 1.0)
        """
        return self.vertical_axis

class InputManager:
    """
    Manages input for all players and global game inputs
    """
    
    def __init__(self):
        """
        Initialize the input manager with keyboard and single Joy-Con support.
        """
        # --- Keyboard Mappings ---
        self.player1_keys = {
            'left': pygame.K_a,
            'right': pygame.K_d,
            'up': pygame.K_w,
            'down': pygame.K_s,
            'attack': pygame.K_LSHIFT,      # One attack button
            'grab': pygame.K_e
        }
        
        self.player2_keys = {
            'left': pygame.K_l,
            'right': pygame.K_QUOTE,
            'up': pygame.K_p,
            'down': pygame.K_SEMICOLON,
            'attack': pygame.K_RSHIFT,      # One attack button
            'grab': pygame.K_o
        }
        
        # --- Joystick Mappings (Left Joy-Con held sideways) ---
        self.player1_joy_map = {
            'attack': JOYCON_L_BUTTON_MAP['dpad_down'], # Remapped to physical "down" button
            'grab': JOYCON_L_BUTTON_MAP['sl']
        }

        # --- Joystick Mappings (Xbox Controller) ---
        self.player2_xbox_map = {
            'attack': 0, # A button
            'grab': 2    # X button
        }

        # Global keys
        self.global_keys = {
            'pause': pygame.K_ESCAPE
        }
        
        # Player input objects
        self.player1_input = PlayerInput()
        self.player2_input = PlayerInput()
        
        # Joystick handling
        pygame.joystick.init()
        self.joysticks = {}
        self.player1_joy_id = None
        self.player2_joy_id = None

        # Current keyboard state
        self.keys_pressed = pygame.key.get_pressed()
        
        # Global input states
        self.pause_pressed = False
        self.pause_just_pressed = False
    
    def assign_players_to_joysticks(self):
        """Assigns players to available joysticks."""
        p1_assigned = self.player1_joy_id is not None
        p2_assigned = self.player2_joy_id is not None

        for instance_id, joy in self.joysticks.items():
            name = joy.get_name()
            if "Joy-Con (L)" in name and not p1_assigned:
                self.assign_joystick_to_player(instance_id, 1)
                p1_assigned = True
            elif "Xbox" in name and not p2_assigned:
                self.assign_joystick_to_player(instance_id, 2)
                p2_assigned = True

    def assign_joystick_to_player(self, instance_id, player_id):
        """Assigns a joystick to a player."""
        joystick = self.joysticks.get(instance_id)
        if not joystick:
            print(f"Warning: Tried to assign non-existent joystick with instance ID {instance_id}")
            return

        if player_id == 1:
            if self.player1_joy_id is not None:
                self.player1_input.unassign_joystick()
            self.player1_joy_id = instance_id
            self.player1_input.assign_joystick(joystick)
            print(f"Assigned joystick '{joystick.get_name()}' to Player 1")
        elif player_id == 2:
            if self.player2_joy_id is not None:
                self.player2_input.unassign_joystick()
            self.player2_joy_id = instance_id
            self.player2_input.assign_joystick(joystick)
            print(f"Assigned joystick '{joystick.get_name()}' to Player 2")

    def unassign_joystick_from_player(self, instance_id):
        """Unassigns a joystick from a player."""
        if self.player1_joy_id == instance_id:
            self.player1_input.unassign_joystick()
            self.player1_joy_id = None
            print(f"Unassigned joystick from Player 1")
        elif self.player2_joy_id == instance_id:
            self.player2_input.unassign_joystick()
            self.player2_joy_id = None
            print(f"Unassigned joystick from Player 2")
            
    def handle_event(self, event):
        """
        Handle pygame input events for immediate response actions
        """
        if event.type == pygame.KEYDOWN:
            if event.key == self.global_keys['pause']:
                self.pause_just_pressed = True
        elif event.type == pygame.KEYUP:
            if event.key == self.global_keys['pause']:
                self.pause_just_pressed = False
        
        elif event.type == pygame.JOYDEVICEADDED:
            joy = pygame.joystick.Joystick(event.device_index)
            instance_id = joy.get_instance_id()
            self.joysticks[instance_id] = joy
            print(f"Joystick connected: {joy.get_name()}")
            self.assign_players_to_joysticks()
        
        elif event.type == pygame.JOYDEVICEREMOVED:
            print(f"Joystick disconnected (Instance ID: {event.instance_id})")
            if event.instance_id in self.joysticks:
                del self.joysticks[event.instance_id]
            self.unassign_joystick_from_player(event.instance_id)

    def update(self):
        """
        Update input system each frame
        """
        # Get current keyboard state
        self.keys_pressed = pygame.key.get_pressed()
        
        # Check if any movement keys are pressed (for debugging)
        any_p1_movement = (self.keys_pressed[self.player1_keys['left']] or 
                          self.keys_pressed[self.player1_keys['right']] or
                          self.keys_pressed[self.player1_keys['up']] or
                          self.keys_pressed[self.player1_keys['down']])
        any_p2_movement = (self.keys_pressed[self.player2_keys['left']] or 
                          self.keys_pressed[self.player2_keys['right']] or
                          self.keys_pressed[self.player2_keys['up']] or
                          self.keys_pressed[self.player2_keys['down']])
        
        if any_p1_movement:
            print(f"⌨️ Raw P1 keys: A={self.keys_pressed[self.player1_keys['left']]}, D={self.keys_pressed[self.player1_keys['right']]}, W={self.keys_pressed[self.player1_keys['up']]}, S={self.keys_pressed[self.player1_keys['down']]}")
        if any_p2_movement:
            print(f"⌨️ Raw P2 keys: J={self.keys_pressed[self.player2_keys['left']]}, L={self.keys_pressed[self.player2_keys['right']]}, I={self.keys_pressed[self.player2_keys['up']]}, K={self.keys_pressed[self.player2_keys['down']]}")
        
        # Update global inputs
        self.pause_pressed = self.keys_pressed[self.global_keys['pause']]
        
        # Update player inputs
        # Player 1 uses joystick if available, otherwise keyboard
        if self.player1_joy_id is not None:
            self.player1_input.update_from_joystick(self.player1_joy_map)
        else:
            self.player1_input.update(self.keys_pressed, self.player1_keys)
        
        # Player 2 uses joystick if available, otherwise keyboard
        if self.player2_joy_id is not None:
            self.player2_input.update_from_joystick(self.player2_xbox_map)
        else:
            self.player2_input.update(self.keys_pressed, self.player2_keys)
    
    def get_player_input(self, player_id):
        """
        Get input state for a specific player (1 or 2)
        """
        if player_id == 1:
            return self.player1_input
        elif player_id == 2:
            return self.player2_input
        else:
            raise ValueError(f"Invalid player_id: {player_id}. Must be 1 or 2.")
    
    def get_player_id_from_joystick(self, instance_id):
        """
        Returns the player ID (1 or 2) associated with a joystick instance ID.
        """
        if instance_id == self.player1_joy_id:
            return 1
        if instance_id == self.player2_joy_id:
            return 2
        return None
    
    def is_pause_pressed(self):
        """
        Check if pause is currently pressed
        """
        return self.pause_pressed
    
    def was_pause_just_pressed(self):
        """
        Check if pause was just pressed this frame
        """
        return self.pause_just_pressed
    
    def configure_keys(self, player_id, key_mapping):
        """
        Configure key mappings for a player
        """
        if player_id == 1:
            self.player1_keys.update(key_mapping)
        elif player_id == 2:
            self.player2_keys.update(key_mapping)
        else:
            raise ValueError(f"Invalid player_id: {player_id}. Must be 1 or 2.")
    
    def detect_special_move(self, player_id, move_pattern):
        """
        Detect special move input patterns (quarter circles, etc.)
        
        TODO: Implement complex motion detection
        - Quarter circle forward (236): Down, Down-Forward, Forward + Attack
        - Quarter circle back (214): Down, Down-Back, Back + Attack
        - Dragon punch (623): Forward, Down, Down-Forward + Attack
        - Half circle (63214 or 41236): complex motions
        """
        player_input = self.get_player_input(player_id)
        
        # For now, return simple detection
        # This would be expanded with complex motion detection
        if move_pattern == "quarter_circle_forward":
            # Simplified: just check if down and forward were pressed recently
            return (player_input.was_pressed_in_buffer('down', 4) and 
                   player_input.was_pressed_in_buffer('right', 2))
        elif move_pattern == "quarter_circle_back":
            return (player_input.was_pressed_in_buffer('down', 4) and 
                   player_input.was_pressed_in_buffer('left', 2))
        
        return False
    
    def get_input_display_string(self, player_id):
        """
        Get a string representation of current inputs (for debugging/training mode)
        """
        player_input = self.get_player_input(player_id)
        display = []
        
        if player_input.is_pressed('left'):
            display.append('←')
        if player_input.is_pressed('right'):
            display.append('→')
        if player_input.is_pressed('up'):
            display.append('↑')
        if player_input.is_pressed('down'):
            display.append('↓')
        
        if player_input.is_pressed('attack'):
            display.append('A')
        if player_input.is_pressed('grab'):
            display.append('G')
        
        return ''.join(display) if display else '·'
    
    def reset_player_input(self, player_id):
        """
        Reset a player's input state (useful for cutscenes, etc.)
        """
        if player_id == 1:
            self.player1_input = PlayerInput()
        elif player_id == 2:
            self.player2_input = PlayerInput()
    
    def get_all_current_inputs(self):
        """
        Get all current input states for both players (useful for replay system)
        """
        return {
            'player1': self.player1_input.current_inputs.copy(),
            'player2': self.player2_input.current_inputs.copy(),
            'global': {
                'pause': self.pause_pressed
            }
        } 