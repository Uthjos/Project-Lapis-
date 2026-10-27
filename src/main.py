import sys
from pathlib import Path

import pygame

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.object_class.Character import Character
from src.object_class.Item import Item
from src.ui.InventoryUI import InventoryUI


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
ATTACK_DURATION = 2000
FPS = 60

"""
Sprite texture setup
"""
# Resolved relative to this file (src/), so it works from any working directory
SPRITE_DIR = Path(__file__).resolve().parent / "assets" / "sprites"
Tile_DIR = Path(__file__).resolve().parent / "assets" / "tiles"

BACKGROUND_COLOR = (0, 0, 0)  # shows through wherever the tile map is 0

# Stage layout: 0 = blank, 1 = draw the tile.
# Row 0 is the back of the map (top of the screen), and each row's first
# column is on the left side of the map.
TILE_SCALE = 3
TILE_MAP = [
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
    [1, 1, 1, 0, 0, 1, 1, 0, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 0, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 0, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
]
"""
Enlarge a sprite by a whole-number factor
"""
def scale_image(image, factor):

    w, h = image.get_size()
    return pygame.transform.scale(image, (w * factor, h * factor))

"""
Load a sprite from the sprites folder.
convert_alpha() needs the display to exist, so call this
only after pygame.display.set_mode().
"""
def load_sprite(filename):

    return pygame.image.load(str(SPRITE_DIR / filename)).convert_alpha()

"""
Load a sprite from the tile folder.
convert_alpha() needs the display to exist, so call this
only after pygame.display.set_mode().
"""
def load_environment_tile(filename):

    return pygame.image.load(str(Tile_DIR / filename)).convert_alpha()

"""
Draw an isometric tile map onto a surface once, so each frame is a single blit.

texture:    the isometric block sprite (green top face + dirt sides)
tile_map:   2D list of ints. 0 = blank, 1 = draw the texture there
width/height: size of the surface (usually the screen)
top_height: height in pixels of the diamond-shaped top face of the sprite.
            Defaults to half the tile width (standard 2:1 isometric).
            Tweak this if the green tops show gaps or overlap.
"""
def build_background(texture, tile_map, width,
                     height, top_height=None):

    tile_w, tile_h = texture.get_size()
    if top_height is None:
        top_height = tile_w // 2

    # Each grid step moves half a tile across and half a top face down.
    # That makes neighboring top faces meet edge to edge, so the green
    # surface reads as one continuous plane.
    step_x = tile_w // 2.1
    step_y = top_height // 2

    rows = len(tile_map)
    cols = max(len(row) for row in tile_map)

    # Full on-screen size of the map, used to center it on the surface
    map_w = (rows + cols - 2) * step_x + tile_w
    map_h = (rows + cols - 2) * step_y + tile_h
    # Screen position of tile (row 0, col 0). It is the left-most column of
    # the diamond map's far corner, so shift right by (rows - 1) steps.
    origin_x = (width - map_w) // 2 + (rows - 1) * step_x
    origin_y = (height - map_h) // 2

    background = pygame.Surface((width, height))
    background.fill(BACKGROUND_COLOR)

    # Draw back to front (top row first) so nearer tiles overlap the ones behind
    for row in range(rows):
        for col in range(len(tile_map[row])):
            if tile_map[row][col] == 1:
                x = origin_x + (col - row) * step_x
                y = origin_y + (col + row) * step_y
                background.blit(texture, (x, y))
    return background


def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Project Lapis")
    clock = pygame.time.Clock()

    #load assets
    # Environment textures (add more stage tiles to this list later)
    # TEMPORARY: Placeholder tile art; replace with the team's approved terrain tile.
    stage_textures = [scale_image(load_environment_tile("earth_tile.png"), TILE_SCALE)]
    background = build_background(stage_textures[0], TILE_MAP, SCREEN_WIDTH, SCREEN_HEIGHT)

    #player data
    player_image = load_sprite("Sprite style 2.png")
    player = Character(380, 280)
    # Temporary sample items so you can test the screen
    player.inventory.add_item(Item("Rusty Sword", "weapon", "A basic starting weapon."))
    player.inventory.add_item(Item("Health Potion", "consumable",
    "Restores health when used."))
    inventory_ui = InventoryUI(player.inventory, player)
    inventory_open = False


    facing_right = True

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                if inventory_open and event.type == pygame.KEYDOWN:
                    inventory_open = False
                else:
                    running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
                inventory_open = not inventory_open
            elif inventory_open:
                inventory_ui.handle_event(event, screen.get_size())

        #input
        if not inventory_open:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                player.move(0, -PLAYER_SPEED)
            if keys[pygame.K_s]:
                player.move(0, PLAYER_SPEED)
            if keys[pygame.K_a]:
                player.move(-PLAYER_SPEED, 0)
                facing_right = False
            if keys[pygame.K_d]:
                player.move(PLAYER_SPEED, 0)
                facing_right = True
            if keys[pygame.K_SPACE]:
                player.attack()



        # ---- Draw (back to front) ----
        screen.blit(background, (0, 0))

        sprite = player_image if facing_right else pygame.transform.flip(player_image, True, False)
        screen.blit(sprite, (player.x, player.y))
        if inventory_open:
            inventory_ui.draw(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()