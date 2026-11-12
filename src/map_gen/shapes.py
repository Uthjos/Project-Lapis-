"""Stage shapes: which cells of a rows x cols matrix belong to the stage.

Cells outside the shape become VOID, so every stage is still a plain
rectangular TILE_MAP (the format IsoGrid already understands), just with
VOID padding around non-rectangular outlines.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

Mask = list[list[bool]]


class StageShape(ABC):
    """Base class for stage outlines. Subclass and implement ``contains``."""

    @abstractmethod
    def contains(self, row: int, col: int, rows: int, cols: int) -> bool:
        """True if (row, col) is part of a rows x cols stage."""

    def mask(self, rows: int, cols: int) -> Mask:
        return [[self.contains(r, c, rows, cols) for c in range(cols)] for r in range(rows)]


class Rectangle(StageShape):
    """Every cell is inside. The default."""

    def contains(self, row, col, rows, cols):
        return True


class Ellipse(StageShape):
    """Round/oval island that touches the matrix edges."""

    def __init__(self, padding: float = 0.0):
        self.padding = padding  # extra cells of VOID kept around the edge

    def contains(self, row, col, rows, cols):
        ry = rows / 2 - self.padding
        rx = cols / 2 - self.padding
        dy = (row + 0.5 - rows / 2) / ry
        dx = (col + 0.5 - cols / 2) / rx
        return dx * dx + dy * dy <= 1.0


class Diamond(StageShape):
    """Diamond in tile space. Because IsoGrid rotates the grid 45 degrees, this shows up
    on screen as an upright rectangle that fills a widescreen window nicely."""

    def contains(self, row, col, rows, cols):
        dy = abs(row + 0.5 - rows / 2) / (rows / 2)
        dx = abs(col + 0.5 - cols / 2) / (cols / 2)
        return dx + dy <= 1.0


class MaskShape(StageShape):
    """Hand-drawn outline. Accepts bools/ints or strings like "..##.." ('.' or ' ' = outside).

    The mask is stretched (nearest neighbour) if the requested size differs,
    so one hand-drawn outline can be reused at several stage sizes.
    """

    def __init__(self, rows: Sequence[Sequence[bool | int] | str]):
        self._mask = [
            [ch not in ". " for ch in row] if isinstance(row, str) else [bool(v) for v in row]
            for row in rows
        ]
        if not self._mask or not any(any(r) for r in self._mask):
            raise ValueError("MaskShape needs at least one inside cell")

    def contains(self, row, col, rows, cols):
        src = self._mask
        r = min(row * len(src) // rows, len(src) - 1)
        line = src[r]
        c = min(col * len(line) // cols, len(line) - 1)
        return line[c]
