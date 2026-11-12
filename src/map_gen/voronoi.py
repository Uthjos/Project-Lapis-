"""Grid Voronoi math: site placement, Lloyd relaxation and cell assignment.

If maps grow to hundreds of tiles a side, swap ``assign_cells``
for scipy.spatial.cKDTree.query(points, k=2)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from random import Random

from src.map_gen.shapes import Mask

Point = tuple[float, float]  # (row, col) in tile units, may be fractional


def inside_cells(mask: Mask) -> list[tuple[int, int]]:
    """Find all inside cells within a tile."""
    return [(r, c) for r, line in enumerate(mask) for c, inside in enumerate(line) if inside]


def place_sites(mask: Mask, count: int, rng: Random, candidates: int = 12) -> list[Point]:
    """Spread ``count`` sites over the inside cells (Mitchell's best-candidate).

    Each new site is the candidate farthest from all existing sites, which gives
    an even, blue-noise-like spread for any stage shape.
    """
    cells = inside_cells(mask)
    if not cells:
        raise ValueError("Stage shape has no inside cells")
    count = max(1, min(count, len(cells)))
    sites: list[Point] = []
    for _ in range(count):
        best, best_d = None, -1.0
        for _ in range(candidates):
            r, c = rng.choice(cells)
            p = (r + rng.random(), c + rng.random())
            d = min((_dist2(p, s) for s in sites), default=math.inf)
            if d > best_d:
                best, best_d = p, d
        sites.append(best)
    return sites


def relax(sites: list[Point], mask: Mask, iterations: int) -> list[Point]:
    """Lloyd relaxation: move each site to the centroid of its cell. Evens out cell sizes."""
    cells = inside_cells(mask)
    for _ in range(iterations):
        sums = [[0.0, 0.0, 0] for _ in sites]
        for r, c in cells:
            i = _nearest(((r + 0.5, c + 0.5)), sites)
            acc = sums[i]
            acc[0] += r + 0.5
            acc[1] += c + 0.5
            acc[2] += 1
        sites = [(a[0] / a[2], a[1] / a[2]) if a[2] else s for a, s in zip(sums, sites)]
    return sites


@dataclass
class CellMap:
    """
    Cell map class. holds list matrix of cell's site indices.
    holds list of depth for each cell
    """
    owner: list[list[int]]  # site index per tile, -1 outside the shape
    depth: list[list[float]]  # 1.0 at a site, 0.0 on a border between two cells


def assign_cells(mask: Mask, sites: list[Point], warp: ValueNoise | None = None,
                 warp_strength: float = 0.0) -> CellMap:
    """Nearest-site lookup for every inside tile, plus how deep inside its cell it is.

    Goes through every tile inside the stage shape.
    For each tile it records which Voronoi cell the tile belongs to and
    how deep inside that cell it is.

    ``warp`` displaces the lookup point by smooth noise so cell borders wobble
    organically instead of being straight lines.
    """
    rows, cols = len(mask), len(mask[0]) if mask else 0
    owner = [[-1] * cols for _ in range(rows)]
    depth = [[0.0] * cols for _ in range(rows)]
    for r, c in inside_cells(mask):
        point = _lookup_point(r, c, warp, warp_strength)
        best, d1, d2 = _two_nearest(point, sites)
        owner[r][c] = best
        depth[r][c] = _cell_depth(d1, d2, max(rows, cols))
    return CellMap(owner, depth)

def _lookup_point(row: int, col: int, warp: ValueNoise | None, strength: float) -> Point:
    """Center of tile (row, col), nudged by the warp noise when one is given."""
    point = (row + 0.5, col + 0.5)
    if warp is None or not strength:
        return point
    return (point[0] + warp.sample(row, col, 0) * strength,
            point[1] + warp.sample(row, col, 1) * strength)


def _two_nearest(point: Point, sites: list[Point]) -> tuple[int, float, float]:
    """Index of the closest site, plus squared distances to the closest and second closest.

    With a single site the second distance is infinity. Ties go to the lower index.
    """
    nearest_index, d1, d2 = 0, math.inf, math.inf
    for i, site in enumerate(sites):
        d = _dist2(point, site)
        if d < d1:
            nearest_index, d1, d2 = i, d, d1
        elif d < d2:
            d2 = d
    return nearest_index, d1, d2


def _cell_depth(d1: float, d2: float, map_span: int) -> float:
    """How deep inside its cell a point is: 1.0 at the site, 0.0 on a cell border.

    ``d1``/``d2`` are squared distances to the nearest and second-nearest site. A point
    on a border is equally far from both, so the ratio of the real distances is 1 there.
    With only one site there is no border, so depth fades with distance across the map.
    """
    if d2 == math.inf:
        return max(0.0, 1.0 - math.sqrt(d1) / map_span)
    return 1.0 - math.sqrt(d1 / d2)


class ValueNoise:
    """Small smooth 2D noise in [-1, 1] (bilinear value noise), seeded and deterministic."""

    def __init__(self, rng: Random, scale: float = 4.0):
        self.scale = scale
        self._seed = rng.getrandbits(32)

    def _lattice(self, x: int, y: int, channel: int) -> float:
        h = (x * 374761393 + y * 668265263 + channel * 2147483647 + self._seed) & 0xFFFFFFFF
        h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
        return (h & 0xFFFF) / 0x7FFF - 1.0

    def sample(self, row: float, col: float, channel: int = 0) -> float:
        x, y = col / self.scale, row / self.scale
        x0, y0 = math.floor(x), math.floor(y)
        tx, ty = _smooth(x - x0), _smooth(y - y0)
        a = self._lattice(x0, y0, channel)
        b = self._lattice(x0 + 1, y0, channel)
        c = self._lattice(x0, y0 + 1, channel)
        d = self._lattice(x0 + 1, y0 + 1, channel)
        return (a + (b - a) * tx) + ((c + (d - c) * tx) - (a + (b - a) * tx)) * ty


def _smooth(t: float) -> float:
    return t * t * (3 - 2 * t)


def _dist2(a: Point, b: Point) -> float:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def _nearest(p: Point, sites: list[Point]) -> int:
    return min(range(len(sites)), key=lambda i: _dist2(p, sites[i]))
