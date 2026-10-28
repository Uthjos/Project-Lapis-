import AnimationMenuView
import AnimationMenuVM
import pygame
from pygame.sprite import Sprite


def main():
    pygame.init()

    #Create the window
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Animation Editor")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 20)

    sprite = Sprite()
    editor_vm = AnimationMenuVM(sprite)

    menu_vm = AnimationMenuVM(AnimationMenuView, editor_vm)
    menu_view = AnimationMenuView(menu_vm, font, screen.get_width())

    views = []

    running = True
    while running:
        dt = clock.tick(60) / 1000

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif menu_view.handle_event(e):
                continue  # menu consumed it; canvas must not start a stroke
            else:
                for v in views:
                    v.handle_event(e)

        if menu_vm.quit_requested:
            running = False

        editor_vm.tick(dt)

        screen.fill((30, 30, 36))
        for v in views:
            v.draw(screen)
        menu_view.draw(screen)  # last, so dropdowns overlay everything
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()