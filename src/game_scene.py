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


# Slash info will move to weapon
SLASH_MS = 150
ACTIONS_DIR = Path(__file__).resolve().parent / "assets" / "actions"
SLASH_ANGLES = {(1, 0): 0, (0, -1): 90, (-1, 0): 180, (0, 1): 270}

# (key, (dx, dy)) in the order they are applied each frame.
MOVE_KEYS = [
    (pygame.K_w, (0, -1)),
    (pygame.K_s, (0, 1)),
    (pygame.K_a, (-1, 0)),
    (pygame.K_d, (1, 0)),
]


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


class GameState:
    """Mutable per-run state that the helper functions below read and update."""

    def __init__(self, player, enemies):
        self.player = player
        self.enemies = enemies
        self.inventory_open = False
        self.pause_open = False
        self.facing_right = True

    @property
    def frozen(self):
        """True while an overlay menu is open and the world should not advance."""
        return self.inventory_open or self.pause_open


# ---------- event handling
def _is_key(event, key):
    return event.type == pygame.KEYDOWN and event.key == key


def _handle_escape(state, pause_menu):
    """Esc backs out one layer: pause menu -> inventory -> open the pause menu."""
    if state.pause_open:
        state.pause_open = False
    elif state.inventory_open:
        state.inventory_open = False
    else:
        state.pause_open = True
        pause_menu.reset()


def _handle_pause_event(event, state, pause_menu, screen_size):
    """Route an event to the pause menu. Return Scene.QUIT if Quit was chosen."""
    action = pause_menu.handle_event(event, screen_size)
    if action == PauseAction.CONTINUE:
        state.pause_open = False
    elif action == PauseAction.QUIT:
        return Scene.QUIT
    return None


def handle_events(state, inventory_ui, pause_menu, screen_size):
    """Process this frame's events. Return Scene.QUIT to leave the game, else None."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return Scene.QUIT
        if _is_key(event, pygame.K_ESCAPE):
            _handle_escape(state, pause_menu)
        elif state.pause_open:
            if _handle_pause_event(event, state, pause_menu, screen_size) == Scene.QUIT:
                return Scene.QUIT
        elif _is_key(event, pygame.K_i):
            state.inventory_open = not state.inventory_open
        elif state.inventory_open:
            inventory_ui.handle_event(event, screen_size)
    return None


# ---------- per-frame updates
def handle_movement(state):
    """Move and turn the player from the WASD keys."""
    player = state.player
    keys = pygame.key.get_pressed()
    for key, (dx, dy) in MOVE_KEYS:
        if keys[key]:
            player.move(dx * PLAYER_SPEED, dy * PLAYER_SPEED)
            player.facing = (dx, dy)
            if dx:
                state.facing_right = dx > 0


def update_world(state, now):
    """Advance the player's attack and every enemy, then drop the dead ones."""
    if pygame.key.get_pressed()[pygame.K_SPACE]:
        state.player.attack(state.enemies, now)
    for enemy in state.enemies:
        enemy.update(state.player, now)
    state.enemies = [e for e in state.enemies if e.is_alive()]


# ---------- drawing
def draw_characters(screen, state, player_image):
    """Draw the player and enemies, sorted by feet position so lower is in front."""
    player = state.player
    sprite = (
        player_image
        if state.facing_right
        else pygame.transform.flip(player_image, True, False)
    )
    # Each entry is (feet_y, draw_function, *arguments).
    drawables = [
        (player.movement_hitbox.bottom, screen.blit, sprite, (player.x, player.y))
    ]
    drawables += [(e.movement_hitbox.bottom, e.draw, screen) for e in state.enemies]
    for _, draw, *args in sorted(drawables, key=lambda d: d[0]):
        draw(*args)
    pygame.draw.rect(screen, (255, 0, 0), player.movement_hitbox, width=2)


def draw_debug_overlay(screen, enemies, grid):
    for enemy in enemies:
        pygame.draw.rect(screen, (255, 255, 0), enemy.hurtbox, width=1)
    for r in range(grid.rows):
        for c in range(len(grid.tile_map[r])):
            color = (
                (0, 255, 0) if TILESET.is_walkable(grid.tile_map[r][c]) else (255, 0, 0)
            )
            pygame.draw.polygon(screen, color, grid.tile_diamond(r, c), 1)


def draw_frame(screen, state, assets, now):
    """Draw the world, then whichever overlay menu is open."""
    screen.blit(assets["background"], (0, 0))
    draw_characters(screen, state, assets["player_image"])
    for enemy in state.enemies:
        draw_health_bar(screen, enemy)
    draw_slash(screen, assets["slash_image"], state.player, now)

    if state.inventory_open:
        assets["inventory_ui"].draw(screen)
    if state.pause_open:
        assets["pause_menu"].draw(screen)
    if DEBUG_OVERLAY:
        draw_debug_overlay(screen, state.enemies, assets["grid"])
    pygame.display.flip()


def main_game(screen):
    screen_size = screen.get_size()
    clock = pygame.time.Clock()
    paused_ms = 0  # time spent in the inventory or pause menu, so enemy and weapon timers freeze while open

    # Load assets.
    TILESET.load(load_environment_tile, TILE_SCALE)
    Slime.load_assets(SLIME_DIR)
    grid = IsoGrid(TILE_MAP, TILESET, *screen_size)

    # Player data.
    player = Character(screen_size[0] / 2, screen_size[1] / 2)  # spawn in center
    player.set_collision_map(grid)
    give_starting_items(player)

    state = GameState(player, generate_enemies(grid))
    pause_menu = PauseMenu()
    inventory_ui = InventoryUI(player.inventory, player)
    assets = {
        "grid": grid,
        "background": grid.render(BACKGROUND_COLOR),
        "player_image": load_sprite("Sprite style 2.png"),
        "slash_image": pygame.image.load(
            str(ACTIONS_DIR / "test_slash_reference.png")
        ).convert_alpha(),
        "inventory_ui": inventory_ui,
        "pause_menu": pause_menu,
    }

    while True:
        dt = clock.tick(FPS)
        if state.frozen:
            paused_ms += dt
        now = pygame.time.get_ticks() - paused_ms

        if handle_events(state, inventory_ui, pause_menu, screen_size) == Scene.QUIT:
            return Scene.QUIT

        if not state.frozen:
            handle_movement(state)
            update_world(state, now)

        draw_frame(screen, state, assets, now)