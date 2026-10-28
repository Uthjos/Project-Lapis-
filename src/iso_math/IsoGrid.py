import pygame

from src.iso_math.TileSet import Tile


class IsoGrid:
    def __init__(self, tile_map, tileset, width, height, top_height=None):
        self.tile_map = tile_map
        self.tileset = tileset
        self.width, self.height = width, height

        self.tile_w, self.tile_h = tileset.tile_size
        self.top_h = top_height or self.tile_w // 2
        self.step_x = self.tile_w // 2
        self.step_y = self.top_h // 2
        self.rows = len(tile_map)
        self.cols = max(len(r) for r in tile_map)

        map_w = (self.rows + self.cols - 2) * self.step_x + self.tile_w
        map_h = (self.rows + self.cols - 2) * self.step_y + self.tile_h
        self.origin_x = (width - map_w) // 2 + (self.rows - 1) * self.step_x
        self.origin_y = (height - map_h) // 2

    # ---------- geometry (unchanged) ----------
    def tile_topleft(self, row, col):
        return (self.origin_x + (col - row) * self.step_x,
                self.origin_y + (col + row) * self.step_y)

    def tile_center(self, row, col):
        x, y = self.tile_topleft(row, col)
        return (x + self.tile_w / 2, y + self.top_h / 2)

    def tile_diamond(self, row, col):
        cx, cy = self.tile_center(row, col)
        return [(cx, cy - self.step_y), (cx + self.step_x, cy),
                (cx, cy + self.step_y), (cx - self.step_x, cy)]

    # ---------- lookup ----------
    def tile_at(self, px, py):
        cx, cy = self.tile_center(0, 0)
        a = (px - cx) / self.step_x
        b = (py - cy) / self.step_y
        col = round((a + b) / 2)
        row = round((b - a) / 2)
        if 0 <= row < self.rows and 0 <= col < len(self.tile_map[row]):
            return self.tile_map[row][col]
        return Tile.VOID

    def is_walkable(self, px, py):
        return self.tileset.is_walkable(self.tile_at(px, py))

    # ---------- drawing (moved here from main.py) ----------
    def render(self, background_color=(0, 0, 0)):
        """Pre-render the whole map to one surface so each frame is a single blit."""
        surface = pygame.Surface((self.width, self.height))
        surface.fill(background_color)
        for row in range(self.rows):
            for col in range(len(self.tile_map[row])):
                tex = self.tileset.texture(self.tile_map[row][col])
                if tex is None:
                    continue
                x, y = self.tile_topleft(row, col)
                # Bottom-align so taller sprites (walls) rise upward from the same base
                y += self.tile_h - tex.get_height()
                surface.blit(tex, (x, y))
        return surface