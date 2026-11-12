from pathlib import Path

import pygame

from src.iso_math.iso_grid import IsoGrid
from src.iso_math.tile_set import Tile, TileSet, TileType
from src.map_gen import VoronoiMapGenerator
from src.object_class.character import Character
from src.object_class.slime import Slime
from src.object_class.starting_items import give_starting_items
from src.pause_menu import PauseAction, PauseMenu
from src.scene_base import BaseScene
from src.scenes import Scene
from src.ui.inventory_ui import InventoryUI

PLAYER_SPEED = 3
ATTACK_DURATION = 2000
FPS = 60
DEBUG_OVERLAY = False

SPRITE_DIR = Path(__file__).resolve().parent / "assets" / "sprites"
TILE_DIR = Path(__file__).resolve().parent / "assets" / "tiles"
SLIME_DIR = SPRITE_DIR / "Crypt Slime" / "Sprite Sheets"
SLIME_COUNT = 4
SLIME_MIN_DISTANCE = 4  # tiles (Manhattan) from the player spawn and from each other


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

# Stage size in tiles. There is no camera yet, so the whole stage must fit on screen:
# at TILE_SCALE 3 a 1280x720 window holds rows + cols <= 26 (12x12 is 1152x624 px).
STAGE_ROWS = 12
STAGE_COLS = 12

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

MAP_GENERATOR = VoronoiMapGenerator(Tile, TILESET)


def generate_stage(seed=None):
    """A new random stage. Pass a seed to rebuild the same one (e.g. for multiplayer)."""
    return MAP_GENERATOR.generate(STAGE_ROWS, STAGE_COLS, seed=seed)


def tile_position(grid, row, col):
    """Entity x, y that puts its feet hitbox in the middle of tile (row, col).

    An entity's feet box is 32x16 with its bottom-centre at (x + 16, y + 32),
    so centring it on the tile centre (cx, cy) means x = cx - 16, y = cy - 24.
    """
    cx, cy = grid.tile_center(row, col)
    return cx - 16, cy - 24


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


def generate_enemies(grid, spawn_tiles):
    """One slime on each (row, col) in spawn_tiles."""
    enemies_list = []
    for row, col in spawn_tiles:
        slime = Slime(*tile_position(grid, row, col))
        slime.set_collision_map(grid)
        enemies_list.append(slime)
    return enemies_list


def load_sprite(filename):
    """Needs the display to exist (convert_alpha)."""
    return pygame.image.load(str(SPRITE_DIR / filename)).convert_alpha()


def load_environment_tile(filename):
    """Needs the display to exist (convert_alpha)."""
    return pygame.image.load(str(TILE_DIR / filename)).convert_alpha()


def _is_key(event, key):
    return event.type == pygame.KEYDOWN and event.key == key


