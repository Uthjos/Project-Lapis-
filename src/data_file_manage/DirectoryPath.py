from __future__ import annotations

from enum import Enum
from pathlib import Path

#parent makes it go back to the parent folder, which to have it in the main
# project folder added 3 parent
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

class DirectoryPath(Enum):
    ROOT = BASE_DIR
    DATA = DATA_DIR


    SPRITE = DATA_DIR / 'sprites'
    WEAPON = DATA_DIR / 'weapons'
    ANIMATION = DATA_DIR / 'animations'
    STAGE = DATA_DIR / 'stages'

    ASSET_TEST_DIR = BASE_DIR / 'src' / 'assets'

    """This will checks the directory path to see if it exists
    and will make it make a directory if it does"""
    # Test change by Majid
    @staticmethod
    def _make_dir(dirpath: DirectoryPath):
        dirpath.value.mkdir(parents=True, exist_ok=True)

    """Use this to call the Directory paths"""
    @staticmethod
    def get_dir(dirpath: DirectoryPath) -> DirectoryPath:
        DirectoryPath._make_dir(dirpath)
        return dirpath

if __name__ == '__main__':
    sprite_dir = DirectoryPath.get_dir(DirectoryPath.SPRITE)

    print(sprite_dir)