from typing import List

import pygame
from pygame.math import Vector2

from common import TokenModel
from map_entities import MapEntity, Transformation

class Token(MapEntity):
    _init_scale = 1.0
    def __init__(self, pos: Vector2, image_path: str, transform: Transformation):
        super().__init__()
        self.path = image_path
        self.pos = Vector2(pos)

        self.scale = Token._init_scale
        self.surf_initial: pygame.Surface = pygame.image.load(image_path)
        self.decorations: List[pygame.Surface] = []
        self.pos /= transform.scale
        self.update_scale(transform)

        self.selectable = True
        self.scaleable = True
        self.draggable = True
        self.has_context_menu = True


    def on_canvas_scale_update(self, transform) -> None:
        super().on_canvas_scale_update(transform)
        self.update_scale(transform)

    def update_scale(self, transform: Transformation):
        super().update_scale(transform)
        Token._init_scale = self.scale
        self.surf = pygame.transform.smoothscale_by(self.surf_initial, self.scale * transform.scale)
        # for i, decoration in enumerate(self.decorations):
        #     self.decorations[i] = pygame.transform.smoothscale_by(decoration, self.scale * transform.scale)

    def check_if_selected(self, mouse_pos: Vector2, transform: Transformation) -> None:
        self.selected = False
        pos = transform.pos + self.pos * transform.scale
        if pos.distance_to(mouse_pos) < self.surf.get_size()[0] / 2:
            self.selected = True

    def draw(self, win: pygame.Surface, transform: Transformation) -> None:
        pos = transform.pos + self.pos * transform.scale
        win.blit(self.surf, pos - Vector2(self.surf.get_size()) / 2)

        radius = self.surf.get_size()[0] // 2
        for i, decoration in enumerate(self.decorations):
            win.blit(decoration, pos + Vector2(radius / 2 + (decoration.get_width()) * i, radius / 2))

        if self.selected:
            pygame.draw.circle(win, (255, 255, 255), pos, radius, 1)
    
    def add_decoration(self, decoration_surf: pygame.Surface) -> None:
        self.decorations.append(decoration_surf)

    def get_current_state(self):
        return TokenModel(path=self.path,
                          pos=self.pos,
                          scale=self.scale)

    @classmethod
    def from_model(cls, model: TokenModel):
        obj = cls((0,0), model.path, Transformation())
        obj.pos = Vector2(model.pos)
        obj.scale = model.scale
        return obj