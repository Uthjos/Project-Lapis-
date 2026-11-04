import pygame
from pathlib import Path

from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT

pygame.init()

#eventually make this a global enum so that every scene knows how many other scenes there are.
SCENE_MENU = 0
SCENE_GAME = 1
SCENE_SHOP = 2

def main_menu(screen):
    # Initialize game variables as the player, enemies and such.
    fps_cap = 30
    clock = pygame.time.Clock()

    UI_DIR = Path(__file__).resolve().parent / "assets" / "UI"

    title = pygame.image.load(str(UI_DIR / "Project Lapiz Tile.png"))
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    # Game loop.
    while True:

        # Time management.
        clock.tick(fps_cap)

        # Handle events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return SCENE_GAME

        screen.fill((40, 40, 40))
        screen.blit(title, title_rect)
        pygame.display.update()
