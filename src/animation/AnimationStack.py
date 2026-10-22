from enum import Enum

import pygame

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
    THROW_ONE_HANDED = "throwonehanded"
    THROW_TWO_HANDED = "throwtwohanded"

# priority is associated with direction lower number means that they will be put first
# meaning that they will be in the back of the sprite layer

# for the North direction and South direction
# front will be right part on screen and
# back will be left part on screen
class SpriteDirection(Enum):

    N = ("N", {
        AnimationPart.FRONT_LEG: 1,
        AnimationPart.BACK_LEG: 2,
        AnimationPart.HIP: 3,
        AnimationPart.FRONT_TASSET: 4,
        AnimationPart.BACK_TASSET: 5,
        AnimationPart.TORSO: 6,
        AnimationPart.FRONT_ARM: 7,
        AnimationPart.BACK_ARM: 8,
        AnimationPart.FRONT_PAULDRON: 9,
        AnimationPart.BACK_PAULDRON: 10,
        AnimationPart.HEAD: 11,
        AnimationPart.FRONT_CLOAK: 12,
        AnimationPart.BACK_CLOAK: 13,
    })
    NE = ("NE", {
        AnimationPart.BACK_PAULDRON: 1,
        AnimationPart.BACK_CLOAK: 2,
        AnimationPart.BACK_ARM: 3,
        AnimationPart.BACK_TASSET: 4,
        AnimationPart.BACK_LEG: 5,
        AnimationPart.HIP: 6,
        AnimationPart.FRONT_LEG: 7,
        AnimationPart.TORSO: 8,
        AnimationPart.FRONT_TASSET: 9,
        AnimationPart.FRONT_ARM: 10,
        AnimationPart.HEAD: 11,
        AnimationPart.FRONT_PAULDRON: 12,
        AnimationPart.FRONT_CLOAK: 13,
    })
    E = ("E", {
        AnimationPart.BACK_PAULDRON: 1,
        AnimationPart.BACK_CLOAK: 2,
        AnimationPart.BACK_ARM: 3,
        AnimationPart.BACK_TASSET: 4,
        AnimationPart.BACK_LEG: 5,
        AnimationPart.HIP: 6,
        AnimationPart.FRONT_LEG: 7,
        AnimationPart.TORSO: 8,
        AnimationPart.FRONT_TASSET: 9,
        AnimationPart.HEAD: 10,
        AnimationPart.FRONT_ARM: 11,
        AnimationPart.FRONT_PAULDRON: 12,
        AnimationPart.FRONT_CLOAK: 13,
    })
    SE = ("SE", {
        AnimationPart.BACK_CLOAK: 1,
        AnimationPart.BACK_PAULDRON: 2,
        AnimationPart.BACK_ARM: 3,
        AnimationPart.BACK_LEG: 4,
        AnimationPart.BACK_TASSET: 5,
        AnimationPart.HIP: 6,
        AnimationPart.FRONT_LEG: 7,
        AnimationPart.TORSO: 8,
        AnimationPart.FRONT_TASSET: 9,
        AnimationPart.FRONT_ARM: 10,
        AnimationPart.FRONT_PAULDRON: 11,
        AnimationPart.HEAD: 12,
        AnimationPart.FRONT_CLOAK: 13,
    })
    S = ("S", {
        AnimationPart.FRONT_CLOAK: 1,
        AnimationPart.BACK_CLOAK: 2,
        AnimationPart.FRONT_LEG: 3,
        AnimationPart.BACK_LEG: 4,
        AnimationPart.HIP: 5,
        AnimationPart.FRONT_TASSET: 6,
        AnimationPart.BACK_TASSET: 7,
        AnimationPart.TORSO: 8,
        AnimationPart.FRONT_ARM: 9,
        AnimationPart.BACK_ARM: 10,
        AnimationPart.FRONT_PAULDRON: 11,
        AnimationPart.BACK_PAULDRON: 12,
        AnimationPart.HEAD: 13,
    })
    SW = ("SW", {
        AnimationPart.BACK_CLOAK: 1,
        AnimationPart.BACK_PAULDRON: 2,
        AnimationPart.BACK_ARM: 3,
        AnimationPart.BACK_LEG: 4,
        AnimationPart.BACK_TASSET: 5,
        AnimationPart.HIP: 6,
        AnimationPart.FRONT_LEG: 7,
        AnimationPart.TORSO: 8,
        AnimationPart.FRONT_TASSET: 9,
        AnimationPart.FRONT_ARM: 10,
        AnimationPart.FRONT_PAULDRON: 11,
        AnimationPart.HEAD: 12,
        AnimationPart.FRONT_CLOAK: 13,
    })
    W = ("W", {
        AnimationPart.BACK_PAULDRON: 1,
        AnimationPart.BACK_CLOAK: 2,
        AnimationPart.BACK_ARM: 3,
        AnimationPart.BACK_TASSET: 4,
        AnimationPart.BACK_LEG: 5,
        AnimationPart.HIP: 6,
        AnimationPart.FRONT_LEG: 7,
        AnimationPart.TORSO: 8,
        AnimationPart.FRONT_TASSET: 9,
        AnimationPart.HEAD: 10,
        AnimationPart.FRONT_ARM: 11,
        AnimationPart.FRONT_PAULDRON: 12,
        AnimationPart.FRONT_CLOAK: 13,
    })
    NW = ("NW", {
        AnimationPart.BACK_PAULDRON: 1,
        AnimationPart.BACK_CLOAK: 2,
        AnimationPart.BACK_ARM: 3,
        AnimationPart.BACK_TASSET: 4,
        AnimationPart.BACK_LEG: 5,
        AnimationPart.HIP: 6,
        AnimationPart.FRONT_LEG: 7,
        AnimationPart.TORSO: 8,
        AnimationPart.FRONT_TASSET: 9,
        AnimationPart.FRONT_ARM: 10,
        AnimationPart.HEAD: 11,
        AnimationPart.FRONT_PAULDRON: 12,
        AnimationPart.FRONT_CLOAK: 13,
    })

    def __init__(self, direction, layer_priority):
        self.direction = direction
        self.layer_priority = layer_priority

class Animation:
    def __init__(self, direction: str, action: str, animation_time: int , file_location: list[str],
                 max_frames: int, pygame_prop: list[dict]):
        self.direction = direction
        self.action = action
        self.animation_time = animation_time # speed can maybe change need to look into it
        self.max_frames = max_frames

        # file location only holds the file locations
        self.file_location = file_location
        self.pygame_prop = pygame_prop

        # using this to call the frames and associate with pygame
        animation_list = []
        for file in file_location:
            part_image = pygame.image.load(file).convert_alpha()
            animation_list.append(part_image)


        self.body_part_animation_list = list

    def getFrame(self, frame_number):
        return self.body_part_animation_list[frame_number]

    def setAnimationList(self, animationList):
        self.body_part_animation_list = animationList

    def update_animation(self):
        pass

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





