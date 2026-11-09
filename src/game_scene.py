from pathlib import Path

import pygame

from src.iso_math.iso_grid import IsoGrid
from src.iso_math.tile_set import Tile, TileSet, TileType
from src.object_class.character import Character
from src.object_class.slime import Slime
from src.object_class.starting_items import give_starting_items
from src.pause_menu import PauseAction, PauseMenu
from src.scenes import Scene
from src.ui.inventory_ui import InventoryUI

PLAYER_SPEED = 3
ATTACK_DURATION = 2000
FPS = 60
DEBUG_OVERLAY = False

SPRITE_DIR = Path(__file__).resolve().parent / "assets" / "sprites"
TILE_DIR = Path(__file__).resolve().parent / "assets" / "tiles"
SLIME_DIR = SPRITE_DIR / "Crypt Slime" / "Sprite Sheets"
SLIME_SPAWN_TILES = [(2, 6), (7, 5), (3, 5), (7, 7)]


#Slash info will move to weapon
SLASH_MS = 150
ACTIONS_DIR = Path(__file__).resolve().parent / "assets" / "actions"
SLASH_ANGLES = {(1, 0): 0, (0, -1): 90, (-1, 0): 180, (0, 1): 270}


BACKGROUND_COLOR = (0, 0, 0)
TILE_SCALE = 3

# Row 0 is the back of the map (top of the screen); each row's first column is on the left.
TILE_MAP = [
    [0, 1, 7, 6, 7, 1, 1, 10, 10, 0],
    [1, 6, 7, 7, 8, 8, 1, 11, 1, 1],
    [1, 1, 8, 7, 4, 8, 1, 11, 7, 1],
    [1, 1, 8, 4, 4, 8, 1, 4, 6, 6],
    [9, 1, 8, 8, 8, 8, 1, 4, 7, 1],
    [9, 9, 1, 1, 8, 8, 1, 9, 7, 1],
    [1, 9, 4, 6, 9, 8, 8, 1, 1, 1],
    [9, 1, 4, 6, 1, 1, 8, 8, 1, 1],
    [10, 1, 8, 8, 1, 8, 6, 9, 6, 6],
    [0, 1, 1, 1, 1, 8, 1, 1, 6, 0],  # <-- Bottom-most tile
]

TILESET = TileSet(
    {
        Tile.VOID: TileType("void"),
        Tile.WATER: TileType("water", "WaterTile.png", walkable=False),
        Tile.GRASS_CLEAN: TileType("grass", "Grass_Clean_Tile.png", walkable=True),
        Tile.LIGHT_DIRT: TileType("light", "Light_Dirt_Tile.png", walkable=True),
        Tile.MED_DIRT: TileType("med", "Med_Dirt_Tile.png", walkable=True),
        Tile.DARK_DIRT: TileType("dark", "Dark_Dirt_Tile.png", walkable=True),
        Tile.SMALL_ROCK: TileType("small_rock", "Small_Rock_Tile.png", walkable=True),
        Tile.MEDIUM_ROCK: TileType("medium_rock", "Med_Rock_Tile.png", walkable=True),
        Tile.LARGE_ROCK: TileType("large_rock", "Large_Rock_Tile.png", walkable=False),
    }
)


def draw_slash(screen, slash_image, player, now):
    weapon = player.equipped_item
    elapsed = now - player.last_attack_time
    if weapon is None or elapsed >= SLASH_MS:
        return
    rect = weapon.attack_rect(player.hurtbox.center, player.facing)
    img = pygame.transform.scale(slash_image, rect.size)
    img = pygame.transform.rotate(img, SLASH_ANGLES.get(tuple(player.facing), 0))
    img.set_alpha(int(255 * (1 - elapsed / SLASH_MS)))
    screen.blit(img, img.get_rect(center=rect.center))


def draw_health_bar(screen, entity):
    box = entity.hurtbox
    bar_rect = pygame.Rect(box.x, box.y - 8, box.width, 5)
    fill = bar_rect.copy()
    fill.width = int(bar_rect.width * entity.health / entity.max_health)
    pygame.draw.rect(screen, (40, 0, 0), bar_rect)
    pygame.draw.rect(screen, (220, 30, 30), fill)
    pygame.draw.rect(screen, (0, 0, 0), bar_rect, width=1)


def generate_enemies(grid):
    """One slime on each tile in SLIME_SPAWN_TILES."""
    enemies_list = []
    for row, col in SLIME_SPAWN_TILES:
        cx, cy = grid.tile_center(row, col)
        slime = Slime(cx - 16, cy - 24)
        slime.set_collision_map(grid)
        enemies_list.append(slime)
    return enemies_list


