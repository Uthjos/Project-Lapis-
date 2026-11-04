import pygame

from src import game_scene
from src.game_scene import (
    SLIME_SPAWN_TILES,
    TILE_MAP,
    TILESET,
    draw_health_bar,
    draw_slash,
    generate_enemies,
    main_game,
)
from src.iso_math.TileSet import Tile
from src.object_class.Character import Character
from src.object_class.Entity import Entity
from src.object_class.Slime import Slime
from src.object_class.Weapon import Weapon
from src.scenes import Scene


class FakeGrid:
    def tile_center(self, row, col):
        return (100 * col, 100 * row)

    def is_walkable(self, px, py):
        return True


# ---------- map data ----------
def test_tile_map_uses_only_known_tiles():
    for row in TILE_MAP:
        for tile_id in row:
            assert tile_id in TILESET.types


def test_tile_map_is_not_empty():
    assert len(TILE_MAP) > 0
    assert all(len(row) > 0 for row in TILE_MAP)


def test_slime_spawn_tiles_are_inside_map_and_walkable():
    for row, col in SLIME_SPAWN_TILES:
        assert 0 <= row < len(TILE_MAP)
        assert 0 <= col < len(TILE_MAP[row])
        assert TILESET.is_walkable(TILE_MAP[row][col])


def test_tileset_walkability():
    assert TILESET.is_walkable(Tile.GRASS_CLEAN)
    assert not TILESET.is_walkable(Tile.Water)
    assert not TILESET.is_walkable(Tile.LARGE_ROCK)


# ---------- helpers ----------
def test_generate_enemies_spawns_one_slime_per_spawn_tile(slime_assets):
    grid = FakeGrid()

    enemies = generate_enemies(grid)

    assert len(enemies) == len(SLIME_SPAWN_TILES)
    for enemy, (row, col) in zip(enemies, SLIME_SPAWN_TILES):
        cx, cy = grid.tile_center(row, col)
        assert isinstance(enemy, Slime)
        assert (enemy.x, enemy.y) == (cx - 16, cy - 24)
        assert enemy.collision_map is grid


def test_draw_health_bar_shows_remaining_health():
    surface = pygame.Surface((200, 200))
    entity = Entity(50, 50, health=30)
    entity.take_damage(15)   # half health

    draw_health_bar(surface, entity)

    # Bar sits 8px above the hurtbox; left half is filled red, right half is empty.
    assert tuple(surface.get_at((60, 44)))[:3] == (220, 30, 30)
    assert tuple(surface.get_at((75, 44)))[:3] == (40, 0, 0)


def make_attacking_player(last_attack_time):
    player = Character(100, 100)
    sword = Weapon("Sword", damage=10, attack_speed=1.0, range=40)
    player.inventory.add_item(sword)
    player.equip_item(sword)
    player.last_attack_time = last_attack_time
    return player


def surface_bytes(surface):
    return pygame.image.tobytes(surface, "RGB")


def test_draw_slash_draws_during_attack_window():
    surface = pygame.Surface((300, 300))
    surface.fill((0, 0, 0))
    before = surface_bytes(surface)
    slash = pygame.Surface((10, 10), pygame.SRCALPHA)
    slash.fill((255, 255, 255, 255))

    draw_slash(surface, slash, make_attacking_player(1000), 1010)

    assert surface_bytes(surface) != before


def test_draw_slash_does_nothing_after_window():
    surface = pygame.Surface((300, 300))
    before = surface_bytes(surface)
    slash = pygame.Surface((10, 10), pygame.SRCALPHA)
    slash.fill((255, 255, 255, 255))

    draw_slash(surface, slash, make_attacking_player(1000), 1000 + game_scene.SLASH_MS)

    assert surface_bytes(surface) == before


def test_draw_slash_does_nothing_without_weapon():
    surface = pygame.Surface((300, 300))
    before = surface_bytes(surface)
    slash = pygame.Surface((10, 10), pygame.SRCALPHA)
    slash.fill((255, 255, 255, 255))

    draw_slash(surface, slash, Character(100, 100), 0)

    assert surface_bytes(surface) == before


# ---------- scene loop ----------
def test_main_game_returns_quit_on_window_close(screen):
    pygame.event.post(pygame.event.Event(pygame.QUIT))

    assert main_game(screen) == Scene.QUIT


def test_main_game_escape_returns_to_menu(screen):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))

    assert main_game(screen) == Scene.MENU
