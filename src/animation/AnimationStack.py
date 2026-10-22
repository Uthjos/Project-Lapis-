from enum import Enum

from src.animation import SpriteDirection
from src.data_file_manage import ExporterFactory


class AnimationPart(Enum):
    BACK_ARM = "backarm"
    BACK_LEG = "backleg"
    HIP = "hip"
    TORSO = "torso"
    FRONT_LEG = "frontleg"
    HEAD = "head"
    FRONT_ARM = "frontarm"
    FRONT_CLOAK = "frontcloak"
    BACK_CLOAK = "backcloak"
    FRONT_TASSET = "fronttaskset"
    BACK_TASSET = "backtaskset"
    FRONT_PAULDRON = "frontpauldron"
    BACK_PAULDRON = "backpauldron"

class PygameProp(Enum):
    position = "position"
    rotation = "rotation"
    scale = "scale"

class Action(Enum):
    WALK = "walk"
    RUN = "run"
    ATTACK = "attack"
    BLOCK = "block"
    CAST = "cast"
    IDLE = "idle"
    INJURED = "injured"
    BOW_ATTACK = "bowattack"
    CROSS_BOW_ATTACK = "crossbowattack"
    STUNNED = "stunned"



class Animation:
    def __init__(self, direction: str, action: str, animation_time: int , file_location: list[str],
                 ):
        self.file_location = file_location
        self.direction = direction
        self.action = action
        self.animation_time = animation_time
        self.pygame_properties = {
            PygameProp.position.value: list(0,0),
            PygameProp.rotation.value: 0,
            PygameProp.scale.value: 1,
        }
        self.body_part_animation_list = list

    def getFrame(self, frame_number):
        return self.body_part_animation_list[frame_number]

    def setAnimationList(self, animationList):
        self.body_part_animation_list = animationList

    def to_dict(self):
        return {
            "direction": self.direction,
            "part": self.part,
            "action": self.action,
            "animation_time": self.animation_time,
            "file_location": self.file_location,
            #needs more here still organizing
        }


class AnimationStack:
    def __init__(self):

        # will be a directory for all the possible animations
        # direction will contain actions that will be called knowing the direction state
        # actions be chosen from player input or lack of input
        # the part will contain the animation associated with the part
        self.animationList = {}

        #create the Dictionary paths
        for direction in SpriteDirection:
            self.animationList[direction.direction] = {}

            for action in Action:
                self.animationList[direction.direction][action.value] = {}

                for part in AnimationPart:
                    self.animationList[direction.direction][action.value][part] = Animation

    def addAnimation(self, direction, animation):
        pass

    def to_dict(self):
        return {
           direction: {
               part: animatiob.to_dict() for part, animatiob in self.animationList.items()
           }
            for direction, parts in self.animationList.items()

        }

    def export(self, filePath):
        ExporterFactory.createExporter(filePath)

    def load(self, data_file):
        pass # will create the Animation stack from JSON file





