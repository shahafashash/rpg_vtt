from typing import List
import os
from random import choice

import pygame
from pygame.math import Vector2

from common import MapInteractiveState, GridType
from drawing_utils import draw_grid_hex, draw_grid_square
from token_manager import Token, TokenCollection


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


class MapManager:
    def __init__(self):
        self.map_surf_initial: pygame.Surface = None
        self.map_surf: pygame.Surface = None
        self.pos: Vector2 = Vector2(0, 0)
        self.scale: float = 1.0

        self.state = MapInteractiveState.EDIT_MAP
        self.is_dragging = False
        self.mouse_to_map: Vector2 = Vector2(0, 0)

        self.grid = Grid()
        self.token_collection = TokenCollection()
        self.last_event = None

    def set_map_image(self, path: str) -> None:
        self.map_surf_initial = pygame.image.load(path)
        self.update_map()

    def cycle_state(self) -> None:
        members = list(MapInteractiveState)
        next_index = (members.index(self.state) + 1) % len(members)
        self.state = members[next_index]

    def update_map(self) -> None:
        self.map_surf = pygame.transform.smoothscale_by(
            self.map_surf_initial, self.scale
        )

    def add_token(self, file: str, pos: List[int]) -> None:
        pos = Vector2(pos)
        self.token_collection.add_token(file, pos)

    def switch_interactive_state(self) -> None:
        if self.state == MapInteractiveState.EDIT_MAP:
            if self.token_collection.is_token_selected():
                self.state = MapInteractiveState.EDIT_TOKENS

        elif self.state == MapInteractiveState.EDIT_TOKENS:
            if not self.token_collection.is_token_selected():
                self.state = MapInteractiveState.EDIT_MAP

    def handle_event(self, event) -> None:
        self.last_event = event
        if self.state == MapInteractiveState.NONE:
            return

        self.switch_interactive_state()

        if self.state == MapInteractiveState.EDIT_MAP:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in (4, 5):
                    scale_value = 1.1 if event.button == 4 else 0.9
                    mouse_pos = Vector2(event.pos)
                    mouse_to_map = (self.pos - mouse_pos) * scale_value

                    self.pos = mouse_pos + mouse_to_map
                    self.token_collection.scale_from(scale_value, mouse_pos)

                    self.scale *= scale_value
                    self.grid.scale(scale_value)

                    self.update_map()

                if event.button == 1:
                    self.is_dragging = True
                    self.mouse_to_map = self.pos - Vector2(event.pos)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_dragging = False

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

        if self.state == MapInteractiveState.EDIT_TOKENS:
            self.token_collection.handle_event(event)

    def step(self) -> None:
        if self.state == MapInteractiveState.EDIT_MAP:
            if self.is_dragging:
                mouse_pos = Vector2(self.last_event.pos)
                old_pos = self.pos
                self.pos = mouse_pos + self.mouse_to_map
                pos_vector = self.pos - old_pos
                self.token_collection.translate(pos_vector)

        if self.state == MapInteractiveState.EDIT_GRID:
            if self.is_dragging:
                mouse_pos = Vector2(self.last_event.pos)
                self.grid.pos = mouse_pos + self.mouse_to_map

        self.token_collection.step()

    def draw(self, win: pygame.Surface) -> None:
        if self.map_surf:
            win.blit(self.map_surf, self.pos)
            self.grid.draw(win, self.pos)
            self.token_collection.draw(win)


if __name__ == "__main__":
    pygame.init()

    fps = 60
    fpsClock = pygame.time.Clock()

    width, height = 1280, 720
    win = pygame.display.set_mode((width, height))

    map_manager = MapManager()
    maps = os.listdir(r"./yuvalPdf/pics")
    map_manager.set_map_image(os.path.join(r"./yuvalPdf/pics", choice(maps)))

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
                map_manager.add_token(file, Vector2(event.pos))

            map_manager.handle_event(event)

        # step
        map_manager.step()

        # draw
        map_manager.draw(win)

        pygame.display.flip()
        fpsClock.tick(fps)

    pygame.quit()
