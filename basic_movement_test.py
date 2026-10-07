from typing import dataclass_transform

import pygame

from src.object_class.Character import Character

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
FPS = 60

ATTCK_DURATION = 200

def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Project Lapis")
    clock = pygame.time.Clock()

    # loads the player sprite
    player_image = pygame.image.load(
        "src/assets/sprites/Sprite style 2.png"
    ).convert_alpha()

    # loads slash effect
    slash_image = pygame.image.load(
        "src/assets/actions/test_slash_reference.png"
    )

    player = Character(380, 280)

    attacking = False
    attack_timer = 0

    running = True
    while running:
        # Get teh time since the last frame
        dt = clock.tick(FPS)

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

        if keys[pygame.K_SPACE]:
            attacking = True
            attack_timer = ATTCK_DURATION

        if attacking:
            attack_timer -= dt



            if attack_timer <= 0:
                attacking = False

        screen.fill("black")

        if attacking:
            slash_rect = slash_image.get_rect()

            #Put slash to right of player
            slash_rect.midleft = (
                player.x + player_image.get_width() / 2,
                player.y + player_image.get_height() // 2
            )
            screen.blit(slash_image, slash_rect)

        # draws the player sprite at the character's current position
        screen.blit(player_image, (player.x, player.y))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
