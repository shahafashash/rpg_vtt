from __future__ import annotations
from typing import List

import pygame
from pygame import Vector2

from common import MapInteractiveState
import backend.custom_events as CustomPyGameEvents
from backend.models import Message
from map_entities import Transformation, MapEntity, Map, Grid, Token


class Canvas:
    def __init__(self):
        self.transform = Transformation()

        self._is_dragging = False
        self._mouse_to_cam: Vector2 = None

        self.map = Map()
        self.grid = Grid()
        self.tokens: List[Token] = []

        self.entities: List[MapEntity] = [self.map, self.grid]

        self.events: List[Message] = []
        self.state = MapInteractiveState.EDIT_WORLD

    def add_token(self, image_path: str, pos: Vector2) -> None:
        token = Token(pos, image_path)
        self.entities.append(token)
        self.tokens.append(token)

    def insert_event(self, message: Message) -> None:
        self.events.append(message)

    def handle_event(self, message: Message) -> None:
        while len(self.events) > 0:
            event_from_que = self.events.pop()
            self.handle_event(event_from_que)

        event = message.event
        extra = message.extra
        
        if event.type == CustomPyGameEvents.CANVAS_SWITCH_MODE_WORLD:
            self.state = MapInteractiveState.EDIT_WORLD
        elif event.type == CustomPyGameEvents.CANVAS_SWITCH_MODE_GRID:
            self.state = MapInteractiveState.EDIT_GRID
        elif event.type == CustomPyGameEvents.CANVAS_SWITCH_MODE_TOKENS:
            self.state = MapInteractiveState.EDIT_TOKENS

        elif event.type == CustomPyGameEvents.ADD_TOKEN:
            self.add_token(extra['file'], extra['pos'])


        if self.state == MapInteractiveState.EDIT_WORLD:
            if event.type in (CustomPyGameEvents.WHEEL_PRESS_DOWN, CustomPyGameEvents.WHEEL_PRESS_UP):
                scale_value = 1.1 if event.type == CustomPyGameEvents.WHEEL_PRESS_UP else 0.9
                mouse_pos = Vector2(extra['pos'])
                mouse_to_cam = (self.transform.pos - mouse_pos) * scale_value

                self.transform.pos = mouse_pos + mouse_to_cam
                self.transform.scale *= scale_value
                for entity in self.entities:
                    entity.on_canvas_scale_update(self.transform)

            elif event.type == CustomPyGameEvents.LEFT_MOUSE_CLICK_DOWN:
                self._is_dragging = True
                self._mouse_to_cam = self.transform.pos - Vector2(extra['pos'])

            elif event.type == CustomPyGameEvents.LEFT_MOUSE_CLICK_UP:
                self._is_dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if self._is_dragging:
                    mouse_pos = Vector2(event.pos)
                    self.transform.pos = mouse_pos + self._mouse_to_cam
        
        elif self.state == MapInteractiveState.EDIT_GRID:
            self.grid.handle_event(message, self.transform)
        
        elif self.state == MapInteractiveState.EDIT_TOKENS:
            for token in self.tokens:
                token.handle_event(message, self.transform)


    def mouse_in_world(self, mouse_in_win: Vector2) -> Vector2:
        mouse_in_world = (Vector2(mouse_in_win) - self.transform.pos) / self.transform.scale
        return mouse_in_world

    def set_map_image(self, image_path) -> None:
        self.map.set_map_image(image_path)

    def step(self) -> None:
        for entity in self.entities:
            entity.step()

    def draw(self, win: pygame.Surface) -> None:
        for entity in self.entities:
            entity.draw(win, self.transform)