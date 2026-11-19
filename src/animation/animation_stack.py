from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

import pygame
from pygame.math import Vector2
from pygame.transform import scale

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

    # these are for when we want to display another sprite with
    # a smear frame or something
    ACTION_PART1 = "action_part1"
    ACTION_PART2 = "action_part2"
    ACTION_PART3 = "action_part3"
    ACTION_PART4 = "action_part4"


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
    """Transformation and pivot information for an individual sprite."""
    x: float = 0
    y: float = 0

    rotation: float = 0
    scale: tuple[int, int] = (32, 32)

    h_flip: bool = False
    v_flip: bool = False

    pivot: Vector2 = field(
        default_factory=lambda: Vector2(0, 0)
    )  # The position of the pivot point

    pos = Vector2(x, y)  # The position of the image

    # Create the image based on the initiation or make a blank pygame surface
    image_orig: Optional[pygame.Surface] = field(
        default=None,
        repr=False,
        compare=False,
    )

    def __post_init__(self):
        self.pivot = Vector2(self.pivot)
        self.scale = tuple(self.scale)

    @property
    def pos(self) -> Vector2:
        """Local offset from the pivot"""
        return Vector2(self.x, self.y)

    @property
    def center(self) -> Vector2:
        """Unrotated image center."""
        return self.pivot + self.pos

    def transform_image(self, image=None):
        """Apply scale, flip, flip and rotation to an image.

        Returns: image, rect
        """
        # image from the direction when called and when you are
        image = image if image is not None else self.image_orig

        if image is None:
            return None, None

        # Scale
        if image.get_size != self.scale:
            image = pygame.transform.scale(
                image, self.scale
            )

        # Flip
        if self.h_flip or self.v_flip:
            image = pygame.transform.flip(image, self.h_flip, self.v_flip)

        # Calculate the rotated image center
        offset = self.pivot + self.pos.rotate(-self.rotation)

        rect = image.get_rect(center=offset)

        return image, rect


    def rotate_on_pivot(self, image=None):
        """Rotate an image around the fixed pivot point."""
        return self.transform_image(image)

    def update(self):
        return self.transform_image()

    def draw(self, surface, image=None, origin=None):
        """Draw the transformed image.

        origin optionally overrides the world-space pivot.
        """

        if origin is not None:
            old_pibot = self.pivot
            self.pivot = Vector2(origin)

            transformed, rect = self.transform_image(image)

            self.pivot = old_pibot
        else:
            transformed, rect = self.transform_image(image)

        if transformed is not None:
            surface.blit(transformed, rect)

        return rect

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "scale": tuple(self.scale),
            "rotation": self.rotation,
            "h_flip": self.h_flip,
            "v_flip": self.v_flip,
            "pivot": list(self.pivot)
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Reconstruct transformation properties from JSON data"""

        return cls(
            x=data.get("x", 0),
            y=data.get("y", 0),
            scale=tuple(data.get("scale", (32, 32))),
            rotation=data.get("rotation", 0),
            h_flip=data.get("h_flip", False),
            v_flip=data.get("v_flip", False),
            pivot=Vector2(data.get("pivot", (0, 0))),
        )



@dataclass
class SpriteData(PygameProp):
    """the Individual character sprite/body part"""

    part: AnimationPart = AnimationPart.HEAD
    props: PygameProp = field(default_factory=PygameProp)

    def to_dict(self):
        return {
            "part": self.part.value,
            "properties": self.props.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            part=AnimationPart(d["part"]),
            props=PygameProp.from_dict(d.get("properties", {})),
        )






@dataclass
class Frame(PygameProp):
    """The whole picture where every part comes together for a single frame"""
    # layer order is based on where the sprite is on the sprite list
    sprites: list[SpriteData] = field(default_factory=list)
    time_to_next_frame: int = 100

    def to_dict(self):
        return {
            "time_to_next_frame": self.time_to_next_frame,
            "sprites": [s.to_dict() for s in self.sprites],
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            sprites=[
                SpriteData().from_dict(sprite)
                for sprite in data.get("sprites", [])
            ],
            time_to_next_frame=data.get("time_to_next_frame", 100),
        )




@dataclass
class AnimationStack:
    """contains every possible action that a NPC or Character should be able to do"""
    # Every direction contains a dict of actions and actions contains list of frames
    animations: dict = field(
        default_factory=lambda: {
            direction: {
                action: []
                for action in Action
            }
            for direction in SpriteDirection
        }
    )

    #Create dictionary to hold sprite images for direction
    images: dict = field(
        default_factory=lambda: {
            direction: {
                part: None
                for part in AnimationPart
            }
            for direction in SpriteDirection
        }
    )

    # holds file location
    file_location: dict = field(
        default_factory=lambda: {
            direction: {
                part: None
                for part in AnimationPart
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

    def add_image(
            self,
            image: pygame.Surface,
            part: AnimationPart,
            direction:SpriteDirection
    ):
        self.images[direction][part] = image

    def display_on_screen(
            self,
            screen: pygame.Surface,
            frame_index: int,
            direction: SpriteDirection,
            action: Action
    ):
        frames = self.animations[direction][action]

        if not 0 <= frame_index < len(frames):
            raise IndexError("Animation frame index out of range")

        frame = frames[frame_index]

        # Character's base reference point
        origin =Vector2(screen.get_rect().center)

        for sprite in frame.sprites:

            image = self.images[direction].get(sprite.part)

            if image is not None:
                continue

            sprite.props.draw(
                screen,
                image=image,
                origin=origin + sprite.props.pivot
            )
        # return the time to next frame for game model or ui to handle it
        return frame.time_to_next_frame



    def to_dict(self):
        return {
            "animation": {
                direction.value: {
                    action.value: [
                        frame.to_dict()
                        for frame in frames
                    ]
                    for action, frames in actions.items()
                }
                for direction, actions in self.animations.items()
            },

            "file_location": {
                direction.value: {
                    part.value: location
                    for part, location in part.items()
                }
                for direction, part in self.file_location.items()
            }

        }

    @classmethod
    def from_dict(cls, data: dict):
        stack = cls()

        animation_data = data.get("animation", data)

        for direction in SpriteDirection:
            direction_data = animation_data.get(
                 direction.value, {}
            )

            for action in Action:
                raw_frames = direction_data.get(
                    action.value,[]
                )

                stack.animations[direction][action] = [
                    Frame.from_dict(frame)
                    for frame in raw_frames
                ]

            locations = data.get(
                "file_location", {}
            ).get(direction.value, {})

            for part in AnimationPart:
                stack.file_location[direction][part] = (
                    locations.get(part.value)
                )

        return stack

    def load_animations(self, filename: str):
        data = ParserFactory.create_parser("json").parse_file(filename)
        loaded_animation = AnimationStack.from_dict(data)

        self.animations = loaded_animation.animations
        self.file_location = loaded_animation.file_location

    def export_to_json(self, name: str):
        path = dp.get_dir(dp.ANIMATION) / f"{name}.json"
        ExporterFactory.get_exporter("json").export(data=self.to_dict(), filename=path)
