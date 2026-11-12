from dataclasses import dataclass, field
from enum import Enum

import pygame

from src.data_file_manage.directory_path import DirectoryPath as dp
from src.data_file_manage.exporter_factory import ExporterFactory
from src.data_file_manage.parser_factory import ParserFactory


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
    JUMP = "jump"


class SpriteDirection(Enum):
    N = "N"
    NE = "NE"
    E = "E"
    SE = "SE"
    S = "S"
    SW = "SW"
    W = "W"
    NW = "NW"




@dataclass
class PygameProp:
    """PygameProp contains the pygame transformation data that is associated with
    each sprite associated with the individual parts
    """
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
            "scale": tuple(self.scale),
            "rotation": self.rotation,
            "h_flip": self.h_flip,
            "v_flip": self.v_flip,
            "center": tuple(self.center),
        }

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            x=d.get("x", 0),
            y=d.get("y", 0),
            scale=tuple(d.get("scale", (1, 1))),
            rotation=d.get("rotation", 0),
            h_flip=d.get("h_flip", False),
            v_flip=d.get("v_flip", False),
            center=tuple(d.get("center", (0, 0))),
        )




@dataclass
class SpriteData(PygameProp):
    """the Individual sprites that are the different parts on the character"""
    part: AnimationPart = AnimationPart.HEAD
    file_location: str = ""
    props: PygameProp = field(default_factory=PygameProp)

    image = None
    if file_location != "":
        image = pygame.image.load(file_location)

    def to_dict(self):
        return {
            "part": self.part.value,
            "file_location": self.file_location,
            "properties": self.props.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            part=AnimationPart(d["part"]),
            file_location=d["file_location"],
            props=PygameProp.from_dict(d.get("properties", {})),
        )




@dataclass
class Frame(PygameProp):
    """The whole picture where everything comes together for a single frame"""
    # layer order is based on where the sprite is on the sprite list
    sprites: list[SpriteData] = field(default_factory=list)
    time_to_next_frame: int = 100

    def to_dict(self):
        return {
            "time_to_next_frame": self.time_to_next_frame,
            "sprites": [s.to_dict() for s in self.sprites],
        }

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            sprites=[SpriteData.from_dict(s) for s in d.get("sprites", [])],
            time_to_next_frame=d.get("time_to_next_frame", 100),
        )




@dataclass
class AnimationStack:
    """contains every possible action that a NPC or Character should be able to do"""
    # Every direction contains a dict of actions and actions contains list of frames
    animations: dict = field(
        default_factory=lambda: {
            direction: {action: [] for action in Action}
            for direction in SpriteDirection
        }
    )

    def add_frame(self, frame: Frame, action: Action, direction: SpriteDirection):
        self.animations[direction][action].append(frame)

    def to_dict(self):
        return {
            direction.value: {
                action.value: [frame.to_dict() for frame in frames]
                for action, frames in actions.items()
            }
            for direction, actions in self.animations.items()
        }

    @classmethod
    def from_dict(cls, data: dict):
        stack = cls()
        for direction in SpriteDirection:
            for action in Action:
                raw = data.get(direction.value, {}).get(action.value, [])
                stack.animations[direction][action] = [Frame.from_dict(f) for f in raw]
        return stack

    def load_animations(self, filename: str):
        data = ParserFactory.create_parser("json").parse_file(filename)
        self.animations = AnimationStack.from_dict(data).animations

    def export_to_json(self, name: str):
        path = dp.get_dir(dp.ANIMATION) / f"{name}.json"
        ExporterFactory.get_exporter("json").export(data=self.to_dict(), filename=path)
