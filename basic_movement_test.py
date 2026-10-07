import pygame

from src.object_class.Character import Character


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
FPS = 60


def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Project Lapis")
    clock = pygame.time.Clock()

    # loads the player sprite
    player_image = pygame.image.load(
        "src/assets/sprites/Sprite style 1.png"
    ).convert_alpha()

    player = Character(380, 280)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # checks which movement keys are being pressed
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            player.move(0, -PLAYER_SPEED)

        if keys[pygame.K_s]:
            player.move(0, PLAYER_SPEED)

        if keys[pygame.K_a]:
            player.move(-PLAYER_SPEED, 0)

        if keys[pygame.K_d]:
            player.move(PLAYER_SPEED, 0)

        screen.fill("black")

        # draws the player sprite at the character's current position
        screen.blit(player_image, (player.x, player.y))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
