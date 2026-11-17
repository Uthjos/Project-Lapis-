import pygame
import pytest

from src import game_scene
from src.game_scene import (
    PLAYER_SPEED,
    SLIME_COUNT,
    SLIME_MIN_DISTANCE,
    STAGE_COLS,
    STAGE_ROWS,
    TILESET,
    GameScene,
    draw_health_bar,
    draw_slash,
    generate_enemies,
    generate_stage,
    main_game,
    tile_position,
)
from src.iso_math.iso_grid import IsoGrid
from src.iso_math.tile_set import Tile
from src.object_class.character import Character
from src.object_class.enemy import Enemy
from src.object_class.entity import Entity
from src.object_class.slime import Slime
from src.object_class.weapon import Weapon
from src.scene_base import BaseScene
from src.scenes import Scene


class FakeGrid:
    def tile_center(self, row, col):
        return (100 * col, 100 * row)

    def is_walkable(self, px, py):
        return True


SEED = 1234  # fixed stage so GameScene tests are repeatable


# ---------- map data ----------
@pytest.mark.parametrize("seed", range(10))
def test_generated_stage_uses_only_known_tiles(seed):
    stage = generate_stage(seed)

    assert len(stage.tiles) == STAGE_ROWS
    assert all(len(row) == STAGE_COLS for row in stage.tiles)
    for row in stage.tiles:
        for tile_id in row:
            assert tile_id in TILESET.types


def test_generate_stage_is_repeatable_by_seed():
    assert generate_stage(7).tiles == generate_stage(7).tiles
    assert generate_stage(7).tiles != generate_stage(8).tiles


def test_unseeded_stage_reports_a_seed_that_rebuilds_it():
    stage = generate_stage()

    assert generate_stage(stage.seed).tiles == stage.tiles


def test_stage_fits_on_screen(screen):
    TILESET.load(game_scene.load_environment_tile, game_scene.TILE_SCALE)
    grid = IsoGrid(generate_stage(SEED).tiles, TILESET, *screen.get_size())

    corners = [
        grid.tile_topleft(0, 0),
        grid.tile_topleft(0, STAGE_COLS - 1),
        grid.tile_topleft(STAGE_ROWS - 1, 0),
        grid.tile_topleft(STAGE_ROWS - 1, STAGE_COLS - 1),
    ]
    w, h = screen.get_size()
    for x, y in corners:
        assert 0 <= x and x + grid.tile_w <= w
        assert 0 <= y and y + grid.tile_h <= h


def test_tileset_walkability():
    assert TILESET.is_walkable(Tile.GRASS_CLEAN)
    assert not TILESET.is_walkable(Tile.WATER)
    assert not TILESET.is_walkable(Tile.LARGE_ROCK)


# ---------- helpers ----------
def test_tile_position_centres_feet_on_tile():
    grid = FakeGrid()
    player = Character(*tile_position(grid, 2, 3))

    assert player.movement_hitbox.center == grid.tile_center(2, 3)


def test_generate_enemies_spawns_one_slime_per_spawn_tile(slime_assets):
    grid = FakeGrid()
    spawn_tiles = [(2, 6), (7, 5), (3, 5)]

    enemies = generate_enemies(grid, spawn_tiles)

    assert len(enemies) == len(spawn_tiles)
    for enemy, (row, col) in zip(enemies, spawn_tiles):
        cx, cy = grid.tile_center(row, col)
        assert isinstance(enemy, Slime)
        assert (enemy.x, enemy.y) == (cx - 16, cy - 24)
        assert enemy.collision_map is grid


def test_draw_health_bar_shows_remaining_health():
    surface = pygame.Surface((200, 200))
    entity = Entity(50, 50, health=30)
    entity.take_damage(15)  # half health

    draw_health_bar(surface, entity)

    # Bar sits 8px above the hurtbox; left half is filled red, right half is empty.
    assert tuple(surface.get_at((60, 44)))[:3] == (220, 30, 30)
    assert tuple(surface.get_at((75, 44)))[:3] == (40, 0, 0)


def make_attacking_player(last_attack_time):
    player = Character(100, 100)
    sword = Weapon("Sword", damage=10, attack_speed=1.0, attack_range=40)
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


def feed_events(monkeypatch, frames):
    """pygame.event.get() returns one list of events per frame, then QUIT forever."""
    frames = iter(frames)
    monkeypatch.setattr(
        pygame.event, "get", lambda: next(frames, [pygame.event.Event(pygame.QUIT)])
    )


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


