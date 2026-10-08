import pygame

from src.object_class.Character import Character

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
FPS = 60

ATTACK_DURATION = 200

def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Project Lapis")
    clock = pygame.time.Clock()

    # loads the player sprite
    player_image = pygame.image.load(
        "src/assets/sprites/Sprite style 2.png"
    ).convert_alpha()

    torso_image = pygame.image.load(
        "src/assets/sprites/torso_test.png"
    ).convert_alpha()

    # load legs for animation
    leg_images = [
        pygame.image.load("src/assets/sprites/player_sprite_leg_run_reference_0001.png").convert_alpha(),
        pygame.image.load("src/assets/sprites/player_sprite_leg_run_reference_0002.png").convert_alpha(),
        pygame.image.load("src/assets/sprites/player_sprite_leg_run_reference_0003.png").convert_alpha(),
        pygame.image.load("src/assets/sprites/player_sprite_leg_run_reference_0004.png").convert_alpha(),
        pygame.image.load("src/assets/sprites/player_sprite_leg_run_reference_0005.png").convert_alpha()
    ]

    # loads slash effect
    slash_image = pygame.image.load(
        "src/assets/actions/test_slash_reference.png"
    ).convert_alpha()



    player = Character(380, 280)

    #making sure they are facing the right direction
    facing_right = True

    # initialize attack
    attacking = False
    attack_timer = 0

    # leg animation timing
    leg_frame = 0
    leg_timer = 0
    ANIMATION_SPEED = 50
    moving = False

    running = True
    while running:
        # Get teh time since the last frame
        dt = clock.tick(FPS)
        current_image = player_image

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


        # checks which movement keys are being pressed
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            player.move(0, -PLAYER_SPEED)
            moving = True

        if keys[pygame.K_s]:
            player.move(0, PLAYER_SPEED)
            moving = True

        if keys[pygame.K_a]:
            player.move(-PLAYER_SPEED, 0)
            moving = True
            facing_right = False

        if keys[pygame.K_d]:
            player.move(PLAYER_SPEED, 0)
            moving = True
            facing_right = True

        if keys[pygame.K_SPACE]:
            attacking = True
            attack_timer = ATTACK_DURATION

        if keys[pygame.K_r]:
            rotating = True

        if facing_right:
            current_image = player_image
        else:
            current_image = pygame.transform.flip(player_image, True, False)

        if attacking:
            attack_timer -= dt
            if attack_timer <= 0:
                attacking = False

        screen.fill("black")

        if moving:
            leg_timer += dt
            if leg_timer >= ANIMATION_SPEED:
                leg_timer = 0
                leg_frame += 1

                if leg_frame >= len(leg_images):
                    leg_frame = 0
            if facing_right:
                screen.blit(torso_image, (player.x, player.y))
                screen.blit(leg_images[leg_frame % len(leg_images)], (player.x, player.y))
            else:
                screen.blit(pygame.transform.flip(torso_image, True, False),
                            (player.x, player.y))
                screen.blit(pygame.transform.flip(leg_images[leg_frame % len(leg_images)], True, False),
                            (player.x, player.y))

        if not moving:
            # draws the player sprite at the character's current position
            screen.blit(current_image, (player.x, player.y))

        if attacking:
            slash_rect = slash_image.get_rect()
            if facing_right:
                # Put slash to right of player
                slash_rect.midleft = (
                    player.x + player_image.get_width() / 2,
                    player.y + player_image.get_height() // 2
                )
                screen.blit(slash_image, slash_rect)
            else:
                # Put slash to left of player
                slash_rect.midright = (
                    player.x + player_image.get_width() / 2,
                    player.y + player_image.get_height() / 2
                )
                screen.blit(pygame.transform.flip(slash_image, True, False),
                            slash_rect)

        # to when key is no longer pressed will flip to not moving
        moving = False

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
