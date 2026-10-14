from abc import ABC, abstractmethod

import AnimationStack


class StpriteEntity(ABC):

    @abstractmethod
    def parse_file(self, file_path):
        pass

    @abstractmethod
    def __init__(self):
        self.animationStack = AnimationStack.AnimationStack()

