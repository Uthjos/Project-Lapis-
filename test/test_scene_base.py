import pygame
import pytest

from src.scene_base import BaseScene
from src.scenes import Scene


class FakeClock:
    """Stands in for pygame.time.Clock so frames take no real time."""

    def __init__(self, dt=16):
        self.dt = dt
        self.fps_seen = []

    def tick(self, fps):
        self.fps_seen.append(fps)
        return self.dt


class RecordingScene(BaseScene):
    """Logs every hook call so tests can check the order the loop uses."""

    FPS = 30

    def __init__(self, screen, event_results=(), update_results=()):
        super().__init__(screen)
        self.clock = FakeClock()
        self.log = []
        self.event_results = iter(event_results)
        self.update_results = iter(update_results)

    def begin_frame(self, dt):
        self.log.append(("begin", dt))

    def handle_event(self, event):
        self.log.append("event")
        return next(self.event_results, None)

    def update(self, dt):
        self.log.append(("update", dt))
        return next(self.update_results, None)

    def draw(self):
        self.log.append("draw")


def event():
    return pygame.event.Event(pygame.USEREVENT)


def feed_frames(monkeypatch, frames):
    """pygame.event.get() returns one list per frame; running past the end fails fast."""
    frames = iter(frames)
    monkeypatch.setattr(pygame.event, "get", lambda: next(frames))


def count_flips(monkeypatch):
    flips = {"n": 0}
    monkeypatch.setattr(
        pygame.display, "flip", lambda: flips.__setitem__("n", flips["n"] + 1)
    )
    return flips


def test_base_scene_cannot_be_instantiated(screen):
    with pytest.raises(TypeError):
        BaseScene(screen)


def test_scene_missing_a_hook_cannot_be_instantiated(screen):
    class HalfScene(BaseScene):
        def handle_event(self, event):
            return None

        def update(self, dt):
            return None

    with pytest.raises(TypeError):
        HalfScene(screen)


def test_default_fps_and_screen(screen):
    class MinimalScene(BaseScene):
        def handle_event(self, event):
            return None

        def update(self, dt):
            return None

        def draw(self):
            pass

    scene = MinimalScene(screen)

    assert BaseScene.FPS == 60
    assert scene.screen is screen


def test_frame_runs_begin_events_update_draw_in_order(screen, monkeypatch):
    flips = count_flips(monkeypatch)
    feed_frames(monkeypatch, [[event(), event()], []])
    scene = RecordingScene(screen, update_results=[None, Scene.GAME])

    assert scene.run() == Scene.GAME

    assert scene.log == [
        ("begin", 16),
        "event",
        "event",
        ("update", 16),
        "draw",
        ("begin", 16),
        ("update", 16),
    ]
    # Frame 1 was drawn and flipped; frame 2 ended in update before drawing.
    assert flips["n"] == 1


def test_scene_returned_from_handle_event_stops_the_frame(screen, monkeypatch):
    flips = count_flips(monkeypatch)
    feed_frames(monkeypatch, [[event(), event()]])
    scene = RecordingScene(screen, event_results=[Scene.QUIT])

    assert scene.run() == Scene.QUIT

    # The second event is never handled, and the frame is never updated or drawn.
    assert scene.log == [("begin", 16), "event"]
    assert flips["n"] == 0


def test_run_ticks_clock_at_scene_fps_and_passes_dt(screen, monkeypatch):
    count_flips(monkeypatch)
    feed_frames(monkeypatch, [[], []])
    scene = RecordingScene(screen, update_results=[None, Scene.MENU])
    scene.clock.dt = 33

    scene.run()

    assert scene.clock.fps_seen == [30, 30]
    assert ("update", 33) in scene.log
    assert ("begin", 33) in scene.log


def test_begin_frame_is_optional(screen, monkeypatch):
    class NoBeginScene(BaseScene):
        def handle_event(self, event):
            return None

        def update(self, dt):
            return Scene.GAME

        def draw(self):
            pass

    count_flips(monkeypatch)
    feed_frames(monkeypatch, [[]])

    assert NoBeginScene(screen).run() == Scene.GAME
