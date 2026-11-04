import pygame
import pytest

from src.main_menu_scene import main_menu
from src.scenes import Scene


def feed_events(monkeypatch, frames):
    """Make pygame.event.get() return one list of events per call, then QUIT forever."""
    frames = iter(frames)

    def fake_get():
        return next(frames, [pygame.event.Event(pygame.QUIT)])

    monkeypatch.setattr(pygame.event, "get", fake_get)


def enter():
    return pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)


def test_quit_event_exits(screen, monkeypatch):
    feed_events(monkeypatch, [[pygame.event.Event(pygame.QUIT)]])

    with pytest.raises(SystemExit):
        main_menu(screen)


def test_enter_skips_fade_then_starts_game(screen, monkeypatch):
    # First Enter finishes the fade-in, second Enter (next frame) starts the game.
    feed_events(monkeypatch, [[enter()], [enter()]])

    assert main_menu(screen) == Scene.GAME


def test_menu_draws_background(screen, monkeypatch):
    # main_menu calls pygame.quit() on exit, which would kill the display
    # before we can inspect it, so make quit a no-op for this test.
    monkeypatch.setattr(pygame, "quit", lambda: None)
    feed_events(monkeypatch, [[], [pygame.event.Event(pygame.QUIT)]])

    with pytest.raises(SystemExit):
        main_menu(screen)

    assert tuple(screen.get_at((0, 0)))[:3] == (40, 40, 40)
