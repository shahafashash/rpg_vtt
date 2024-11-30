
from enum import Enum
from typing import List, Tuple, Optional
from pydantic import BaseModel


class MapInteractiveState(Enum):
    NONE = 0
    EDIT_WORLD = 1
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


class MapModel(BaseModel):
    path: str

class GridModel(BaseModel):
    grid_type: int
    size: float
    pos: Tuple[int, int]
    scale: float

class TokenModel(BaseModel):
    path: str
    pos: Tuple[int, int]
    scale: float

class CanvasModel(BaseModel):
    pos: Tuple[int, int]
    scale: float

    map: MapModel
    grid: GridModel
    tokens: Optional[List[TokenModel]]
