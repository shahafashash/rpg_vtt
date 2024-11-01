from typing import List

import pygame
from pygame import Vector2

NORMAL_SIZE = 100.0


class Token:
    def __init__(self, pos: Vector2):
        self.surf_initial: pygame.Surface = None
        self.surf: pygame.Surface = None
        self.scale: float = 1.0
        self.pos = pos

    def update_surf(self) -> None:
        self.surf = pygame.transform.smoothscale_by(self.surf_initial, self.scale)

    def scale_by(self, value: float) -> None:
        self.scale *= value
        self.update_surf()

    def scale_from(self, value: float, anchor: Vector2) -> None:
        anchor_to_pos = self.pos - anchor
        anchor_to_pos *= value
        self.pos = anchor + anchor_to_pos
        self.scale_by(value)

    def set_image(self, path: str) -> None:
        self.surf_initial = pygame.image.load(path)
        normal_scale_factor = NORMAL_SIZE / self.surf_initial.get_width()
        self.scale = normal_scale_factor
        self.update_surf()

    def set_pos(self, pos: Vector2) -> None:
        self.pos = pos

    def draw(self, win: pygame.Surface) -> None:
        win.blit(self.surf, self.pos - Vector2(self.surf.get_size()) / 2)


class TokenCollection:
    def __init__(self):
        self.tokens: List[Token] = []

        self.selected_token: Token = None
        self.token_dragged = False
        self.drag_offset = Vector2()

        self.last_event = None

    def is_token_selected(self) -> bool:
        return self.selected_token is not None

    def add_token(self, file: str, pos: Vector2) -> None:
        token = Token(pos)
        token.set_image(file)
        self.tokens.append(token)

    def handle_event(self, event) -> None:
        self.last_event = event
        if self.selected_token is None:
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in [4, 5]:
                scale_value = 1.1 if event.button == 4 else 0.9
                self.selected_token.scale_by(scale_value)

            if event.button == 1:
                self.token_dragged = True
                self.drag_offset = self.selected_token.pos - Vector2(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.token_dragged = False

        elif event.type == pygame.MOUSEMOTION:
            self.selected_token = None
            for token in self.tokens:
                if token.pos.distance_to(event.pos) < token.surf.get_width() / 2:
                    self.selected_token = token
                    break

    def translate(self, vec: Vector2) -> None:
        for token in self.tokens:
            token.pos += vec

    def scale_by(self, value: float) -> None:
        for token in self.tokens:
            token.scale_by(value)

    def scale_from(self, value: float, anchor: Vector2) -> None:
        for token in self.tokens:
            token.scale_from(value, anchor)

    def step(self):
        check_for_selection = True
        if self.token_dragged:
            check_for_selection = False

            mouse_pos = Vector2(self.last_event.pos)
            self.selected_token.pos = mouse_pos + self.drag_offset

        # if check_for_selection:
        #     self.selected_token = None
        #     for token in self.tokens:
        #         if (
        #             token.pos.distance_to(self.last_event.pos)
        #             < token.surf.get_width() / 2
        #         ):
        #             self.selected_token = token
        #             break

    def draw(self, win: pygame.Surface) -> None:
        for token in self.tokens:
            token.draw(win)
            if self.selected_token is token:
                pygame.draw.circle(
                    win, (255, 255, 255), token.pos, token.surf.get_width() / 2, 1
                )
