import random

import pygame


class Square(pygame.sprite.Sprite):
    def __init__(self, col, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50, 50))
        self.image.fill(col)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        #make squares fall
        self.rect.move_ip(0, 5)

        #check if sprite has gone off-screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

#define screen size
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

#create game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Square")

#frame rate
clock = pygame.time.Clock()
FPS = 60

#create sprite group for squares
squares = pygame.sprite.Group()

#create sprite group for squares
square = Square("crimson", 500, 300)
squares.add(square)

if __name__ == "__main__":
    run = True
    while run:
        clock.tick(FPS)

        #update background
        screen.fill("yellow")

        #update sprite group
        squares.update()

        #draw sprite group
        squares.draw(screen)

        print(squares)

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                #get mouse coordinates
                pos = pygame.mouse.get_pos()
                #create square
                square = Square("crimson", pos[0], pos[1])
                squares.add(square)

            #quit program
            if event.type == pygame.QUIT:
                run = False

        #update display
        pygame.display.flip()

    pygame.quit()