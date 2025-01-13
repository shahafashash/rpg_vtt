
from itertools import count

import pygame
from pygame.event import Event as PyGameEvent
from pygame.math import Vector2

from backend.models import Message
import backend.custom_events as CustomPyGameEvents
from menu_gui import Gui, ImageToggle, StackPanel, HORIZONTAL, RadioConatiner, Button
from map_entities import Token
from canvas import Canvas

counter = count(start=1, step=1)
EVENT_NONE = counter.__next__()
EVENT_REMOVE_TOKEN = counter.__next__()


class CanvasGui(Gui):
    def __init__(self, canvas: Canvas, size: tuple[int, int]):
        super().__init__()
        self.canvas = canvas

        icons_path = r'assets/icons.png'
        icons_surf = pygame.image.load(icons_path)
        icons = [pygame.Surface((64, 64), pygame.SRCALPHA) for i in range(3)]
        [icon.blit(icons_surf, (0, 0), (i * 64, 0, 64, 64)) for i, icon in enumerate(icons)]

        map_key = Message(event=PyGameEvent(CustomPyGameEvents.CANVAS_SWITCH_MODE_WORLD))
        grid_key = Message(event=PyGameEvent(CustomPyGameEvents.CANVAS_SWITCH_MODE_GRID))
        token_key = Message(event=PyGameEvent(CustomPyGameEvents.CANVAS_SWITCH_MODE_TOKENS))

        tool_bar_menu = RadioConatiner(orientation=HORIZONTAL, size=Vector2(64 * 3, 64), pos=Vector2(size[0] // 2 - (3 * 64) // 2, 0))
        tool_bar_menu.insert(ImageToggle(key=map_key, value=True, surf=icons[0], generate_event=True))
        tool_bar_menu.insert(ImageToggle(key=grid_key, surf=icons[1], generate_event=True))
        tool_bar_menu.insert(ImageToggle(key=token_key, surf=icons[2], generate_event=True))
        self.insert(tool_bar_menu)
    
    def handle_event(self, message) -> None:
        super().handle_event(message)
        token = self.canvas.get_context_menu_token()
        if token is None:
            return
        token.context_menu_opened = False
        self.open_token_context_menu(token)
        
    def open_token_context_menu(self, token: Token) -> None:
        pos = self.canvas.transform.pos + token.pos * self.canvas.transform.scale

        context_menu = StackPanel(pos=pos, size=(200, 300))
        context_menu.insert(Button(key={'type': EVENT_REMOVE_TOKEN, 'token': token}, text='Remove Token'))
        # context_menu.insert(Button(key={'type': EVENT_NONE}, text='button2'))
        # context_menu.insert(Button(key={'type': EVENT_NONE}, text='button3'))
        # context_menu.insert(Button(key={'type': EVENT_NONE}, text='button4'))
        # context_menu.insert(Button(key={'type': EVENT_NONE}, text='button5'))

        self.insert_context_menu(context_menu)


    def step(self) -> None:
        super().step()

        # handle self gui events
        if len(self.event_que) > 0:
            key = self.event_que.pop(0)
            # print(key)

            if isinstance(key, Message):
                self.canvas.insert_event(key)
            
            else:
                if key['type'] == EVENT_REMOVE_TOKEN:
                    self.canvas.remove_token(key['token'])
