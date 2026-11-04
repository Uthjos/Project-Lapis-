import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pygame

from src.game_scene import main_game
from src.main_menu_scene import main_menu
from src.scenes import Scene
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from src.main_menu_scene import main_menu

SCENES = {
    Scene.MENU: main_menu,
    Scene.GAME: main_game,
}


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Project Lapis")

    scene = Scene.MENU
    while scene != Scene.QUIT:
        scene = SCENES[scene](screen)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()