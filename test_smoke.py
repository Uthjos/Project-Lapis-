import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

def test_pygame_imports():
    assert pygame.version.ver

def test_pygame_init_and_display():
    pygame.init()
    screen = pygame.display.set_mode((100,100))
    assert screen.get_size() == (100,100)
    pygame.quit()

def test_surface_and_rect():
    surface = pygame.Surface((100,100))
    rect = pygame.Rect()
    assert rect.width == 100
    assert rect.height == 100