def test_escape_opens_pause_menu_instead_of_leaving(screen, monkeypatch):
    # Esc must not return to the menu any more; the loop keeps running until QUIT.
    feed_events(monkeypatch, [[key(pygame.K_ESCAPE)], []])

    assert main_game(screen) == Scene.QUIT


def test_pause_menu_quit_button_quits(screen, monkeypatch):
    # Esc opens the pause menu, Down selects Quit, Enter confirms.
    feed_events(
        monkeypatch,
        [[key(pygame.K_ESCAPE)], [key(pygame.K_DOWN)], [key(pygame.K_RETURN)]],
    )
    result = main_game(screen)

    assert result == Scene.QUIT


def test_pause_menu_continue_resumes_game(screen, monkeypatch):
    calls = {"n": 0}
    frames = [[key(pygame.K_ESCAPE)], [key(pygame.K_RETURN)], [], []]

    def fake_get():
        calls["n"] += 1
        return (
            frames[calls["n"] - 1]
            if calls["n"] <= len(frames)
            else [pygame.event.Event(pygame.QUIT)]
        )

    monkeypatch.setattr(pygame.event, "get", fake_get)

    assert main_game(screen) == Scene.QUIT
    # Loop kept running after Continue instead of exiting on it.
    assert calls["n"] == len(frames) + 1


def test_escape_closes_pause_menu(screen, monkeypatch):
    calls = {"n": 0}
    frames = [[key(pygame.K_ESCAPE)], [key(pygame.K_ESCAPE)], []]

    def fake_get():
        calls["n"] += 1
        return (
            frames[calls["n"] - 1]
            if calls["n"] <= len(frames)
            else [pygame.event.Event(pygame.QUIT)]
        )

    monkeypatch.setattr(pygame.event, "get", fake_get)

    assert main_game(screen) == Scene.QUIT
    assert calls["n"] == len(frames) + 1


def test_escape_closes_inventory_before_opening_pause(screen, monkeypatch):
    # I opens inventory, Esc closes it (no pause menu), second Esc opens pause,
    # then Down+Enter picks Quit.
    feed_events(
        monkeypatch,
        [
            [key(pygame.K_i)],
            [key(pygame.K_ESCAPE)],
            [key(pygame.K_ESCAPE)],
            [key(pygame.K_DOWN)],
            [key(pygame.K_RETURN)],
        ],
    )

    assert main_game(screen) == Scene.QUIT


def test_inventory_key_ignored_while_paused(screen, monkeypatch):
    # With the pause menu open, I must not open the inventory; Enter hits Continue.
    calls = {"n": 0}
    frames = [[key(pygame.K_ESCAPE)], [key(pygame.K_i)], [key(pygame.K_RETURN)], []]

    def fake_get():
        calls["n"] += 1
        return (
            frames[calls["n"] - 1]
            if calls["n"] <= len(frames)
            else [pygame.event.Event(pygame.QUIT)]
        )

    monkeypatch.setattr(pygame.event, "get", fake_get)

    assert main_game(screen) == Scene.QUIT


# ---------- GameScene ----------
class Pressed:
    """Stands in for the object pygame.key.get_pressed() returns."""

    def __init__(self, *keys):
        self.keys = set(keys)

    def __getitem__(self, k):
        return k in self.keys


def press(monkeypatch, *keys):
    monkeypatch.setattr(pygame.key, "get_pressed", lambda: Pressed(*keys))


@pytest.fixture
def scene(screen):
    game = GameScene(screen, seed=SEED)
    game.player.set_collision_map(None)  # tests move the player freely
    return game


def test_game_scene_is_a_base_scene(scene):
    assert isinstance(scene, BaseScene)
    assert scene.FPS == game_scene.FPS


def test_game_scene_uses_generated_stage(scene):
    assert scene.grid.tile_map is scene.stage.tiles
    assert scene.stage.seed == SEED


def test_each_game_gets_its_own_random_stage(screen):
    assert GameScene(screen).stage.seed != GameScene(screen).stage.seed


@pytest.mark.parametrize("seed", range(10))
def test_player_spawns_standing_on_walkable_ground(screen, seed):
    game = GameScene(screen, seed=seed)
    row, col = game.stage.spawn

    assert game.stage.is_walkable(row, col)
    assert game.grid.tile_at(*game.player.movement_hitbox.center) == game.stage.tiles[row][col]
    assert game.player._can_stand(0, 0)  # feet box fully on walkable tiles


