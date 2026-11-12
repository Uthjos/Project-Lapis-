"""Voronoi stage generator for Project Lapis.

Quick start:

    from src.iso_math.tile_set import Tile
    from src.game_scene import TILESET
    from src.map_gen import VoronoiMapGenerator

    gen = VoronoiMapGenerator(Tile, TILESET)
    stage = gen.generate(12, 12, seed=42)
    TILE_MAP = stage.tiles                      # same format as the hand-written map
    SLIME_SPAWN_TILES = stage.pick_spawn_tiles(4)
"""

from src.map_gen.generator import StageMap, VoronoiMapGenerator
from src.map_gen.progression import StageProgression
from src.map_gen.regions import DEFAULT_REGIONS, Layer, Region
from src.map_gen.shapes import Diamond, Ellipse, MaskShape, Rectangle, StageShape

__all__ = [
    "DEFAULT_REGIONS",
    "Diamond",
    "Ellipse",
    "Layer",
    "MaskShape",
    "Rectangle",
    "Region",
    "StageMap",
    "StageProgression",
    "StageShape",
    "VoronoiMapGenerator",
]
