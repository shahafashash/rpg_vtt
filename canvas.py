from __future__ import annotations
from typing import List

import pygame
from pygame import Vector2
import custom_events as CustomPyGameEvents
from models import Message


class MapEntity:
    def __init__(self, canvas: Canvas):
        self.pos = Vector2()
        self.scale = 1.0

        self.draggable = False
        self.scaleable = False
        self.selectable = False
        self.selected = False

        self.is_dragging = False
        self.mouse_world_to_self = Vector2()
        self.canvas = canvas

    def handle_event(self, message: Message):
        event = message.event
        extra = message.extra

        if self.selected:
            # drag
            if self.draggable:
                if event.type == CustomPyGameEvents.LEFT_MOUSE_CLICK_DOWN:
                    self.is_dragging = True
                    mouse_in_world = (Vector2(extra['pos']) - self.canvas.cam) / self.canvas.scale
                    self.mouse_world_to_self = self.pos - mouse_in_world

                if event.type == CustomPyGameEvents.LEFT_MOUSE_CLICK_UP:
                    self.is_dragging = False

                if event.type == pygame.MOUSEMOTION and self.is_dragging:
                    mouse_in_world = (Vector2(extra['pos']) - self.canvas.cam) / self.canvas.scale
                    self.pos = mouse_in_world + self.mouse_world_to_self

            # scale
            if self.scaleable:
                if event.type in (CustomPyGameEvents.WHEEL_PRESS_DOWN, CustomPyGameEvents.WHEEL_PRESS_UP):
                    scale_value = 1.1 if event.type == CustomPyGameEvents.WHEEL_PRESS_UP else 0.9
                    self.scale *= scale_value
                    self.update_scale()

        # check for selection
        if event.type == pygame.MOUSEMOTION:
            if self.selectable:
                self.check_if_selected(extra['pos'])

    def check_if_selected(self, mouse_pos: Vector2) -> None:
        ...

    def update_scale(self) -> None:
        ...

    def update_canvas_scale(self, win: pygame.Surface) -> None:
        ...



class Canvas:
    def __init__(self):
        self.cam = Vector2()
        self.scale = 1.0

        self._is_dragging = False
        self._mouse_to_cam: Vector2 = None
        self.entities: List[MapEntity] = []

    def register_map_entity(self, entity: MapEntity) -> None:
        self.entities.append(entity)

    def handle_event(self, message: Message) -> None:
        event = message.event
        extra = message.extra

        if event.type in (CustomPyGameEvents.WHEEL_PRESS_DOWN, CustomPyGameEvents.WHEEL_PRESS_UP):
                scale_value = 1.1 if event.type == CustomPyGameEvents.WHEEL_PRESS_UP else 0.9
                mouse_pos = Vector2(extra['pos'])
                mouse_to_cam = (self.cam - mouse_pos) * scale_value

                self.cam = mouse_pos + mouse_to_cam
                self.scale *= scale_value
                for entity in self.entities:
                    entity.update_canvas_scale(self)

        elif event.type == CustomPyGameEvents.LEFT_MOUSE_CLICK_DOWN:
            self._is_dragging = True
            self._mouse_to_cam = self.cam - Vector2(extra['pos'])

        elif event.type == CustomPyGameEvents.LEFT_MOUSE_CLICK_UP:
            self._is_dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self._is_dragging:
                mouse_pos = Vector2(event.pos)
                self.cam = mouse_pos + self._mouse_to_cam

    def mouse_in_world(self, mouse_in_win: Vector2) -> Vector2:
        mouse_in_world = (Vector2(mouse_in_win) - self.cam) / self.scale
        return mouse_in_world
