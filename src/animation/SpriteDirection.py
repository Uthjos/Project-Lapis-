
from enum import Enum

from src.animation.AnimationStack import AnimationPart

# priority is associated with direction lower number means that they will be put first
# meaning that they will be in the back of the sprite layer

# for the North direction and South direction
# front will be right part on screen and
# back will be left part on screen
class SpriteDirection(Enum):
    BACK_ARM = AnimationPart.BACK_ARM.value
    BACK_LEG = AnimationPart.BACK_LEG.value
    HIP = AnimationPart.HIP.value
    TORSO = AnimationPart.TORSO.value
    FRONT_LEG = AnimationPart.FRONT_LEG.value
    HEAD = AnimationPart.HEAD.value
    FRONT_ARM = AnimationPart.FRONT_ARM.value
    FRONT_CLOAK = AnimationPart.FRONT_CLOAK.value
    BACK_CLOAK = AnimationPart.BACK_CLOAK.value
    FRONT_TASSET = AnimationPart.FRONT_TASSET.value
    BACK_TASSET = AnimationPart.BACK_TASSET.value
    FRONT_PAULDRON = AnimationPart.FRONT_PAULDRON.value
    BACK_PAULDRON = AnimationPart.BACK_PAULDRON.value

    N = ("N", {
        FRONT_LEG: 1,
        BACK_LEG: 2,
        HIP: 3,
        FRONT_TASSET: 4,
        BACK_TASSET: 5,
        TORSO: 6,
        FRONT_ARM: 7,
        BACK_ARM: 8,
        FRONT_PAULDRON: 9,
        BACK_PAULDRON: 10,
        HEAD: 11,
        FRONT_CLOAK: 12,
        BACK_CLOAK: 13,
    })
    NE = ("NE", {
        BACK_PAULDRON: 1,
        BACK_CLOAK: 2,
        BACK_ARM: 3,
        BACK_TASSET: 4,
        BACK_LEG: 5,
        HIP: 6,
        FRONT_LEG: 7,
        TORSO: 8,
        FRONT_TASSET: 9,
        FRONT_ARM: 10,
        HEAD: 11,
        FRONT_PAULDRON: 12,
        FRONT_CLOAK: 13,
    })
    E = ("E", {
        BACK_PAULDRON: 1,
        BACK_CLOAK: 2,
        BACK_ARM: 3,
        BACK_TASSET: 4,
        BACK_LEG: 5,
        HIP: 6,
        FRONT_LEG: 7,
        TORSO: 8,
        FRONT_TASSET: 9,
        HEAD: 10,
        FRONT_ARM: 11,
        FRONT_PAULDRON: 12,
        FRONT_CLOAK: 13,
    })
    SE = ("SE", {
        BACK_CLOAK: 1,
        BACK_PAULDRON: 2,
        BACK_ARM: 3,
        BACK_LEG: 4,
        BACK_TASSET: 5,
        HIP: 6,
        FRONT_LEG: 7,
        TORSO: 8,
        FRONT_TASSET: 9,
        FRONT_ARM: 10,
        FRONT_PAULDRON: 11,
        HEAD: 12,
        FRONT_CLOAK: 13,
    })
    S = ("S", {
        FRONT_CLOAK: 1,
        BACK_CLOAK: 2,
        FRONT_LEG: 3,
        BACK_LEG: 4,
        HIP: 5,
        FRONT_TASSET: 6,
        BACK_TASSET: 7,
        TORSO: 8,
        FRONT_ARM: 9,
        BACK_ARM: 10,
        FRONT_PAULDRON: 11,
        BACK_PAULDRON: 12,
        HEAD: 13,
    })
    SW = ("SW", {
        BACK_CLOAK: 1,
        BACK_PAULDRON: 2,
        BACK_ARM: 3,
        BACK_LEG: 4,
        BACK_TASSET: 5,
        HIP: 6,
        FRONT_LEG: 7,
        TORSO: 8,
        FRONT_TASSET: 9,
        FRONT_ARM: 10,
        FRONT_PAULDRON: 11,
        HEAD: 12,
        FRONT_CLOAK: 13,
    })
    W = ("W", {
        BACK_PAULDRON: 1,
        BACK_CLOAK: 2,
        BACK_ARM: 3,
        BACK_TASSET: 4,
        BACK_LEG: 5,
        HIP: 6,
        FRONT_LEG: 7,
        TORSO: 8,
        FRONT_TASSET: 9,
        HEAD: 10,
        FRONT_ARM: 11,
        FRONT_PAULDRON: 12,
        FRONT_CLOAK: 13,
    })
    NW = ("NW", {
        BACK_PAULDRON: 1,
        BACK_CLOAK: 2,
        BACK_ARM: 3,
        BACK_TASSET: 4,
        BACK_LEG: 5,
        HIP: 6,
        FRONT_LEG: 7,
        TORSO: 8,
        FRONT_TASSET: 9,
        FRONT_ARM: 10,
        HEAD: 11,
        FRONT_PAULDRON: 12,
        FRONT_CLOAK: 13,
    })

    def __init__(self, direction, layer_priority):
        self.direction = direction
        self.layer_priority = layer_priority