from typing import List
import os
from random import choice

import pygame
from pygame.math import Vector2

from common import MapInteractiveState, GridType
from drawing_utils import draw_grid_hex, draw_grid_square
import backend.custom_events as CustomPyGameEvents
from backend.models import Message

from menu_gui import Gui, ImageToggle, StackPanel, HORIZONTAL
from dataclasses import dataclass

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

        self.is_dragging = False
        self.mouse_world_to_self = Vector2()

    def handle_event(self, message: Message, transformations: Transformation):
        event = message.event
        extra = message.extra

        if self.selected:
            # drag
            if self.draggable:
                if event.type == CustomPyGameEvents.LEFT_MOUSE_CLICK_DOWN:
                    self.is_dragging = True
                    mouse_in_world = (Vector2(extra['pos']) - transformations.pos) / transformations.scale
                    self.mouse_world_to_self = self.pos - mouse_in_world

                if event.type == CustomPyGameEvents.LEFT_MOUSE_CLICK_UP:
                    self.is_dragging = False

                if event.type == pygame.MOUSEMOTION and self.is_dragging:
                    mouse_in_world = (Vector2(extra['pos']) - transformations.pos) / transformations.scale
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

    def on_canvas_scale_update(self, transform: Transformation) -> None:
        ...
    
    def step(self) -> None:
        ...

    def draw(self, win: pygame.Surface, transform: Transformation) -> None:
        ...




class Map(MapEntity):
    def __init__(self):
        self.surf_initial: pygame.Surface = None
        self.surf: pygame.Surface = None

    def set_map_image(self, path: str):
        self.surf_initial = pygame.image.load(path)
        self.surf = self.surf_initial

    def on_canvas_scale_update(self, transform: Transformation) -> None:
        super().on_canvas_scale_update(transform)
        self.surf = pygame.transform.smoothscale_by(self.surf_initial, transform.scale)

    def draw(self, win: pygame.Surface, transform: Transformation) -> None:
        if self.surf is None:
            return
        win.blit(self.surf, transform.pos)



class Grid(MapEntity):
    def __init__(self):
        super().__init__()
        self.grid_type = GridType.SQUARE
        self.initial_size = 50.0
        self.size = self.initial_size

        self.selectable = True
        self.draggable = True
        self.scaleable = True

    def on_canvas_scale_update(self, transform: Transformation) -> None:
        super().on_canvas_scale_update(transform)
        self.size = self.initial_size * transform.scale * self.scale

    def update_scale(self):
        super().update_scale()
        self.size = self.initial_size * self.canvas.scale * self.scale

    def check_if_selected(self, mouse_pos: Vector2) -> None:
        self.selected = True

    def draw(self, win: pygame.Surface) -> None:
        pos = self.canvas.cam + self.pos * self.canvas.scale
        if self.grid_type == GridType.SQUARE:
            draw_grid_square(win, pos, self.size)



class Token(MapEntity):
    def __init__(self, pos: Vector2, image_path: str):
        super().__init__()
        self.pos = pos

        self.surf_initial: pygame.Surface = pygame.image.load(image_path)
        self.surf: pygame.Surface = self.surf_initial

        self.selectable = True
        self.scaleable = True
        self.draggable = True

    def on_canvas_scale_update(self, transform) -> None:
        super().on_canvas_scale_update(transform)
        self.surf = pygame.transform.smoothscale_by(self.surf_initial, self.scale * transform.scale)

    def update_scale(self) -> None:
        super().update_scale()
        self.surf = pygame.transform.smoothscale_by(self.surf_initial, self.scale * canvas.scale)

    def check_if_selected(self, mouse_pos: Vector2) -> None:
        self.selected = False
        pos = self.canvas.cam + self.pos * self.canvas.scale
        if pos.distance_to(mouse_pos) < self.surf.get_size()[0] / 2:
            self.selected = True

    def draw(self, win: pygame.Surface) -> None:
        pos = self.canvas.cam + self.pos * self.canvas.scale
        win.blit(self.surf, pos - Vector2(self.surf.get_size()) / 2)
        if self.selected:
            pygame.draw.circle(win, (255, 255, 255), pos, self.surf.get_size()[0] // 2, 1)


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


if __name__ == "__main__":
    pygame.init()

    fps = 60
    fpsClock = pygame.time.Clock()

    width, height = 1280, 720
    win = pygame.display.set_mode((width, height))

    canvas = Canvas()
    state = MapInteractiveState.EDIT_WORLD

    map = Map(canvas)
    canvas.register_map_entity(map)
    maps = os.listdir(r"./assets/yuvalPdf/pics")
    map.set_map_image(os.path.join(r"./assets/yuvalPdf/pics", choice(maps)))

    grid = Grid(canvas)
    canvas.register_map_entity(grid)

    tokens: List[Token] = []

    # create menu
    icons_path = r'assets/icons.png'
    icons_surf = pygame.image.load(icons_path).convert_alpha()
    icons = [pygame.Surface((64, 64), pygame.SRCALPHA) for i in range(3)]
    [icon.blit(icons_surf, (0, 0), (i * 64, 0, 64, 64)) for i, icon in enumerate(icons)]

    gui = Gui()
    tool_bar_menu = StackPanel(orientation=HORIZONTAL, size=Vector2(64 * 3, 64), pos=Vector2(width // 2 - (3 * 64) // 2, height - 64))
    tool_bar_menu.insert(ImageToggle(key='map_tool', value=True, surf=icons[0], generate_event=True))
    tool_bar_menu.insert(ImageToggle(key='grid_tool', surf=icons[1], generate_event=True))
    tool_bar_menu.insert(ImageToggle(key='token_tool', surf=icons[2], generate_event=True))
    gui.insert(tool_bar_menu)

    done = False
    while not done:
        win.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    pass
                    # map_manager.cycle_state()

            if event.type == pygame.DROPFILE:
                file = event.file
                pos = canvas.mouse_in_world(pygame.mouse.get_pos())

                new_token = Token(canvas, pos, file)
                canvas.register_map_entity(new_token)
                tokens.append(new_token)

                # map_manager.add_token(file, pygame.mouse.get_pos())

            if state == MapInteractiveState.EDIT_WORLD:
                canvas.handle_event(event)
            elif state == MapInteractiveState.EDIT_TOKENS:
                for token in tokens:
                    token.handle_event(event)
            elif state == MapInteractiveState.EDIT_GRID:
                grid.handle_event(event)

            gui.handle_pygame_event(event)

        # step
        gui.step()
        state = handel_gui_events(gui, state)


        # draw
        map.draw(win)
        grid.draw(win)
        for token in tokens:
            token.draw(win)

        gui.draw(win)

        pygame.display.flip()
        fpsClock.tick(fps)

    pygame.quit()
