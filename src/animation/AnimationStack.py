from dataclasses import dataclass, field
from enum import Enum


class AnimationPart(Enum):
    BACK_ARM = "back_arm"
    BACK_LEG = "back_leg"
    HIP = "hip"
    TORSO = "torso"
    FRONT_LEG = "front_leg"
    HEAD = "head"
    FRONT_ARM = "front_arm"
    FRONT_CLOAK = "front_cloak"
    BACK_CLOAK = "back_cloak"
    FRONT_TASSET = "front_taskset"
    BACK_TASSET = "back_taskset"
    FRONT_PAULDRON = "front_pauldron"
    BACK_PAULDRON = "back_pauldron"


class Action(Enum):
    WALK = "walk"
    RUN = "run"
    ATTACK = "attack"
    BLOCK = "block"
    CAST = "cast"
    IDLE = "idle"
    INJURED = "injured"
    BOW_ATTACK = "bow_attack"
    CROSS_BOW_ATTACK = "crossbow_attack"
    STUNNED = "stunned"
    THROW_ONE_HANDED = "throw_one_handed"
    THROW_TWO_HANDED = "throw_two_handed"


class SpriteDirection(Enum):
    N = "N"
    NE = "NE"
    E = "E"
    SE = "SE"
    S = "S"
    SW = "SW"
    W = "W"
    NW = "NW"

"""PygameProp contains the pygame transformation data that is associated with
each sprite associated with the individual parts"""
@dataclass
class PygameProp:
    x: float = 0
    y: float = 0
    scale: tuple = (1.0, 1.0)
    rotation: float = 0
    h_flip: bool = False
    v_flip: bool = False
    center: tuple = (0, 0)

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "scale": list(self.scale),
            "rotation": self.rotation,
            "h_flip": self.h_flip,
            "v_flip": self.v_flip,
            "center": list(self.center),
        }

"""the Individual sprites that are the different parts on the character"""
@dataclass
class SpriteData(PygameProp):
    part: AnimationPart = AnimationPart.HEAD
    file_location: str = ""

    def to_dict(self):
        return {
            "part": self.part,
            "file_location": self.file_location,
            "properties": super().to_dict()
        }

"""The whole picture where everything comes together for a single frame"""
@dataclass
class Frame(PygameProp):
    frame_number: int = 0
    # layer order is based on where the sprite is on the sprite list
    sprites: list[SpriteData] = field(default_factory=list)
    time_to_next_frame: int = 100

    def to_dict(self):
        return {
            "frame_number": self.frame_number,
            "time_to_next_frame": self.time_to_next_frame,
            "sprites": [
                sprite.to_dict() for sprite in self.sprites
            ],
        }

"""contains every possible action that a NPC or Character should be able to do"""
@dataclass
class AnimationStack:
    animations: dict = field(
        default_factory=lambda: {
            action: [] for action in Action
        }
    )

    def add_frame(self, frame: Frame, action: Action):
        self.animations[action].append(frame)

    def to_dict(self):
        # look for frames in ever action item in the list
        return {
            action.value: [
                frame.to_dict() for frame in frames
            ]
            for action, frames in self.animations.items()
        }
