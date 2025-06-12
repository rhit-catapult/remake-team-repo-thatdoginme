import pygame
import os

def load_sprites_for_character(character_name, scale_factor):
    """
    Loads all sprites for a given character from their asset folder.
    Organizes them into a dictionary of animations.
    e.g., {'walk': [img1, img2], 'jump': [img1]}
    """
    sprites = {}
    path = f"assets/images/{character_name.lower()} sprites"

    if not os.path.isdir(path):
        print(f"Warning: Sprite directory not found for {character_name} at {path}")
        return sprites

    for filename in os.listdir(path):
        if not filename.endswith(('.png', '.jpg')):
            continue

        # Clean filename to get animation name and frame
        # e.g., 'speedsterDrive-a.png' -> animation_name='drive', frame_id='a'
        clean_name = os.path.splitext(filename)[0]
        parts = clean_name.split('-')
        
        # The part before the first '-' is the animation name
        # We remove the character name from it
        animation_name = parts[0].replace(character_name.lower(), '').lower()
        
        # Determine the key for the dictionary
        if animation_name == 'drive':
            animation_key = 'walk' # Map 'drive' to 'walk' for consistency
        elif animation_name == 'jump':
            animation_key = 'jump'
        else:
            animation_key = animation_name

        try:
            image = pygame.image.load(os.path.join(path, filename)).convert_alpha()
            
            # Scale image
            original_size = image.get_size()
            new_size = (int(original_size[0] * scale_factor), int(original_size[1] * scale_factor))
            scaled_image = pygame.transform.scale(image, new_size)

            if animation_key not in sprites:
                sprites[animation_key] = []
            
            sprites[animation_key].append(scaled_image)
            print(f"Loaded sprite: {filename} for animation '{animation_key}'")

        except pygame.error as e:
            print(f"Error loading sprite {filename}: {e}")
            continue

    # Sort walk sprites to ensure 'a' comes before 'b'
    if 'walk' in sprites:
        sprites['walk'].sort(key=lambda img: img.get_width()) # A bit of a hack, but should work for a/b

    return sprites 