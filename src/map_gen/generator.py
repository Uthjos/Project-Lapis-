"""VoronoiMapGenerator: random TILE_MAPs for IsoGrid, built from Voronoi regions.

Pipeline for one stage:
  1. shape mask        -> which cells exist (everything else is VOID)
  2. Voronoi sites     -> spread over the shape, relaxed so cells are similar sizes
  3. region per cell   -> meadow / pond / rock field ... (weighted random)
  4. tile per cell     -> chosen by how deep inside its Voronoi cell it is
  5. stitch            -> optionally copy the previous stage's exit edge into this entry
  6. spawn + connect   -> clear the spawn, then carve the cheapest paths so every
                          walkable tile is reachable from the spawn
"""

from __future__ import annotations

import random
from collections import deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import IntEnum

from src.map_gen.regions import DEFAULT_REGIONS, Layer, Region
from src.map_gen.shapes import Rectangle, StageShape
from src.map_gen.voronoi import Point, ValueNoise, assign_cells, place_sites, relax

SIDES = ("top", "bottom", "left", "right")  # matrix sides: top = row 0, left = col 0
OPPOSITE = {"top": "bottom", "bottom": "top", "left": "right", "right": "left"}
NEIGHBOURS = ((1, 0), (-1, 0), (0, 1), (0, -1))


@dataclass
class StageMap:
    """Stage Map class. contains attributes about the stage, including spawn points, seed, sites, tiles"""
    tiles: list[list[int]]  # same format as TILE_MAP: plain ints, VOID outside the shape
    spawn: tuple[int, int]  # (row, col) the player should start on
    seed: int  # pass back into generate() to rebuild the exact same stage
    sites: list[Point] = field(repr=False)
    site_regions: list[str] = field(repr=False)
    walkable_ids: frozenset[int] = field(repr=False)
    void_id: int = 0

    @property
    def rows(self) -> int:
        """The rows of the stage map."""
        return len(self.tiles)

    @property
    def cols(self) -> int:
        """The columns of the stage map."""
        return max((len(r) for r in self.tiles), default=0)

    def is_walkable(self, row: int, col: int) -> bool:
        """returns if a tile is walkable."""
        return (0 <= row < self.rows and 0 <= col < len(self.tiles[row])
                and self.tiles[row][col] in self.walkable_ids)

    def walkable_cells(self) -> list[tuple[int, int]]:
        """returns list of tiles that are walkable."""
        return [(r, c) for r, line in enumerate(self.tiles)
                for c, t in enumerate(line) if t in self.walkable_ids]

    def pick_spawn_tiles(self, count: int, rng: random.Random | int | None = None,
                         min_distance: int = 4) -> list[tuple[int, int]]:
        """Walkable tiles for enemies, at least ``min_distance`` tiles (Manhattan) from the
        player spawn and from each other where possible. Drop-in for SLIME_SPAWN_TILES."""
        rng = rng if isinstance(rng, random.Random) else random.Random(rng)
        candidates = [p for p in self.walkable_cells() if _manhattan(p, self.spawn) >= min_distance]
        rng.shuffle(candidates)
        picked: list[tuple[int, int]] = []
        for p in candidates:
            if all(_manhattan(p, q) >= min_distance for q in picked):
                picked.append(p)
                if len(picked) == count:
                    break
        return picked

    def edge(self, side: str, depth: int = 1) -> list[list[int]]:
        """The outer ``depth`` lines of the map on ``side``, each read left->right / top->bottom,
        outermost line first."""
        if side not in SIDES:
            raise ValueError(f"side must be one of {SIDES}")
        rows, cols = self.rows, self.cols
        get = lambda r, c: self.tiles[r][c] if c < len(self.tiles[r]) else self.void_id
        lines = []
        for k in range(min(depth, rows if side in ("top", "bottom") else cols)):
            if side == "top":
                lines.append([get(k, c) for c in range(cols)])
            elif side == "bottom":
                lines.append([get(rows - 1 - k, c) for c in range(cols)])
            elif side == "left":
                lines.append([get(r, k) for r in range(rows)])
            else:
                lines.append([get(r, cols - 1 - k) for r in range(rows)])
        return lines


