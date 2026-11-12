"""Stage-to-stage progression: biome mix that drifts over a run, and stitched edges.

Keyframes map a stage number to region weights. Stages between keyframes get a
linear blend, so e.g. stage 0 is mostly meadow, stage 10 mostly rock field, and
stages 1-9 slide gradually between them. Each stage is also stitched to the one
before it so the boundary the player walks across lines up.
"""

from __future__ import annotations

import random
from collections.abc import Mapping

from src.map_gen.generator import StageMap, VoronoiMapGenerator
from src.map_gen.shapes import StageShape


class StageProgression:
    def __init__(
        self,
        generator: VoronoiMapGenerator,
        keyframes: Mapping[int, Mapping[str, float]],
        run_seed: int | None = None,
        exit_side: str = "right",
        stitch_depth: int = 2,
    ):
        if not keyframes:
            raise ValueError("Need at least one keyframe")
        self.generator = generator
        self.keyframes = dict(sorted(keyframes.items()))
        self.run_seed = random.randrange(2**31) if run_seed is None else run_seed
        self.exit_side = exit_side
        self.stitch_depth = stitch_depth
        self.stages: list[StageMap] = []

    def weights_for(self, stage: int) -> dict[str, float]:
        """Region weights for a stage, linearly blended between the nearest keyframes."""
        keys = list(self.keyframes)
        if stage <= keys[0]:
            return dict(self.keyframes[keys[0]])
        if stage >= keys[-1]:
            return dict(self.keyframes[keys[-1]])
        hi = next(k for k in keys if k >= stage)
        lo = keys[keys.index(hi) - 1]
        t = (stage - lo) / (hi - lo)
        a, b = self.keyframes[lo], self.keyframes[hi]
        # A region a keyframe doesn't mention keeps its default Region.weight.
        default = lambda n: self.generator.regions[n].weight
        return {
            n: a.get(n, default(n)) * (1 - t) + b.get(n, default(n)) * t
            for n in set(a) | set(b)
        }

    def stage_seed(self, stage: int) -> int:
        """Per-stage seed derived from the run seed, so any stage can be rebuilt on its own
        (handy for multiplayer: share run_seed and every client builds identical stages)."""
        return random.Random(self.run_seed * 1_000_003 + stage).randrange(2**31)

    def next_stage(self, rows: int, cols: int, shape: StageShape | None = None) -> StageMap:
        """Build the next stage, stitched to the previous one if there is one."""
        index = len(self.stages)
        previous = self.stages[-1] if self.stages else None
        stage = self.generator.generate(
            rows,
            cols,
            seed=self.stage_seed(index),
            shape=shape,
            region_weights=self.weights_for(index),
            previous=previous,
            enter_from=_opposite(self.exit_side) if previous else None,
            stitch_depth=self.stitch_depth,
        )
        self.stages.append(stage)
        return stage


def _opposite(side: str) -> str:
    return {"top": "bottom", "bottom": "top", "left": "right", "right": "left"}[side]
