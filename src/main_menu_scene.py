from pathlib import Path

import pygame

from src.scene_base import BaseScene
from src.scenes import Scene
from src.settings import SCREEN_HEIGHT, SCREEN_WIDTH

FADE_IN_MS = 2000
# eventually make this a global enum so that every scene knows how many other scenes there are.

UI_DIR = Path(__file__).resolve().parent / "assets" / "UI"


class MainMenuScene(BaseScene):
    """Title screen: the subtitle fades in, Enter starts the game."""

    FPS = 30

    def __init__(self, screen):
        super().__init__(screen)
        self.title = pygame.image.load(str(UI_DIR / "Project Lapiz Tile.png"))
        self.title_rect = self.title.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        )
        self.subtitle = pygame.image.load(str(UI_DIR / "Lapis_Subtitle.png"))
        self.subtitle_rect = self.subtitle.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5)
        )
        self.fade_start = pygame.time.get_ticks() + 1000

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            now = pygame.time.get_ticks()
            if now - self.fade_start >= FADE_IN_MS:
                return Scene.GAME
            self.fade_start = now - FADE_IN_MS  # first Enter skips the fade
        return None

    def update(self, dt):
        return None

    def draw(self):
        now = pygame.time.get_ticks()
        progress = min((now - self.fade_start) / FADE_IN_MS, 1.0)
        self.subtitle.set_alpha(int(progress * 255))
        self.screen.fill((40, 40, 40))
        self.screen.blit(self.title, self.title_rect)
        self.screen.blit(self.subtitle, self.subtitle_rect)


def main_menu(screen):
    """Scene entry point used by main.py."""
    return MainMenuScene(screen).run()
