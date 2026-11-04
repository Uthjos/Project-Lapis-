from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from src.data_file_manage.DirectoryPath import DirectoryPath as dp
from src.data_file_manage.ExporterFactory import ExporterFactory
from src.data_file_manage.ParserFactory import ParserFactory


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
            "scale": tuple(self.scale),
            "rotation": self.rotation,
            "h_flip": self.h_flip,
            "v_flip": self.v_flip,
            "center": tuple(self.center),
        }

    def load(self, data: dict):
        self.x = data["x"]
        self.y = data["y"]
        self.scale = data["scale"]
        self.rotation = data["rotation"]
        self.h_flip = data["h_flip"]
        self.v_flip = data["v_flip"]
        self.center = data["center"]

        return self


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

    def load(self, data: dict):
        self.part = data["part"]
        self.file_location = data["file_location"]
        super().load(data)
        return self


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

    def load(self, data: dict):
        self.frame_number = data["frame_number"]
        self.time_to_next_frame = data["time_to_next_frame"]

        self.sprites.clear()

        for s in data["sprites"]:
            sprite = SpriteData().load(s)
            self.sprites.append(sprite)

        return self



"""contains every possible action that a NPC or Character should be able to do"""
@dataclass
class AnimationStack:


    # Every direction contains a dict of actions and actions contains list of frames
    animations: dict = field(
        default_factory=lambda: {
            direction: {
                action: [] for action in Action
            }
            for direction in SpriteDirection
        }
    )


    def add_frame(
            self,
            frame: Frame,
            action: Action,
            direction: SpriteDirection
    ):
        self.animations[direction][action].append(frame)

    def to_dict(self):
        return {
            direction.value: {
                action.value: [
                    frame.to_dict() for frame in frames
                ]
                for action, frames in actions.items()
            }
            for direction, actions in self.animations.items()
        }

    def export_to_json(self, name: str):
        name_ext = name + ".json"
        path = (
            dp.get_dir(dp.ANIMATION) / Path(name_ext)
        )

        ExporterFactory.createExporter('json').export(data=self.to_dict(), fileName=path)

    def load_animations(self, filename: str):
        data = ParserFactory.create_parser("json").parse_file(filename)

        self.animations = {
            direction: {
                action: [
                    Frame().load(frame_data)
                    for frame_data in data.get(direction.value, {}).get(
                        action.value, []
                    )
                ]
                for action in Action
            }
            for direction in SpriteDirection
        }


if __name__ == "__main__":
    test = AnimationStack()

    test.export_to_json("test")