@pytest.mark.parametrize("seed", range(10))
def test_slimes_spawn_on_walkable_ground_away_from_player(screen, seed):
    game = GameScene(screen, seed=seed)
    spawn_center = game.grid.tile_center(*game.stage.spawn)

    assert len(game.enemies) == SLIME_COUNT
    for slime in game.enemies:
        assert slime._can_stand(0, 0)
        assert slime.movement_hitbox.center != spawn_center
    # Distance check in tile units, using the generator's own spawn list.
    for row, col in game.stage.pick_spawn_tiles(
        SLIME_COUNT, rng=game.stage.seed, min_distance=SLIME_MIN_DISTANCE
    ):
        sr, sc = game.stage.spawn
        assert abs(row - sr) + abs(col - sc) >= SLIME_MIN_DISTANCE


def test_game_scene_starts_with_slimes_and_armed_player(scene):
    assert len(scene.enemies) == SLIME_COUNT
    assert all(isinstance(e, Slime) for e in scene.enemies)
    assert isinstance(scene.player.equipped_item, Weapon)
    assert scene.frozen is False
    assert scene.facing_right is True


@pytest.mark.parametrize(
    "inventory_open,pause_open,expected",
    [(False, False, False), (True, False, True), (False, True, True), (True, True, True)],
)
def test_frozen_when_any_overlay_is_open(scene, inventory_open, pause_open, expected):
    scene.inventory_open = inventory_open
    scene.pause_open = pause_open

    assert scene.frozen is expected


# ----- begin_frame
def test_begin_frame_only_counts_paused_time_when_frozen(scene):
    scene.begin_frame(16)
    assert scene.paused_ms == 0

    scene.inventory_open = True
    scene.begin_frame(16)
    assert scene.paused_ms == 16

    scene.inventory_open = False
    scene.pause_open = True
    scene.begin_frame(10)
    assert scene.paused_ms == 26


def test_begin_frame_sets_now_without_paused_time(scene, monkeypatch):
    monkeypatch.setattr(pygame.time, "get_ticks", lambda: 1000)

    scene.begin_frame(0)
    assert scene.now == 1000

    scene.pause_open = True
    scene.begin_frame(100)
    assert scene.now == 900


# ----- handle_event
def test_window_close_returns_quit(scene):
    assert scene.handle_event(pygame.event.Event(pygame.QUIT)) == Scene.QUIT


def test_escape_opens_then_closes_pause_menu(scene):
    assert scene.handle_event(key(pygame.K_ESCAPE)) is None
    assert scene.pause_open is True

    assert scene.handle_event(key(pygame.K_ESCAPE)) is None
    assert scene.pause_open is False


def test_escape_closes_inventory_without_opening_pause(scene):
    scene.inventory_open = True

    scene.handle_event(key(pygame.K_ESCAPE))

    assert scene.inventory_open is False
    assert scene.pause_open is False


def test_escape_resets_pause_menu_selection(scene):
    scene.pause_menu.selected_index = 1

    scene.handle_event(key(pygame.K_ESCAPE))

    assert scene.pause_menu.selected_index == 0


def test_i_toggles_inventory(scene):
    scene.handle_event(key(pygame.K_i))
    assert scene.inventory_open is True

    scene.handle_event(key(pygame.K_i))
    assert scene.inventory_open is False


def test_i_is_ignored_while_paused(scene):
    scene.pause_open = True

    scene.handle_event(key(pygame.K_i))

    assert scene.inventory_open is False


def test_pause_menu_continue_closes_it(scene):
    scene.handle_event(key(pygame.K_ESCAPE))

    assert scene.handle_event(key(pygame.K_RETURN)) is None
    assert scene.pause_open is False


def test_pause_menu_quit_returns_quit(scene):
    scene.handle_event(key(pygame.K_ESCAPE))
    scene.handle_event(key(pygame.K_DOWN))

    assert scene.handle_event(key(pygame.K_RETURN)) == Scene.QUIT


def test_events_go_to_inventory_ui_only_while_it_is_open(scene, screen, monkeypatch):
    seen = []
    monkeypatch.setattr(
        scene.inventory_ui, "handle_event", lambda e, size: seen.append((e, size))
    )
    event = key(pygame.K_DOWN)

    scene.handle_event(event)
    assert seen == []

    scene.inventory_open = True
    scene.handle_event(event)
    assert seen == [(event, screen.get_size())]


