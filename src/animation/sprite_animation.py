"""Helpers for sprite-sheet animations (horizontal strips of equal-size frames)."""

import pygame


def load_strip(path, frame_w, frame_h, scale=1):
    """Slice a horizontal sprite strip into frames. Needs the display (convert_alpha).

    scale enlarges every frame with nearest-neighbour, so pixel art stays crisp.
    """
    sheet = pygame.image.load(str(path)).convert_alpha()
    frames = [
        sheet.subsurface((i * frame_w, 0, frame_w, frame_h)).copy()
        for i in range(sheet.get_width() // frame_w)
    ]
    if scale != 1:
        frames = [pygame.transform.scale_by(frame, scale) for frame in frames]
    return frames


class Animation:
    """Frames plus per-frame durations in ms. Shared by every entity that uses it."""

    def __init__(self, frames, durations, loop=True):
        if len(frames) != len(durations):
            raise ValueError("Each frame needs a duration")
        self.frames = frames
        self.durations = durations
        self.loop = loop

    @property
    def total_ms(self):
        return sum(self.durations)


class AnimationPlayer:
    """Per-entity playback state for an Animation."""

    def __init__(self, animation):
        self.animation = animation
        self.index = 0
        self.timer = 0
        self.finished = False

    def play(self, animation, restart=False):
        """Switch animation. Does nothing if it is already playing (unless restart=True)."""
        if animation is self.animation and not restart:
            return
        self.animation = animation
        self.index = 0
        self.timer = 0
        self.finished = False

    def update(self, dt_ms):
        anim = self.animation
        if self.finished:
            return
        self.timer += dt_ms
        while self.timer >= anim.durations[self.index]:
            self.timer -= anim.durations[self.index]
            if self.index + 1 < len(anim.frames):
                self.index += 1
            elif anim.loop:
                self.index = 0
            else:
                self.finished = True  # holds on the last frame
                self.timer = 0
                break

    @property
    def image(self):
        return self.animation.frames[self.index]
