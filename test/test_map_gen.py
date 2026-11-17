from collections import deque

import pytest

from src.iso_math.tile_set import Tile, TileSet, TileType
from src.map_gen import (
    Diamond,
    Ellipse,
    Layer,
    MaskShape,
    Region,
    StageProgression,
    VoronoiMapGenerator,
)

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


@pytest.fixture
def gen():
    return VoronoiMapGenerator(Tile, TILESET)


def reachable(stage, start):
    seen, todo = {start}, deque([start])
    while todo:
        r, c = todo.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (r + dr, c + dc)
            if q not in seen and stage.is_walkable(*q):
                seen.add(q)
                todo.append(q)
    return seen


# ---------- format ----------
def test_output_matches_tile_map_format(gen):
    stage = gen.generate(10, 14, seed=1)

    assert len(stage.tiles) == 10
    assert all(len(row) == 14 for row in stage.tiles)
    assert all(type(t) is int for row in stage.tiles for t in row)


def test_only_textured_tiles_from_the_tileset_are_used(gen):
    allowed = {int(t) for t, tt in TILESET.types.items() if tt.texture_file}
    for seed in range(20):
        stage = gen.generate(12, 12, seed=seed)
        assert {t for row in stage.tiles for t in row} <= allowed  # no WALL/PATH/VOID


def test_same_seed_same_map(gen):
    assert gen.generate(12, 12, seed=7).tiles == gen.generate(12, 12, seed=7).tiles


def test_different_seeds_differ(gen):
    assert gen.generate(12, 12, seed=1).tiles != gen.generate(12, 12, seed=2).tiles


def test_seed_is_reported_so_random_maps_can_be_rebuilt(gen):
    stage = gen.generate(8, 8)
    assert gen.generate(8, 8, seed=stage.seed).tiles == stage.tiles


# ---------- playability ----------
@pytest.mark.parametrize("seed", range(40))
def test_spawn_is_walkable_and_every_walkable_tile_is_reachable(gen, seed):
    stage = gen.generate(14, 14, seed=seed)

    assert stage.is_walkable(*stage.spawn)
    assert reachable(stage, stage.spawn) == set(stage.walkable_cells())


def test_connectivity_holds_with_mostly_blocking_regions():
    gen = VoronoiMapGenerator(
        Tile, TILESET,
        regions=[Region("lake", (Layer(0.0, {"WATER": 1}),)),
                 Region("islet", (Layer(0.0, {"GRASS_CLEAN": 1}),), weight=0.5)],
        cell_size=3,
    )
    for seed in range(10):
        stage = gen.generate(12, 12, seed=seed)
        assert reachable(stage, stage.spawn) == set(stage.walkable_cells())


def test_pick_spawn_tiles_are_walkable_and_spread_out(gen):
    stage = gen.generate(14, 14, seed=3)
    spots = stage.pick_spawn_tiles(4, rng=0, min_distance=3)

    assert len(spots) == 4
    for r, c in spots:
        assert stage.is_walkable(r, c)
        assert abs(r - stage.spawn[0]) + abs(c - stage.spawn[1]) >= 3


# ---------- shapes & sizes ----------
@pytest.mark.parametrize("shape", [Ellipse(), Diamond()])
def test_shapes_leave_void_outside(gen, shape):
    stage = gen.generate(15, 15, seed=4, shape=shape)
    mask = shape.mask(15, 15)

    for r in range(15):
        for c in range(15):
            assert (stage.tiles[r][c] == Tile.VOID) == (not mask[r][c])


def test_mask_shape_is_stretched_to_requested_size(gen):
    l_shape = MaskShape(["##..", "##..", "####", "####"])
    stage = gen.generate(8, 8, seed=2, shape=l_shape)

    assert stage.tiles[0][7] == Tile.VOID  # top-right is cut out
    assert stage.tiles[7][7] != Tile.VOID


@pytest.mark.parametrize("rows,cols", [(1, 1), (3, 20), (30, 30)])
def test_odd_sizes(gen, rows, cols):
    stage = gen.generate(rows, cols, seed=0)
    assert len(stage.tiles) == rows and len(stage.tiles[0]) == cols
    assert stage.is_walkable(*stage.spawn)


# ---------- regions ----------
def test_region_weights_can_remove_regions(gen):
    stage = gen.generate(16, 16, seed=5, region_weights={"pond": 0, "rock_field": 0})
    used = {t for row in stage.tiles for t in row}

    assert Tile.WATER not in used
    assert Tile.LARGE_ROCK not in used


def test_unknown_region_weight_raises(gen):
    with pytest.raises(ValueError):
        gen.generate(8, 8, region_weights={"lava": 1})


def test_tiles_missing_from_tileset_are_dropped():
    gen = VoronoiMapGenerator(
        Tile, TILESET, regions=[Region("walls", (Layer(0.0, {"WALL": 1}),))]
    )
    stage = gen.generate(6, 6, seed=0)

    assert {t for row in stage.tiles for t in row} == {int(Tile.GRASS_CLEAN)}


def test_bad_bridge_tile_raises():
    with pytest.raises(ValueError):
        VoronoiMapGenerator(Tile, TILESET, bridge_tile="WATER")


# ---------- progression ----------
def test_stitched_edge_matches_previous_exit(gen):
    first = gen.generate(10, 10, seed=1)
    second = gen.generate(10, 10, seed=2, previous=first, enter_from="left")

    exit_cols = first.edge("right", 2)
    entry_cols = second.edge("left", 2)
    walk = first.walkable_ids
    for exit_line, entry_line in zip(exit_cols, entry_cols):
        for a, b in zip(exit_line, entry_line):
            # Copied exactly, except where a path had to be carved through a blocker.
            assert a == b or (a not in walk and b == gen.bridge_id)


def test_stitched_spawn_is_on_entry_side(gen):
    first = gen.generate(10, 10, seed=1)
    second = gen.generate(10, 10, seed=2, previous=first, enter_from="left")

    assert second.spawn[1] <= 1


def test_progression_blends_weights_between_keyframes(gen):
    prog = StageProgression(gen, {0: {"meadow": 4, "rock_field": 0}, 10: {"meadow": 0, "rock_field": 4}})

    mid = prog.weights_for(5)
    assert mid["meadow"] == pytest.approx(2)
    assert mid["rock_field"] == pytest.approx(2)
    assert prog.weights_for(20) == {"meadow": 0, "rock_field": 4}


def test_progression_is_reproducible_from_run_seed(gen):
    a = StageProgression(gen, {0: {}}, run_seed=99)
    b = StageProgression(gen, {0: {}}, run_seed=99)

    for _ in range(3):
        assert a.next_stage(10, 10).tiles == b.next_stage(10, 10).tiles


def test_progression_handles_changing_sizes_and_shapes(gen):
    prog = StageProgression(gen, {0: {}}, run_seed=3)

    s1 = prog.next_stage(10, 10)
    s2 = prog.next_stage(14, 8, shape=Ellipse())
    s3 = prog.next_stage(20, 20, shape=Diamond())

    for s in (s1, s2, s3):
        assert reachable(s, s.spawn) == set(s.walkable_cells())