def test_unrelated_event_returns_none(scene):
    assert scene.handle_event(pygame.event.Event(pygame.USEREVENT)) is None


# ----- update: movement
@pytest.mark.parametrize(
    "pressed_key,dx,dy,facing",
    [
        (pygame.K_w, 0, -PLAYER_SPEED, (0, -1)),
        (pygame.K_s, 0, PLAYER_SPEED, (0, 1)),
        (pygame.K_a, -PLAYER_SPEED, 0, (-1, 0)),
        (pygame.K_d, PLAYER_SPEED, 0, (1, 0)),
    ],
)
def test_update_moves_and_turns_player(scene, monkeypatch, pressed_key, dx, dy, facing):
    scene.enemies = []
    press(monkeypatch, pressed_key)
    x, y = scene.player.x, scene.player.y

    assert scene.update(16) is None

    assert (scene.player.x - x, scene.player.y - y) == (dx, dy)
    assert tuple(scene.player.facing) == facing


def test_horizontal_movement_updates_sprite_direction(scene, monkeypatch):
    scene.enemies = []

    press(monkeypatch, pygame.K_a)
    scene.update(16)
    assert scene.facing_right is False

    press(monkeypatch, pygame.K_d)
    scene.update(16)
    assert scene.facing_right is True


def test_vertical_movement_keeps_sprite_direction(scene, monkeypatch):
    scene.enemies = []
    scene.facing_right = False
    press(monkeypatch, pygame.K_w)

    scene.update(16)

    assert scene.facing_right is False


def test_diagonal_input_moves_both_axes_and_faces_last_key_applied(scene, monkeypatch):
    scene.enemies = []
    press(monkeypatch, pygame.K_w, pygame.K_d)
    x, y = scene.player.x, scene.player.y

    scene.update(16)

    assert (scene.player.x - x, scene.player.y - y) == (PLAYER_SPEED, -PLAYER_SPEED)
    assert tuple(scene.player.facing) == (1, 0)  # D is applied after W


def test_update_does_nothing_while_frozen(scene, monkeypatch):
    press(monkeypatch, pygame.K_d, pygame.K_SPACE)
    x = scene.player.x
    enemy = Enemy(scene.player.x + 40, scene.player.y)
    scene.enemies = [enemy]

    for flag in ("inventory_open", "pause_open"):
        setattr(scene, flag, True)
        assert scene.update(16) is None
        setattr(scene, flag, False)

    assert scene.player.x == x
    assert enemy.health == 50


# ----- update: combat and enemies
def test_space_attacks_enemy_in_front_of_player(scene, monkeypatch):
    press(monkeypatch, pygame.K_SPACE)
    enemy = Enemy(scene.player.x + 40, scene.player.y)
    scene.enemies = [enemy]
    scene.now = 0

    scene.update(16)

    assert enemy.health == 50 - scene.player.equipped_item.damage


def test_update_removes_dead_enemies(scene, monkeypatch):
    press(monkeypatch)
    dead = Enemy(0, 0)
    alive = Enemy(9000, 9000)
    dead.take_damage(999)
    scene.enemies = [dead, alive]

    scene.update(16)

    assert scene.enemies == [alive]


def test_update_advances_enemy_ai_with_scene_time(scene, monkeypatch):
    press(monkeypatch)
    enemy = Enemy(scene.player.x + 100, scene.player.y, aggro_range=250)
    scene.enemies = [enemy]
    scene.now = 5000

    scene.update(16)

    assert enemy._now == 5000


# ----- draw
def test_draw_renders_world_without_crashing(scene, screen):
    scene.draw()

    assert screen.get_size() == (1280, 720)


def test_draw_overlays_change_the_picture(scene, screen):
    scene.draw()
    world = surface_bytes(screen)

    scene.inventory_open = True
    scene.draw()
    with_inventory = surface_bytes(screen)
    assert with_inventory != world

    scene.inventory_open = False
    scene.pause_open = True
    scene.draw()
    assert surface_bytes(screen) != world


def test_draw_debug_overlay_does_not_crash(scene, monkeypatch):
    monkeypatch.setattr(game_scene, "DEBUG_OVERLAY", True)

    scene.draw()


def test_main_game_wrapper_runs_a_game_scene(screen, monkeypatch):
    # The wrapper must hand back whatever scene GameScene.run() asks for.
    monkeypatch.setattr(GameScene, "run", lambda self: Scene.MENU)

    assert main_game(screen) == Scene.MENU
