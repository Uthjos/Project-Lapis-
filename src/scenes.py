from enum import IntEnum


class Scene(IntEnum):
    """
    This is an enum file for all game scenes. This is a global reference for all scenes to know what other scenes are
    available to swap to. Use this to transition into different scenes like main menu or alternate worlds.
    """
    QUIT = -1
    MENU = 0
    GAME = 1
