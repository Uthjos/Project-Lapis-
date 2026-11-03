import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
import pygame

from src.iso_math.IsoGrid import IsoGrid
from src.iso_math.TileSet import Tile, TileSet, TileType
from src.object_class.Character import Character
from src.object_class.Item import Item
from src.ui.InventoryUI import InventoryUI

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 3
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
    [1, 1, 3, 4, 4, 1, 1, 1, 1, 1],
    [1, 1, 3, 4, 4, 1, 1, 4, 1, 1],
    [1, 1, 3, 3, 3, 1, 1, 4, 1, 1],
    [1, 1, 1, 1, 3, 3, 1, 1, 1, 1],
    [1, 1, 4, 1, 1, 3, 3, 1, 1, 1],
    [1, 1, 4, 1, 1, 1, 3, 3, 1, 1],
    [1, 1, 1, 1, 1, 3, 1, 1, 1, 1],
    [0, 1, 1, 1, 1, 3, 1, 1, 1, 0], # <-- Bottom-most tile
]

TILESET = TileSet({
    Tile.VOID:  TileType("void"),
    Tile.FLOOR: TileType("earth", "GrassDirt_tile.png", walkable=True),
    Tile.PATH: TileType("path", "GrassStone_tile.png", walkable=True),
    Tile.Water: TileType("water", "Watertile.png", walkable=False),
    #Tile.WALL:  TileType("wall", "wall_tile.png", walkable=False),
})

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




def main():
    DEBUG_OVERLAY = False
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Project Lapis")
    clock = pygame.time.Clock()

    #load assets
    TILESET.load(load_environment_tile, TILE_SCALE)
    grid = IsoGrid(TILE_MAP, TILESET,SCREEN_WIDTH, SCREEN_HEIGHT)
    background = grid.render(BACKGROUND_COLOR)

    #player data
    player_image = load_sprite("Sprite style 2.png")
    player = Character(380, 280)
    player.set_collision_map(grid)

    # Temporary sample items so you can test the screen
    player.inventory.add_item(Item("Rusty Sword", "weapon", "A basic starting weapon."))
    player.inventory.add_item(Item("Health Potion", "consumable",
    "Restores health when used."))
    inventory_ui = InventoryUI(player.inventory, player)
    inventory_open = False


    facing_right = True

    running = True
    #Handle events here before rendering
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


        #render game here
        # ---- Draw (back to front) ----
        screen.blit(background, (0, 0))

        sprite = player_image if facing_right else pygame.transform.flip(player_image, True, False)
        screen.blit(sprite, (player.x, player.y))
        if inventory_open:
            inventory_ui.draw(screen)

        pygame.draw.rect(screen, (255,0,0), player.movement_hitbox, width=2)
        #debug info, set at start of main()
        if DEBUG_OVERLAY:
            for r in range(grid.rows):
                for c in range(len(grid.tile_map[r])):
                    color = (0, 255, 0) if TILESET.is_walkable(grid.tile_map[r][c]) else (255, 0, 0)
                    pygame.draw.polygon(screen, color, grid.tile_diamond(r, c), 1)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()