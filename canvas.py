
from typing import List

import pygame
from pygame import Vector2


class MapEntity:
    def __init__(self, canvas: 'Canvas'):
        self.pos = Vector2()
        self.scale = 1.0

        self.draggable = False
        self.scaleable = False
        self.selectable = False
        self.selected = False

        self.is_dragging = False
        self.mouse_world_to_self = Vector2()
        self.canvas = canvas
    
    def handle_event(self, event):
        if self.selected:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in (4, 5):
                    scale_value = 1.1 if event.button == 4 else 0.9
                    self.scale *= scale_value
                    self.update_scale()

                if event.button == 1:
                    self.is_dragging = True
                    mouse_in_world = (Vector2(event.pos) - self.canvas.cam) / self.canvas.scale
                    self.mouse_world_to_self = self.pos - mouse_in_world
            
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_dragging = False
        
            if event.type == pygame.MOUSEMOTION:
                if self.is_dragging:
                    mouse_in_world = (Vector2(event.pos) - self.canvas.cam) / self.canvas.scale
                    self.pos = mouse_in_world + self.mouse_world_to_self
        
        if event.type == pygame.MOUSEMOTION:
            if self.selectable:
                    self.check_if_selected(event.pos)

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

        self.is_dragging = False
        self.mouse_to_cam: Vector2 = None
        self.entities: List[MapEntity] = []
    
    def register_map_entity(self, entity: MapEntity) -> None:
        self.entities.append(entity)
    
    def handle_event(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in (4, 5):
                scale_value = 1.1 if event.button == 4 else 0.9
                mouse_pos = Vector2(event.pos)
                mouse_to_cam = (self.cam - mouse_pos) * scale_value

                self.cam = mouse_pos + mouse_to_cam
                self.scale *= scale_value
                for entity in self.entities:
                    entity.update_canvas_scale(self)

            if event.button == 1:
                self.is_dragging = True
                self.mouse_to_cam = self.cam - Vector2(event.pos)
        
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_dragging = False
        
        if event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                mouse_pos = Vector2(event.pos)
                self.cam = mouse_pos + self.mouse_to_cam
        
    def mouse_in_world(self, mouse: Vector2) -> Vector2:
        pos = (mouse - self.cam) / self.scale
        return pos
