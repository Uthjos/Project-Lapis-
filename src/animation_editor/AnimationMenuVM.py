import pathlib
import pygame

from src.animation.AnimationStack import *


class AnimationMenuVM:
    def __init__(self, ani_stack: AnimationStack, ):
        self.ani_stack = ani_stack


    @staticmethod
    def get_image(filename: str):
        # no need to convert since it is going to be passed through to CustomTkinter
        image = pygame.image.load(str(filename))
        return image