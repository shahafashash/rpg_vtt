from typing import List
import os
from random import choice
from dataclasses import dataclass

import pygame
from pygame.math import Vector2
from pydantic import BaseModel

from common import MapInteractiveState, GridType, MapModel, GridModel, TokenModel
from drawing_utils import draw_grid_hex, draw_grid_square
import backend.custom_events as CustomPyGameEvents
from backend.models import Message

from menu_gui import Gui, ImageToggle, StackPanel, HORIZONTAL

@dataclass
class Transformation:
    pos = Vector2()
    scale = 1.0



class MapEntity:
    def __init__(self):
        self.pos = Vector2()
        self.scale = 1.0

        self.draggable = False
        self.scaleable = False
        self.selectable = False
        self.selected = False
        self.has_context_menu = False

        self.is_dragging = False
        self.mouse_world_to_self = Vector2()
        self.context_menu_opened = False

    def handle_event(self, message: Message, transform: Transformation):
        event = message.event
        extra = message.extra

        if self.selected:
            # drag
            if self.draggable:
                if event.type == CustomPyGameEvents.LEFT_MOUSE_CLICK_DOWN:
                    self.is_dragging = True
                    mouse_in_world = (Vector2(extra['pos']) - transform.pos) / transform.scale
                    self.mouse_world_to_self = self.pos - mouse_in_world

                if event.type == CustomPyGameEvents.LEFT_MOUSE_CLICK_UP:
                    self.is_dragging = False

                if event.type == pygame.MOUSEMOTION and self.is_dragging:
                    mouse_in_world = (Vector2(extra['pos']) - transform.pos) / transform.scale
                    self.pos = mouse_in_world + self.mouse_world_to_self

            if self.has_context_menu and event.type == CustomPyGameEvents.RIGHT_MOUSE_CLICK_DOWN:
                self.context_menu_opened = True

            # scale
            if self.scaleable:
                if event.type in (CustomPyGameEvents.WHEEL_PRESS_DOWN, CustomPyGameEvents.WHEEL_PRESS_UP):
                    scale_value = 1.1 if event.type == CustomPyGameEvents.WHEEL_PRESS_UP else 0.9
                    self.scale *= scale_value
                    self.update_scale(transform)

        # check for selection
        if event.type == pygame.MOUSEMOTION:
            if self.selectable:
                self.check_if_selected(extra['pos'], transform)

    def check_if_selected(self, mouse_pos: Vector2, transform: Transformation) -> None:
        ...

    def update_scale(self, transform: Transformation) -> None:
        ...

    def on_canvas_scale_update(self, transform: Transformation) -> None:
        ...
    
    def step(self) -> None:
        ...

    def draw(self, win: pygame.Surface, transform: Transformation) -> None:
        ...
    
    def get_current_state(self) -> BaseModel:
        ...
    
    def load_state(self, model: BaseModel):
        ...



class Map(MapEntity):
    def __init__(self):
        self.path: str = None
        self.surf_initial: pygame.Surface = None
        self.surf: pygame.Surface = None

    def set_map_image(self, path: str, transform: Transformation):
        self.path = path
        if os.path.exists(path):
            self.surf_initial = pygame.image.load(path)
            self.on_canvas_scale_update(transform)
        else:
            raise FileNotFoundError(f"Map image not found at {path}")

    def on_canvas_scale_update(self, transform: Transformation) -> None:
        super().on_canvas_scale_update(transform)
        self.surf = pygame.transform.smoothscale_by(self.surf_initial, transform.scale)

    def draw(self, win: pygame.Surface, transform: Transformation) -> None:
        if self.surf is None:
            return
        win.blit(self.surf, transform.pos)

        
    
    def get_current_state(self) -> MapModel:
        return MapModel(path=self.path)

    def load_state(self, model: MapModel, transform: Transformation):
        self.path = model.path
        self.set_map_image(self.path, transform)



class Grid(MapEntity):
    def __init__(self):
        super().__init__()
        self.grid_type = GridType.NONE
        self.initial_size = 50.0
        self.size = self.initial_size

        self.selectable = True
        self.draggable = True
        self.scaleable = True

    def on_canvas_scale_update(self, transform: Transformation) -> None:
        super().on_canvas_scale_update(transform)
        self.size = self.initial_size * transform.scale * self.scale

    def update_scale(self, transform: Transformation):
        super().update_scale(transform)
        self.size = self.initial_size * transform.scale * self.scale

    def check_if_selected(self, mouse_pos: Vector2, transform: Transformation) -> None:
        self.selected = True

    def draw(self, win: pygame.Surface, transform: Transformation) -> None:
        pos = transform.pos + self.pos * transform.scale
        if self.grid_type == GridType.SQUARE:
            draw_grid_square(win, pos, self.size)

    def get_current_state(self):
        return GridModel(grid_type=self.grid_type,
                         size=self.size,
                         pos=self.pos,
                         scale=self.scale)

    def load_state(self, model: GridModel):
        self.pos = Vector2(model.pos)
        self.scale = model.scale
        self.size = model.size
        self.grid_type = GridType(model.grid_type)

    def set_grid_type(self, grid_type: GridType) -> None:
        self.grid_type = grid_type


def handel_gui_events(gui: Gui, state: MapInteractiveState) -> MapInteractiveState:
    # todo: this should be simplified

    output = state

    event, _ = gui.listen()
    if event == 'map_tool':
        output = MapInteractiveState.EDIT_WORLD
        gui.get_element_by_key('grid_tool').set_value(False)
        gui.get_element_by_key('token_tool').set_value(False)

    elif event == 'grid_tool':
        output = MapInteractiveState.EDIT_GRID
        gui.get_element_by_key('map_tool').set_value(False)
        gui.get_element_by_key('token_tool').set_value(False)

    elif event == 'token_tool':
        output = MapInteractiveState.EDIT_TOKENS
        gui.get_element_by_key('map_tool').set_value(False)
        gui.get_element_by_key('grid_tool').set_value(False)

    return output


