"""Region (biome) definitions: what a Voronoi cell is filled with.

Every Voronoi cell is given one Region. Inside a cell, each tile has a
``depth`` between 0.0 (on the border with a neighbouring cell) and 1.0 (at
the cell's centre). A Region is a list of Layers; the deepest layer whose
``min_depth`` the tile reaches decides which tiles can appear there. That is
what gives ponds a water core with a dirt shore, rock fields a boulder core
with rubble around it, and so on.

Tiles are named by enum member *name* (e.g. "WATER") so these definitions
work with any Tile enum that has those names; names your enum or tileset do
not have are dropped by the generator.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from random import Random


@dataclass(frozen=True)
class Layer:
    min_depth: float  # 0.0 = reaches the cell border, 1.0 = only the exact centre
    tiles: Mapping[str, float]  # tile name -> relative weight


@dataclass(frozen=True)
class Region:
    name: str
    layers: tuple[Layer, ...]
    weight: float = 1.0  # how often this region is picked for a cell

    def __post_init__(self):
        if not self.layers:
            raise ValueError(f"Region {self.name!r} needs at least one layer")
        # Deepest first so pick() can take the first match.
        object.__setattr__(
            self, "layers", tuple(sorted(self.layers, key=lambda l: l.min_depth, reverse=True))
        )
        if self.layers[-1].min_depth > 0:
            raise ValueError(f"Region {self.name!r} needs a layer with min_depth 0")

    def pick(self, depth: float, rng: Random) -> str:
        for layer in self.layers:
            if depth >= layer.min_depth:
                names, weights = zip(*layer.tiles.items())
                return rng.choices(names, weights)[0]
        raise AssertionError("unreachable: last layer has min_depth 0")


DEFAULT_REGIONS: tuple[Region, ...] = (
    Region(
        "meadow",
        (Layer(0.0, {"GRASS_CLEAN": 0.86, "LIGHT_DIRT": 0.09, "SMALL_ROCK": 0.05}),),
        weight=3,
    ),
    Region(
        "dirt_patch",
        (
            Layer(0.55, {"DARK_DIRT": 1}),
            Layer(0.25, {"MED_DIRT": 0.8, "DARK_DIRT": 0.2}),
            Layer(0.0, {"LIGHT_DIRT": 0.7, "GRASS_CLEAN": 0.3}),
        ),
        weight=2,
    ),
    Region(
        "pond",
        (
            Layer(0.45, {"WATER": 1}),
            Layer(0.25, {"DARK_DIRT": 0.5, "MED_DIRT": 0.5}),
            Layer(0.0, {"GRASS_CLEAN": 0.7, "LIGHT_DIRT": 0.3}),
        ),
        weight=1,
    ),
    Region(
        "rock_field",
        (
            Layer(0.6, {"LARGE_ROCK": 1}),
            Layer(0.35, {"MEDIUM_ROCK": 0.7, "SMALL_ROCK": 0.3}),
            Layer(0.0, {"SMALL_ROCK": 0.5, "GRASS_CLEAN": 0.3, "MED_DIRT": 0.2}),
        ),
        weight=1,
    ),
)