class VoronoiMapGenerator:
    """Builds StageMaps for a Tile enum + TileSet pair.

    tile_enum   the IntEnum class (Tile). Region tile names are looked up on it.
    tileset     the TileSet; only tiles it defines *with a texture* are placed, and its
                walkable flags drive spawn clearing and connectivity.
    regions     Region definitions (see regions.py). Defaults cover the current tileset.
    bridge_tile tile name used to clear the spawn and carve paths through blockers.
    cell_size   average Voronoi cell width in tiles (bigger = fewer, larger regions).
    """

    def __init__(
        self,
        tile_enum: type[IntEnum],
        tileset,
        regions: Sequence[Region] = DEFAULT_REGIONS,
        bridge_tile: str = "GRASS_CLEAN",
        cell_size: float = 4.0,
        relax_iterations: int = 2,
        warp_strength: float = 1.2,
        warp_scale: float = 4.0,
    ):
        self.tile_enum = tile_enum
        self.tileset = tileset
        self.void_id = int(tile_enum["VOID"]) if "VOID" in tile_enum.__members__ else 0
        self.placeable = {
            name: int(member) for name, member in tile_enum.__members__.items()
            if member in tileset.types and tileset.types[member].texture_file
        }
        self.walkable_ids = frozenset(i for i in self.placeable.values() if tileset.is_walkable(i))
        if not self.walkable_ids:
            raise ValueError("Tileset has no walkable tiles with textures")
        if bridge_tile not in self.placeable or self.placeable[bridge_tile] not in self.walkable_ids:
            raise ValueError(f"bridge_tile {bridge_tile!r} must be a walkable, textured tile")
        self.bridge_id = self.placeable[bridge_tile]
        self.regions = {r.name: self._resolve(r) for r in regions}
        self.cell_size = cell_size
        self.relax_iterations = relax_iterations
        self.warp_strength = warp_strength
        self.warp_scale = warp_scale

    # ---------- public ----------
    def generate(
        self,
        rows: int,
        cols: int,
        *,
        seed: int | None = None,
        shape: StageShape | None = None,
        region_weights: Mapping[str, float] | None = None,
        previous: StageMap | None = None,
        enter_from: str | None = None,
        stitch_depth: int = 2,
        spawn: tuple[int, int] | None = None,
    ) -> StageMap:
        """Generate one stage.

        region_weights  override Region.weight per region name (0 removes it). This is
                        the knob StageProgression turns between stages.
        previous, enter_from
                        copy ``previous``'s opposite edge into this stage's ``enter_from``
                        side, so walking off one stage's right edge lands on matching
                        ground at the next stage's left edge.
        spawn           (row, col) for the player. Defaults to the middle of the entry
                        edge when stitching, otherwise the cell nearest the centre.
        """
        if rows < 1 or cols < 1:
            raise ValueError("rows and cols must be at least 1")
        seed = random.randrange(2**31) if seed is None else seed
        rng = random.Random(seed)
        mask = (shape or Rectangle()).mask(rows, cols)

        # 1-2. Voronoi cells
        inside = sum(map(sum, mask))
        if not inside:
            raise ValueError("Stage shape has no inside cells at this size")
        n_sites = max(1, round(inside / (self.cell_size ** 2)))
        sites = relax(place_sites(mask, n_sites, rng), mask, self.relax_iterations)
        warp = ValueNoise(rng, self.warp_scale)
        cells = assign_cells(mask, sites, warp, self.warp_strength)

        # 3. region per cell
        names, weights = self._region_table(region_weights)
        site_regions = rng.choices(names, weights, k=len(sites))

        # 4. tiles
        tiles = [[self.void_id] * cols for _ in range(rows)]
        for r in range(rows):
            for c in range(cols):
                owner = cells.owner[r][c]
                if owner >= 0:
                    name = self.regions[site_regions[owner]].pick(cells.depth[r][c], rng)
                    tiles[r][c] = self.placeable[name]

        # 5. stitch to the previous stage
        if previous is not None or enter_from is not None:
            if previous is None or enter_from not in SIDES:
                raise ValueError(f"stitching needs previous and enter_from in {SIDES}")
            self._stitch(tiles, mask, previous, enter_from, stitch_depth)

        # 6. spawn + connectivity
        spawn = self._choose_spawn(mask, spawn, enter_from)
        self._clear(tiles, mask, spawn)
        self._connect(tiles, mask, spawn)

        return StageMap(tiles, spawn, seed, sites, site_regions, self.walkable_ids, self.void_id)

    # ---------- setup helpers ----------
    def _resolve(self, region: Region) -> Region:
        """Drop tile names this enum/tileset can't place;
        empty layers fall back to the bridge tile."""
        bridge = next(n for n, i in self.placeable.items() if i == self.bridge_id)
        layers = []
        for layer in region.layers:
            tiles = {n: w for n, w in layer.tiles.items() if n in self.placeable and w > 0}
            layers.append(Layer(layer.min_depth, tiles or {bridge: 1.0}))
        return Region(region.name, tuple(layers), region.weight)

    def _region_table(self, overrides):
        overrides = overrides or {}
        unknown = set(overrides) - set(self.regions)
        if unknown:
            raise ValueError(f"Unknown regions in region_weights: {sorted(unknown)}")
        table = [(n, overrides.get(n, r.weight)) for n, r in self.regions.items()]
        table = [(n, w) for n, w in table if w > 0]
        if not table:
            raise ValueError("All region weights are zero")
        names, weights = zip(*table)
        return list(names), list(weights)

    # ---------- stitching ----------
    def _stitch(self, tiles, mask, previous: StageMap, side: str, depth: int):
        rows, cols = len(tiles), len(tiles[0])
        source = previous.edge(OPPOSITE[side], depth)
        along = cols if side in ("top", "bottom") else rows
        for k, line in enumerate(source):
            for i in range(along):
                t = line[min(i * len(line) // along, len(line) - 1)]  # resample to new length
                if t == previous.void_id:
                    continue
                r, c = {
                    "top": (k, i), "bottom": (rows - 1 - k, i),
                    "left": (i, k), "right": (i, cols - 1 - k),
                }[side]
                if 0 <= r < rows and 0 <= c < cols and mask[r][c] and t in self.placeable.values():
                    tiles[r][c] = t

    # ---------- spawn & connectivity ----------
    def _choose_spawn(self, mask, spawn, enter_from):
        rows, cols = len(mask), len(mask[0])
        if spawn is not None:
            r, c = spawn
            if not (0 <= r < rows and 0 <= c < cols and mask[r][c]):
                raise ValueError(f"spawn {spawn} is outside the stage shape")
            return spawn
        target = {
            None: (rows / 2, cols / 2), "top": (0, cols / 2), "bottom": (rows - 1, cols / 2),
            "left": (rows / 2, 0), "right": (rows / 2, cols - 1),
        }[enter_from]
        # Step one tile in from the entry edge so the spawn isn't right on the border.
        inward = {None: (0, 0), "top": (1, 0), "bottom": (-1, 0), "left": (0, 1), "right": (0, -1)}
        target = (target[0] + inward[enter_from][0], target[1] + inward[enter_from][1])
        return min(
            ((r, c) for r in range(rows) for c in range(cols) if mask[r][c]),
            key=lambda p: (p[0] + 0.5 - target[0]) ** 2 + (p[1] + 0.5 - target[1]) ** 2,
        )

    def _clear(self, tiles, mask, spawn):
        """Make the spawn and its direct neighbours walkable."""
        r0, c0 = spawn
        for dr, dc in ((0, 0), *NEIGHBOURS):
            r, c = r0 + dr, c0 + dc
            if (0 <= r < len(tiles) and 0 <= c < len(tiles[0]) and mask[r][c]
                    and tiles[r][c] not in self.walkable_ids):
                tiles[r][c] = self.bridge_id

    def _connect(self, tiles, mask, spawn):
        """Join every walkable pocket to the spawn's area through the fewest blocked tiles.

        Uses a 0-1 BFS from the reachable area: stepping onto a walkable tile costs 0,
        onto a blocker costs 1. When the search reaches a cut-off pocket, the blockers
        on that path become the bridge tile. Repeats until nothing is cut off.
        """
        rows, cols = len(tiles), len(tiles[0])
        walk = self.walkable_ids
        while True:
            reached = _flood(tiles, mask, [spawn], walk)
            pockets = [(r, c) for r in range(rows) for c in range(cols)
                       if mask[r][c] and tiles[r][c] in walk and (r, c) not in reached]
            if not pockets:
                return
            pocket_set = set(pockets)
            cost = {p: 0 for p in reached}
            prev: dict[tuple[int, int], tuple[int, int] | None] = {p: None for p in reached}
            dq = deque(reached)
            hit = None
            while dq:
                p = dq.popleft()
                if p in pocket_set:
                    hit = p
                    break
                for dr, dc in NEIGHBOURS:
                    q = (p[0] + dr, p[1] + dc)
                    if not (0 <= q[0] < rows and 0 <= q[1] < cols and mask[q[0]][q[1]]):
                        continue
                    step = 0 if tiles[q[0]][q[1]] in walk else 1
                    if cost[p] + step < cost.get(q, 1 << 30):
                        cost[q] = cost[p] + step
                        prev[q] = p
                        (dq.appendleft if step == 0 else dq.append)(q)
            if hit is None:  # pocket unreachable even through blockers (split shape): drop it
                for r, c in pockets:
                    tiles[r][c] = self.void_id
                return
            p = hit
            while p is not None:
                if tiles[p[0]][p[1]] not in walk:
                    tiles[p[0]][p[1]] = self.bridge_id
                p = prev[p]


def _flood(tiles, mask, starts, walk):
    rows, cols = len(tiles), len(tiles[0])
    seen = set(starts)
    stack = list(starts)
    while stack:
        r, c = stack.pop()
        for dr, dc in NEIGHBOURS:
            q = (r + dr, c + dc)
            if (q not in seen and 0 <= q[0] < rows and 0 <= q[1] < cols
                    and mask[q[0]][q[1]] and tiles[q[0]][q[1]] in walk):
                seen.add(q)
                stack.append(q)
    return seen


def _manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
