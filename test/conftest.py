import os
import sys
from pathlib import Path

# Must be set before pygame is imported anywhere so no real window/audio opens.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pygame
import pytest

SLIME_DIR = (
    PROJECT_ROOT / "src" / "assets" / "sprites" / "Crypt Slime" / "Sprite Sheets"
)


@pytest.fixture
def screen():
    """A headless 1280x720 display (needed for convert_alpha and image loading)."""
    pygame.init()
    surface = pygame.display.set_mode((1280, 720))
    pygame.event.clear()
    yield surface


@pytest.fixture
def slime_assets(screen):
    """Slime sprite sheets loaded once into the class."""
    from src.object_class.slime import Slime
    Slime.load_assets(SLIME_DIR)
    return Slime