class GameScene(BaseScene):
    """The playable world: movement, combat, inventory and pause menu."""

    FPS = FPS

    def __init__(self, screen, seed=None):
        super().__init__(screen)
        screen_size = screen.get_size()

        # Load assets.
        TILESET.load(load_environment_tile, TILE_SCALE)
        Slime.load_assets(SLIME_DIR)

        # Build a fresh random stage. Row 0 is the back of the map (top of the screen).
        self.stage = generate_stage(seed)
        self.grid = IsoGrid(self.stage.tiles, TILESET, *screen_size)
        self.background = self.grid.render(BACKGROUND_COLOR)
        self.player_image = load_sprite("Sprite style 2.png")
        self.slash_image = pygame.image.load(
            str(ACTIONS_DIR / "test_slash_reference.png")
        ).convert_alpha()

        # Player data.
        self.player = Character(*tile_position(self.grid, *self.stage.spawn))
        self.player.set_collision_map(self.grid)
        give_starting_items(self.player)

        slime_tiles = self.stage.pick_spawn_tiles(
            SLIME_COUNT, rng=self.stage.seed, min_distance=SLIME_MIN_DISTANCE
        )
        self.enemies = generate_enemies(self.grid, slime_tiles)
        self.inventory_ui = InventoryUI(self.player.inventory, self.player)
        self.pause_menu = PauseMenu()
        self.inventory_open = False
        self.pause_open = False
        self.facing_right = True

        # Time spent in a menu, so enemy and weapon timers freeze while open.
        self.paused_ms = 0
        self.now = 0

    @property
    def frozen(self):
        """True while an overlay menu is open and the world should not advance."""
        return self.inventory_open or self.pause_open

    # ---------- BaseScene hooks
    def begin_frame(self, dt):
        if self.frozen:
            self.paused_ms += dt
        self.now = pygame.time.get_ticks() - self.paused_ms

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return Scene.QUIT
        if _is_key(event, pygame.K_ESCAPE):
            self._handle_escape()
        elif self.pause_open:
            return self._handle_pause_event(event)
        elif _is_key(event, pygame.K_i):
            self.inventory_open = not self.inventory_open
        elif self.inventory_open:
            self.inventory_ui.handle_event(event, self.screen.get_size())
        return None

    def update(self, dt):
        if not self.frozen:
            self._handle_movement()
            self._update_world()

    def draw(self):
        screen = self.screen
        screen.blit(self.background, (0, 0))
        self._draw_characters()
        for enemy in self.enemies:
            if enemy.is_alive():
                draw_health_bar(screen, enemy)
        draw_slash(screen, self.slash_image, self.player, self.now)

        if self.inventory_open:
            self.inventory_ui.draw(screen)
        if self.pause_open:
            self.pause_menu.draw(screen)
        if DEBUG_OVERLAY:
            self._draw_debug_overlay()

    # ---------- event helpers
    def _handle_escape(self):
        """Esc backs out one layer: pause menu -> inventory -> open the pause menu."""
        if self.pause_open:
            self.pause_open = False
        elif self.inventory_open:
            self.inventory_open = False
        else:
            self.pause_open = True
            self.pause_menu.reset()

    def _handle_pause_event(self, event):
        """Route an event to the pause menu. Return Scene.QUIT if Quit was chosen."""
        action = self.pause_menu.handle_event(event, self.screen.get_size())
        if action == PauseAction.CONTINUE:
            self.pause_open = False
        elif action == PauseAction.QUIT:
            return Scene.QUIT
        return None

    # ---------- update helpers
    def _handle_movement(self):
        """Move and turn the player from the WASD keys."""
        keys = pygame.key.get_pressed()
        for key, (dx, dy) in MOVE_KEYS:
            if keys[key]:
                self.player.move(dx * PLAYER_SPEED, dy * PLAYER_SPEED)
                self.player.facing = (dx, dy)
                if dx:
                    self.facing_right = dx > 0

    def _update_world(self):
        """Advance the player's attack and every enemy, then drop finished corpses."""
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            self.player.attack(self.enemies, self.now)
        for enemy in self.enemies:
            enemy.update(self.player, self.now)
        self.enemies = [e for e in self.enemies if not e.removable]

    # ---------- draw helpers
    def _draw_characters(self):
        """Draw the player and enemies, sorted by feet position so lower is in front."""
        screen, player = self.screen, self.player
        sprite = (
            self.player_image
            if self.facing_right
            else pygame.transform.flip(self.player_image, True, False)
        )
        # Each entry is (feet_y, draw_function, *arguments).
        drawables = [
            (player.movement_hitbox.bottom, screen.blit, sprite, (player.x, player.y))
        ]
        drawables += [(e.movement_hitbox.bottom, e.draw, screen) for e in self.enemies]
        for _, draw, *args in sorted(drawables, key=lambda d: d[0]):
            draw(*args)
        pygame.draw.rect(screen, (255, 0, 0), player.movement_hitbox, width=2)

    def _draw_debug_overlay(self):
        for enemy in self.enemies:
            pygame.draw.rect(self.screen, (255, 255, 0), enemy.hurtbox, width=1)
        grid = self.grid
        for r in range(grid.rows):
            for c in range(len(grid.tile_map[r])):
                walkable = TILESET.is_walkable(grid.tile_map[r][c])
                color = (0, 255, 0) if walkable else (255, 0, 0)
                pygame.draw.polygon(self.screen, color, grid.tile_diamond(r, c), 1)


def main_game(screen):
    """Scene entry point used by main.py."""
    return GameScene(screen).run()