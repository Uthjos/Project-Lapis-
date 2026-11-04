import pygame

pygame.init()

#eventually make this a global enum so that every scene knows how many other scenes there are.
SCENE_MENU = 0
SCENE_GAME = 1
SCENE_SHOP = 2

def main_menu(screen):
    # Initialize game variables as the player, enemies and such.
    fps_cap = 30
    clock = pygame.time.Clock()

    # Game loop.
    while True:

        # Time management.
        clock.tick(fps_cap)

        # Handle events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                return SCENE_GAME

        screen.fill((0, 0, 255))
        pygame.display.update()
