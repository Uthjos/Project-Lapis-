import json

from src.animation.AnimationStack import (
    Action,
    AnimationPart,
    AnimationStack,
    Frame,
    PygameProp,
    SpriteData,
    SpriteDirection,
)


def test_animation_stack_roundtrip():
    stack = AnimationStack()
    stack.add_frame(
        Frame(sprites=[SpriteData(part=AnimationPart.TORSO,
                                  file_location="E/walk/head_00.png",
                                  props=PygameProp(x=3, scale=(2.0, 2.0), rotation=15))],
              time_to_next_frame=120),
        Action.WALK, SpriteDirection.E)

    restored = AnimationStack.from_dict(json.loads(json.dumps(stack.to_dict())))
    assert restored == stack