
from enum import Enum
from typing import List, Tuple, Optional

from pydantic import BaseModel
import pygame

class HaloFont:
    def __init__(self, font, width=1):
        self.font: pygame.font.Font = font
        self.width = width

    def render(self, text, aa, color, halo=(0,0,0)) -> pygame.Surface:
        halo_surf = self.font.render(text, aa, halo)
        text_surf = self.font.render(text, aa, color)
        
        surf = pygame.Surface((text_surf.get_width() + 2 * self.width, text_surf.get_height() + 2 * self.width), pygame.SRCALPHA)
        for i in [(0, self.width), (self.width, 0), (self.width, 2 * self.width), (2 * self.width, 1)]:
            surf.blit(halo_surf, i)

        surf.blit(text_surf, (self.width, self.width))
        return surf

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
    pos: Tuple[float, float]
    scale: float


class TokenModel(BaseModel):
    path: str
    pos: Tuple[float, float]
    scale: float


class CanvasModel(BaseModel):
    pos: Tuple[float, float]
    scale: float

    map: MapModel
    grid: GridModel
    tokens: Optional[List[TokenModel]]
