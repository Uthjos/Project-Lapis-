from dataclasses import dataclass
from enum import IntEnum

import pygame


class Tile(IntEnum):
    """Named IDs for the numbers in TILE_MAP. IntEnum members still equal plain ints."""
    VOID = 0
    FLOOR = 1
    WALL = 2
    PATH = 3
    Water = 4


@dataclass(frozen=True)
class TileType:
    name: str
    texture_file: str | None = None   # None = nothing is drawn
    walkable: bool = False
    # Add future properties here with defaults, e.g.:
    # speed_multiplier: float = 1.0
    # damage_per_second: int = 0


class TileSet:
    def __init__(self, types: dict[int, TileType]):
        self.types = types
        self.textures: dict[int, pygame.Surface] = {}
        self.tile_size = (0, 0)   # size of the base (floor) tile, used for grid math

    def load(self, loader, scale=1, base_id=Tile.FLOOR):
        """Load and scale every texture. Call after pygame.display.set_mode()."""
        for tile_id, t in self.types.items():
            if t.texture_file:
                img = loader(t.texture_file)
                w, h = img.get_size()
                self.textures[tile_id] = pygame.transform.scale(img, (w * scale, h * scale))
        self.tile_size = self.textures[base_id].get_size()

    def is_walkable(self, tile_id) -> bool:
        t = self.types.get(tile_id)
        return t.walkable if t else False   # unknown IDs are solid

    def texture(self, tile_id):
        return self.textures.get(tile_id)   # None for void