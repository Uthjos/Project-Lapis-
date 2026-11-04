from pathlib import Path

import pygame

from src.scenes import Scene
from src.settings import SCREEN_HEIGHT, SCREEN_WIDTH

pygame.init()
FADE_IN_MS = 2000
#eventually make this a global enum so that every scene knows how many other scenes there are.

def main_menu(screen):
    # Initialize game variables as the player, enemies and such.
    fps_cap = 30
    clock = pygame.time.Clock()

    UI_DIR = Path(__file__).resolve().parent / "assets" / "UI"

    title = pygame.image.load(str(UI_DIR / "Project Lapiz Tile.png"))
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    subtitle = pygame.image.load(str(UI_DIR / "Lapis_Subtitle.png"))
    subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5))

    fade_start = pygame.time.get_ticks() + 1000
    # Game loop.
    while True:

        # Time management.
        clock.tick(fps_cap)
        now = pygame.time.get_ticks()
        fade_done = now - fade_start >= FADE_IN_MS

        # Handle events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if fade_done:
                    return Scene.GAME
                fade_start = now - FADE_IN_MS

        progress = min((now - fade_start) / FADE_IN_MS, 1.0) #title fading

        subtitle.set_alpha(int(progress * 255))
        screen.fill((40, 40, 40))
        screen.blit(title, title_rect)
        screen.blit(subtitle, subtitle_rect)
        pygame.display.update()