def load_sprite(filename):
    """Needs the display to exist (convert_alpha)."""
    return pygame.image.load(str(SPRITE_DIR / filename)).convert_alpha()


def load_environment_tile(filename):
    """Needs the display to exist (convert_alpha)."""
    return pygame.image.load(str(TILE_DIR / filename)).convert_alpha()


def main_game(screen):
    screen_width, screen_height = screen.get_size()
    clock = pygame.time.Clock()
    paused_ms = 0  # time spent in the inventory or pause menu, so enemy and weapon timers freeze while open

    # Load assets.
    TILESET.load(load_environment_tile, TILE_SCALE)
    Slime.load_assets(SLIME_DIR)
    grid = IsoGrid(TILE_MAP, TILESET, screen_width, screen_height)
    background = grid.render(BACKGROUND_COLOR)

    # Player data.
    player_image = load_sprite("Sprite style 2.png")
    player = Character(screen_width / 2, screen_height / 2)  # spawn in center
    player.set_collision_map(grid)
    slash_image = pygame.image.load(
        str(ACTIONS_DIR / "test_slash_reference.png")
    ).convert_alpha()

    # gives player starting items
    give_starting_items(player)

    inventory_ui = InventoryUI(player.inventory, player)
    inventory_open = False
    pause_menu = PauseMenu()
    pause_open = False
    facing_right = True
    enemies = generate_enemies(grid)

    while True:
        dt = clock.tick(FPS)
        if inventory_open or pause_open:
            paused_ms += dt
        now = pygame.time.get_ticks() - paused_ms

        #Event Handling
        #Block

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return Scene.QUIT
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Esc backs out one layer: pause menu -> inventory -> open the pause menu.
                if pause_open:
                    pause_open = False
                elif inventory_open:
                    inventory_open = False
                else:
                    pause_open = True
                    pause_menu.reset()
            elif pause_open:
                action = pause_menu.handle_event(event, screen.get_size())
                if action == PauseAction.CONTINUE:
                    pause_open = False
                elif action == PauseAction.QUIT:
                    return Scene.QUIT
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
                inventory_open = not inventory_open
            elif inventory_open:
                inventory_ui.handle_event(event, screen.get_size())

        #Keyboard Input
        #Block

        if not inventory_open and not pause_open:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                player.move(0, -PLAYER_SPEED)
                player.facing = (0, -1)
            if keys[pygame.K_s]:
                player.move(0, PLAYER_SPEED)
                player.facing = (0, 1)
            if keys[pygame.K_a]:
                player.move(-PLAYER_SPEED, 0)
                player.facing = (-1, 0)
                facing_right = False
            if keys[pygame.K_d]:
                player.move(PLAYER_SPEED, 0)
                player.facing = (1, 0)
                facing_right = True
            if keys[pygame.K_SPACE]:
                player.attack(enemies, now)

            for e in enemies:
                e.update(player, now)
            enemies = [e for e in enemies if e.is_alive()]

        #Drawing
        #Block

        screen.blit(background, (0, 0))
        sprite = (
            player_image
            if facing_right
            else pygame.transform.flip(player_image, True, False)
        )
        # Sort by feet position so whoever is lower on screen draws in front.
        # Each entry is (feet_y, draw_function, *arguments).
        drawables = [
            (player.movement_hitbox.bottom, screen.blit, sprite, (player.x, player.y))
        ]
        drawables += [(e.movement_hitbox.bottom, e.draw, screen) for e in enemies]
        for _, draw, *args in sorted(drawables, key=lambda d: d[0]):
            draw(*args)
        pygame.draw.rect(screen, (255, 0, 0), player.movement_hitbox, width=2)

        for e in enemies:
            draw_health_bar(screen, e)
        draw_slash(screen, slash_image, player, now)

        if inventory_open:
            inventory_ui.draw(screen)
        if pause_open:
            pause_menu.draw(screen)

        if DEBUG_OVERLAY:
            for enemy in enemies:
                pygame.draw.rect(screen, (255, 255, 0), enemy.hurtbox, width=1)
            for r in range(grid.rows):
                for c in range(len(grid.tile_map[r])):
                    color = (
                        (0, 255, 0)
                        if TILESET.is_walkable(grid.tile_map[r][c])
                        else (255, 0, 0)
                    )
                    pygame.draw.polygon(screen, color, grid.tile_diamond(r, c), 1)
        pygame.display.flip()
