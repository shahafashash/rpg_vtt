from typing import List
import pygame as pg
from pygame.event import Event as PyGameEvent
from backend.models import Message
from backend.event_queues.base import EventQueue
import backend.custom_events as CustomPyGameEvents


class PublisherEventQueue(EventQueue):
    def __init__(self) -> None:
        self._event_queue: pg.event = pg.event

    def get(self) -> List[Message]:
        events = self._event_queue.get()
        messages = []
        for event in events:
            extra = None
            # This is a hacky way to mask events for both the publisher and the subscriber
            if event.type == pg.DROPFILE:
                extra = {"file": event.file, "pos": pg.mouse.get_pos()}
                event = PyGameEvent(CustomPyGameEvents.ADD_TOKEN)
            elif event.type == pg.MOUSEBUTTONDOWN:
                extra = {"pos": pg.mouse.get_pos()}
                if event.button == 1:
                    event = PyGameEvent(CustomPyGameEvents.LEFT_MOUSE_CLICK_DOWN)
                elif event.button == 2:
                    event = PyGameEvent(CustomPyGameEvents.MIDDLE_MOUSE_CLICK_DOWN)
                elif event.button == 3:
                    event = PyGameEvent(CustomPyGameEvents.RIGHT_MOUSE_CLICK_DOWN)
                elif event.button == 4:
                    event = PyGameEvent(CustomPyGameEvents.WHEEL_PRESS_UP)
                elif event.button == 5:
                    event = PyGameEvent(CustomPyGameEvents.WHEEL_PRESS_DOWN)

            elif event.type == pg.MOUSEBUTTONUP:
                extra = {"pos": pg.mouse.get_pos()}
                if event.button == 1:
                    event = PyGameEvent(CustomPyGameEvents.LEFT_MOUSE_CLICK_UP)
                elif event.button == 2:
                    event = PyGameEvent(CustomPyGameEvents.MIDDLE_MOUSE_CLICK_UP)
                elif event.button == 3:
                    event = PyGameEvent(CustomPyGameEvents.RIGHT_MOUSE_CLICK_UP)
                elif event.button == 4:
                    event = PyGameEvent(CustomPyGameEvents.WHEEL_RELEASE_UP)
                elif event.button == 5:
                    event = PyGameEvent(CustomPyGameEvents.WHEEL_RELEASE_DOWN)

            messages.append(Message(event=event, extra=extra))

        return messages