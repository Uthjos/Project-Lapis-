import json
from enum import Enum


class AnimationName(Enum):
    BACK_ARM = "backarm"
    BACK_LEG = "backleg"
    HIP = "hip"
    LEFT_ARM="leftarm"
    TORSO = "torso"
    HEAD = "head"
    FRONT_ARM = "frontarm"
    CLOAK = "cloak"

class Animation:
    def __init__(self, animationList):
        self.bodyPartAnimationList = animationList
        self.currentFrame = 0


    def update(self):
        self.currentFrame = (self.currentFrame + 1) % len(self.bodyPartAnimationList)

        if self.currentFrame >= len(self.bodyPartAnimationList):
            self.currentFrame = 0

    def getFrame(self):
        return self.bodyPartAnimationList[self.currentFrame]

    def load(self, fileName):
        self.bodyPartAnimationList = []
        with open(fileName) as json_file:
            data = json.load(json_file)

        for bodyPart in data:
            self.bodyPartAnimationList.append(Animation(bodyPart))


