
from enum import Enum
from typing import Tuple


class MapInteractiveState(Enum):
    NONE = 0
    EDIT_MAP = 1
    EDIT_GRID = 2
    EDIT_TOKENS = 3


class GridType(Enum):
    NONE = 0
    SQUARE = 1
    HEX = 2


class GridColors(Tuple, Enum):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)