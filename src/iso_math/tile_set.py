from dataclasses import dataclass
from enum import IntEnum, auto

import pygame


class Tile(IntEnum):
    """Named IDs for the numbers in a tile map. IntEnum members still equal plain ints."""

    VOID = 0
    GRASS_CLEAN = auto()
    WALL = auto()
    PATH = auto()
    WATER = auto()
    LIGHT_DIRT = auto()
    MED_DIRT = auto()
    DARK_DIRT = auto()
    SMALL_ROCK = auto()
    MEDIUM_ROCK = auto()
    LARGE_ROCK = auto()


@dataclass(frozen=True)
class TileType:
    """Named IDs for a tile type."""
    name: str
    texture_file: str | None = None  # None = nothing is drawn
    walkable: bool = False
    sight_blocking: bool = False
    # Add future properties here with defaults, e.g.:
    # speed_multiplier: float = 1.0
    # damage_per_second: int = 0


class TileSet:
    """Class representing a tile set."""
    def __init__(self, types: dict[int, TileType]):
        self.types = types
        self.textures: dict[int, pygame.Surface] = {}
        self.tile_size = (0, 0)  # size of the base (floor) tile, used for grid math

    def load(self, loader, scale=1, base_id=Tile.GRASS_CLEAN):
        """Load and scale every texture. Call after pygame.display.set_mode()."""
        for tile_id, t in self.types.items():
            if t.texture_file:
                img = loader(t.texture_file)
                w, h = img.get_size()
                self.textures[tile_id] = pygame.transform.scale(
                    img, (w * scale, h * scale)
                )
        self.tile_size = self.textures[base_id].get_size()

    def is_walkable(self, tile_id) -> bool:
        """Check if a tile is walkable."""
        t = self.types.get(tile_id)
        return t.walkable if t else False  # unknown IDs are solid

    def texture(self, tile_id):
        """Get the texture for a tile_id."""
        return self.textures.get(tile_id)  # None for void

    def is_sight_blocking(self, tile_id) -> bool:
        """Check if a tile is sight blocking."""
        t = self.types.get(tile_id)
        return t.sight_blocking if t else False
