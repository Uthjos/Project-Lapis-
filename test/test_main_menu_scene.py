import pygame
import pytest

from src.main_menu_scene import FADE_IN_MS, MainMenuScene, main_menu
from src.scene_base import BaseScene
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


# ---------- MainMenuScene ----------
@pytest.fixture
def menu(screen):
    return MainMenuScene(screen)


def fix_time(monkeypatch, ticks=5000):
    monkeypatch.setattr(pygame.time, "get_ticks", lambda: ticks)


def test_menu_scene_is_a_30_fps_base_scene(menu):
    assert isinstance(menu, BaseScene)
    assert menu.FPS == 30


def test_update_is_a_no_op(menu):
    assert menu.update(16) is None


def test_enter_during_fade_skips_the_fade_instead_of_starting(menu, monkeypatch):
    fix_time(monkeypatch)
    menu.fade_start = 5000  # fade has just begun

    assert menu.handle_event(enter()) is None
    assert menu.fade_start == 5000 - FADE_IN_MS


def test_enter_after_fade_starts_game(menu, monkeypatch):
    fix_time(monkeypatch)
    menu.fade_start = 5000 - FADE_IN_MS

    assert menu.handle_event(enter()) == Scene.GAME


def test_other_keys_are_ignored(menu, monkeypatch):
    fix_time(monkeypatch)
    menu.fade_start = 4000

    result = menu.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))

    assert result is None
    assert menu.fade_start == 4000


def test_window_close_quits_the_program(menu, monkeypatch):
    monkeypatch.setattr(pygame, "quit", lambda: None)

    with pytest.raises(SystemExit):
        menu.handle_event(pygame.event.Event(pygame.QUIT))


def test_draw_fades_subtitle_in(menu, monkeypatch):
    fix_time(monkeypatch, 5000)

    menu.fade_start = 4000  # halfway through the fade
    menu.draw()
    assert menu.subtitle.get_alpha() == 127

    menu.fade_start = 0  # long finished
    menu.draw()
    assert menu.subtitle.get_alpha() == 255


def test_draw_fills_background(menu, screen):
    screen.fill((255, 0, 255))

    menu.draw()

    assert tuple(screen.get_at((0, 0)))[:3] == (40, 40, 40)
