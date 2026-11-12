"""Shared interface that every game scene implements.

A scene owns its own state and only has to fill in three hooks:

    handle_event(event) -> Scene | None   react to one pygame event
    update(dt)          -> Scene | None   advance the simulation one frame
    draw()              -> None           render to self.screen

Returning a Scene from handle_event or update ends the scene and tells
main.py which scene to run next. run() owns the frame loop, so individual
scenes no longer write their own while-True loop.
"""

from abc import ABC, abstractmethod

import pygame

from src.scenes import Scene


class BaseScene(ABC):
    """Base class for menu, game and any future scene."""

    FPS = 60

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

    # ---------- hooks a scene implements
    @abstractmethod
    def handle_event(self, event) -> Scene | None:
        """Handle one pygame event. Return a Scene to switch to it, else None."""

    @abstractmethod
    def update(self, dt) -> Scene | None:
        """Advance one frame (dt in ms). Return a Scene to switch to it, else None."""

    @abstractmethod
    def draw(self) -> None:
        """Draw the current frame onto self.screen (no display flip needed)."""

    def begin_frame(self, dt) -> None:
        """Optional hook that runs before events each frame (timers, bookkeeping)."""

    # ---------- shared loop
    def run(self) -> Scene:
        """Run the scene until it asks for another one, and return that Scene."""
        while True:
            dt = self.clock.tick(self.FPS)
            self.begin_frame(dt)

            for event in pygame.event.get():
                next_scene = self.handle_event(event)
                if next_scene is not None:
                    return next_scene

            next_scene = self.update(dt)
            if next_scene is not None:
                return next_scene

            self.draw()
            pygame.display.flip()