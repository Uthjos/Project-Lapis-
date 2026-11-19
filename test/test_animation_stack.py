

import pygame
import pytest
from pygame.math import Vector2

from src.animation.animation_stack import (
    Action,
    AnimationPart,
    AnimationStack,
    Frame,
    PygameProp,
    SpriteData,
    SpriteDirection,
)


@pytest.fixture(autouse=True)
def pygame_setup():
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


@pytest.fixture
def test_image():
    image = pygame.Surface((32, 32), pygame.SRCALPHA)
    image.fill("white")
    return image


# --------------------------------------------------
# PYGAME PROP TESTS
# --------------------------------------------------

def test_prop_initialization():

    prop = PygameProp(
        x=20,
        y=10,
        pivot=(100, 100)
    )

    assert prop.x == 20
    assert prop.y == 10
    assert prop.pivot == Vector2(100, 100)
    assert prop.pos == Vector2(20, 10)
    assert prop.center == Vector2(120, 110)


def test_pivot_rotation(test_image):

    prop = PygameProp(
        x=32,
        y=0,
        rotation=90,
        scale=(32, 32),
        pivot=(100, 100),
        image_orig=test_image
    )

    image, rect = prop.update()

    expected = Vector2(100, 100) + Vector2(32, 0).rotate(-90)

    assert image is not None
    assert rect is not None

    assert rect.centerx == pytest.approx(expected.x, abs=1)
    assert rect.centery == pytest.approx(expected.y, abs=1)


def test_zero_rotation(test_image):

    prop = PygameProp(
        x=32,
        y=0,
        pivot=(100, 100),
        image_orig=test_image
    )

    image, rect = prop.update()

    assert rect.center == (132, 100)
    assert image.get_size() == (32, 32)


def test_scaling(test_image):

    prop = PygameProp(
        scale=(64, 64),
        image_orig=test_image
    )

    image, rect = prop.update()

    assert image.get_size() == (64, 64)
    assert rect.size == (64, 64)


def test_horizontal_flip(test_image):

    test_image.set_at((0, 0), (255, 0, 0, 255))

    prop = PygameProp(
        h_flip=True,
        image_orig=test_image
    )

    image, rect = prop.update()

    assert image.get_at((31, 0)) == (255, 0, 0, 255)
    assert rect.size == (32, 32) # default rectangle size


def test_vertical_flip(test_image):

    test_image.set_at((0, 0), (255, 0, 0, 255))

    prop = PygameProp(
        v_flip=True,
        image_orig=test_image
    )

    image, rect = prop.update()

    assert image.get_at((0, 31)) == (255, 0, 0, 255)
    assert rect.size == (32, 32) # default rectangle size


# --------------------------------------------------
# SERIALIZATION TESTS
# --------------------------------------------------

def test_prop_serialization():

    prop = PygameProp(
        x=12,
        y=24,
        rotation=45,
        scale=(64, 64),
        h_flip=True,
        v_flip=False,
        pivot=(100, 200)
    )

    data = prop.to_dict()

    restored = PygameProp.from_dict(data)

    assert restored.x == 12
    assert restored.y == 24
    assert restored.rotation == 45
    assert restored.scale == (64, 64)
    assert restored.h_flip is True
    assert restored.v_flip is False
    assert restored.pivot == Vector2(100, 200)


def test_sprite_serialization():

    sprite = SpriteData(
        part=AnimationPart.HEAD,
        props=PygameProp(
            x=10,
            y=-20,
            rotation=30
        )
    )

    data = sprite.to_dict()

    restored = SpriteData.from_dict(data)

    assert restored.part == AnimationPart.HEAD
    assert restored.props.x == 10
    assert restored.props.y == -20
    assert restored.props.rotation == 30


def test_frame_serialization():

    frame = Frame(
        sprites=[
            SpriteData(
                part=AnimationPart.HEAD,
                props=PygameProp(x=10)
            ),
            SpriteData(
                part=AnimationPart.TORSO,
                props=PygameProp(y=20)
            )
        ],
        time_to_next_frame=150
    )

    restored = Frame.from_dict(frame.to_dict())

    assert len(restored.sprites) == 2
    assert restored.time_to_next_frame == 150
    assert restored.sprites[0].part == AnimationPart.HEAD
    assert restored.sprites[1].part == AnimationPart.TORSO


# --------------------------------------------------
# ANIMATION STACK TESTS
# --------------------------------------------------

def test_animation_stack_initialization():

    stack = AnimationStack()

    assert len(stack.animations) == 8

    for direction in SpriteDirection:
        for action in Action:
            assert stack.animations[direction][action] == []


def test_add_frame():

    stack = AnimationStack()

    frame = Frame(time_to_next_frame=120)

    stack.add_frame(
        frame,
        Action.WALK,
        SpriteDirection.E
    )

    assert len(
        stack.animations[SpriteDirection.E][Action.WALK]
    ) == 1


def test_animation_stack_serialization():

    stack = AnimationStack()

    frame = Frame(
        sprites=[
            SpriteData(
                part=AnimationPart.HEAD,
                props=PygameProp(
                    x=10,
                    y=15,
                    rotation=45
                )
            )
        ],
        time_to_next_frame=200
    )

    stack.add_frame(
        frame,
        Action.IDLE,
        SpriteDirection.S
    )

    data = stack.to_dict()

    restored = AnimationStack.from_dict(data)

    frames = restored.animations[
        SpriteDirection.S
    ][Action.IDLE]

    assert len(frames) == 1
    assert frames[0].time_to_next_frame == 200
    assert frames[0].sprites[0].props.rotation == 45


def test_display_on_screen(test_image):

    stack = AnimationStack()

    stack.add_image(
        test_image,
        AnimationPart.HEAD,
        SpriteDirection.S
    )

    frame = Frame(
        sprites=[
            SpriteData(
                part=AnimationPart.HEAD,
                props=PygameProp(
                    x=0,
                    y=0
                )
            )
        ],
        time_to_next_frame=100
    )

    stack.add_frame(
        frame,
        Action.IDLE,
        SpriteDirection.S
    )

    screen = pygame.Surface((192, 108))
    # specify the color
    screen.fill((0, 0, 0, 255))

    delay = stack.display_on_screen(
        screen,
        0,
        SpriteDirection.S,
        Action.IDLE
    )

    assert delay == 100

    # The image should be drawn at the center of the screen.
    # and image should be (0, 0, 0, 255) since default surface is a black box
    assert screen.get_at((96, 54)) == (0, 0, 0, 255)


def test_invalid_frame_index():

    stack = AnimationStack()

    screen = pygame.Surface((192, 108))

    with pytest.raises(IndexError):
        stack.display_on_screen(
            screen,
            0,
            SpriteDirection.S,
            Action.IDLE
        )
