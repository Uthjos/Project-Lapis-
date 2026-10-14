from enum import Enum

from src.data_file_manage import ParserFactory


class AnimationPart(Enum):
    BACK_ARM = "backarm"
    BACK_LEG = "backleg"
    HIP = "hip"
    LEFT_ARM="leftarm"
    TORSO = "torso"
    HEAD = "head"
    FRONT_ARM = "frontarm"
    CLOAK = "cloak"

class SpriteDirection(Enum):
    North = "N"
    NorthEast = "NE"
    East = "E"
    SouthEast = "SE"
    South = "S"
    SouthWest = "SW"
    West = "W"
    NorthWest = "NW"

class Animation:
    def __init__(self):
        self.bodyPartAnimationList = {}

    def getFrame(self, frame_number):
        return self.bodyPartAnimationList[frame_number]

    def setAnimationList(self, animationList):
        self.bodyPartAnimationList = animationList

    def load(self, fileName):
        ParserFactory.createParser(ParserFactory.get_file_format(fileName))(fileName)




class AnimationStack:
    def __init__(self):
        # will be a dictionary of directions S, SW, SE, N etc.
        # S will have dictionary of bodypart "backleg" for example
        # within that will the Animation class
        self.animationList = dict
        for direction in SpriteDirection:
            self.animationList[direction.value] = {}
            for part in AnimationPart:
                self.animationList[direction.value][part.value] = Animation(part, {})

    def load(self, fileName):
        pass
