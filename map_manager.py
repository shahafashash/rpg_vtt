from typing import List
import os
from random import choice

import pygame
from pygame.math import Vector2

from common import MapInteractiveState, GridType
from drawing_utils import draw_grid_hex, draw_grid_square
# from token_collection import TokenCollection, Token
from canvas import Canvas, IMapEntity

from menu_gui import Gui, ImageToggle, StackPanel, HORIZONTAL


class Grid:
    def __init__(self):
        self.pos = Vector2()
        self.grid_type = GridType.SQUARE
        self.size = 50

    def draw(self, win: pygame.Surface, pos: Vector2):
        if self.grid_type == GridType.SQUARE:
            draw_grid_square(win, pos + self.pos, self.size)

    def scale(self, value: float) -> None:
        self.size *= value






class MapManager(IMapEntity):
    def __init__(self, canvas: Canvas):
        self.canvas: Canvas = canvas
        self.map_surf_initial: pygame.Surface = None
        self.map_surf: pygame.Surface = None
        # self.pos: Vector2 = Vector2(0, 0)
        # self.scale: float = 1.0

        self.state = MapInteractiveState.EDIT_WORLD
        self.is_dragging = False
        self.mouse_to_map: Vector2 = Vector2(0, 0)

        self.grid = Grid()
        self.token_collection = TokenCollection()

    def set_map_image(self, path: str) -> None:
        self.map_surf_initial = pygame.image.load(path)
        self.update_map()

    def cycle_state(self) -> None:
        members = list(MapInteractiveState)
        next_index = (members.index(self.state) + 1) % len(members)
        self.state = members[next_index]
    
    def set_state(self, state: MapInteractiveState):
        self.state = state

    def update_map(self) -> None:
        self.map_surf = pygame.transform.smoothscale_by(
            self.map_surf_initial, self.canvas.scale
        )

    def add_token(self, file: str, pos: List[int]) -> None:
        pos = Vector2(pos)
        self.token_collection.add_token(file, pos)

    def switch_interactive_state(self) -> None:
        if self.state == MapInteractiveState.EDIT_WORLD:
            if self.token_collection.is_token_selected():
                self.state = MapInteractiveState.EDIT_TOKENS

        elif self.state == MapInteractiveState.EDIT_TOKENS:
            if not self.token_collection.is_token_selected():
                self.state = MapInteractiveState.EDIT_WORLD

    def handle_event(self, event) -> None:
        if self.state == MapInteractiveState.NONE:
            return

        if event.type == pygame.MOUSEMOTION:
            # check if there is a selected token and if there is, set the state to token edit
            is_selected_token = self.token_collection.check_for_selected_token(Vector2(event.pos))
            if is_selected_token:
                self.state = MapInteractiveState.EDIT_TOKENS

        self.switch_interactive_state()

        # todo: similar code for edit map and edit grid
        if self.state == MapInteractiveState.EDIT_WORLD:
            self.canvas.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                pass
                # if event.button in (4, 5):
                #     scale_value = 1.1 if event.button == 4 else 0.9
                #     mouse_pos = Vector2(event.pos)
                #     mouse_to_map = (self.pos - mouse_pos) * scale_value

                #     self.pos = mouse_pos + mouse_to_map
                #     self.token_collection.scale_from(scale_value, mouse_pos)

                #     self.scale *= scale_value
                #     self.grid.scale(scale_value)

                #     self.update_map()

                # if event.button == 1:
                #     self.is_dragging = True
                #     self.mouse_to_map = self.pos - Vector2(event.pos)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_dragging = False
            
            if event.type == pygame.MOUSEMOTION:
                if self.is_dragging:
                    mouse_pos = Vector2(event.pos)
                    old_pos = self.pos
                    self.pos = mouse_pos + self.mouse_to_map
                    pos_vector = self.pos - old_pos
                    self.token_collection.translate(pos_vector)

        if self.state == MapInteractiveState.EDIT_GRID:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in [4, 5]:
                    scale_value = 1.1 if event.button == 4 else 0.9
                    mouse_pos = Vector2(event.pos)
                    mouse_to_pos = (self.grid.pos - mouse_pos) * scale_value
                    self.grid.pos = mouse_pos + mouse_to_pos

                    self.grid.scale(scale_value)

                if event.button == 1:
                    self.is_dragging = True
                    self.mouse_to_map = self.grid.pos - Vector2(event.pos)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_dragging = False
            
            if event.type == pygame.MOUSEMOTION:
                if self.is_dragging:
                    mouse_pos = Vector2(event.pos)
                    self.grid.pos = mouse_pos + self.mouse_to_map

        if self.state == MapInteractiveState.EDIT_TOKENS:
            self.token_collection.handle_event(event)

    def step(self) -> None:
        # self.token_collection.step()
        pass

    def draw(self, canvas: Canvas) -> None:
        if self.map_surf:
            canvas.win.blit(self.map_surf, self.canvas.cam)
            # self.grid.draw(canvas.win, self.pos)
            # self.token_collection.draw(canvas.win)

def handel_gui_events(gui: Gui, map_manager: MapManager):
    # todo: this should be simplified

    event, _ = gui.listen()
    if event == 'map_tool':
        map_manager.set_state(MapInteractiveState.EDIT_WORLD)
        gui.get_element_by_key('grid_tool').set_value(False)
        gui.get_element_by_key('token_tool').set_value(False)
    
    elif event == 'grid_tool':
        map_manager.set_state(MapInteractiveState.EDIT_GRID)
        gui.get_element_by_key('map_tool').set_value(False)
        gui.get_element_by_key('token_tool').set_value(False)

    elif event == 'token_tool':
        map_manager.set_state(MapInteractiveState.EDIT_TOKENS)
        gui.get_element_by_key('map_tool').set_value(False)
        gui.get_element_by_key('grid_tool').set_value(False)
    
    elif map_manager.state == MapInteractiveState.EDIT_WORLD:
        gui.get_element_by_key('map_tool').set_value(True)
        gui.get_element_by_key('grid_tool').set_value(False)
        gui.get_element_by_key('token_tool').set_value(False)
    
    elif map_manager.state == MapInteractiveState.EDIT_TOKENS:
        gui.get_element_by_key('map_tool').set_value(False)
        gui.get_element_by_key('grid_tool').set_value(False)
        gui.get_element_by_key('token_tool').set_value(True)
    

if __name__ == "__main__":
    pygame.init()

    fps = 60
    fpsClock = pygame.time.Clock()

    width, height = 1280, 720
    win = pygame.display.set_mode((width, height))

    canvas = Canvas(win)

    map_manager = MapManager(canvas)
    maps = os.listdir(r"./assets/yuvalPdf/pics")
    map_manager.set_map_image(os.path.join(r"./assets/yuvalPdf/pics", choice(maps)))

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
                    map_manager.cycle_state()

            if event.type == pygame.DROPFILE:
                file = event.file
                map_manager.add_token(file, pygame.mouse.get_pos())

            gui.handle_pygame_event(event)
            map_manager.handle_event(event)

        # step
        map_manager.step()
        gui.step()
        handel_gui_events(gui, map_manager)
        

        # draw
        map_manager.draw(canvas)
        gui.draw(win)

        pygame.display.flip()
        fpsClock.tick(fps)

    pygame.quit()
