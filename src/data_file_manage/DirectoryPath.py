from enum import Enum
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

class DirectoryPath(Enum):
    ROOT = BASE_DIR
    DATA = DATA_DIR
    SPRITE = DATA_DIR / 'sprites'
    WEAPON = DATA_DIR / 'weapons'
    ANIMATION = DATA_DIR / 'animations'
    STAGE = DATA_DIR / 'stages'
    # Test change by Majid



