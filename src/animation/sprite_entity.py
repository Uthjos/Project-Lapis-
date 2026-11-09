from abc import ABC, abstractmethod

from src.animation.animation_stack import AnimationStack


class SpriteEntity(ABC):
    def __init__(self):
        self.animation_stack = AnimationStack()

    @abstractmethod
    def parse_file(self, file_path):
        pass
