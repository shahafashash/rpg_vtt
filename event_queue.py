from typing import List
from abc import ABC, abstractmethod
import pygame as pg
from pygame.event import Event as PyGameEvent
from models import Message
from subscriber import Subscriber
import custom_events as CustomPyGameEvents


class EventQueue(ABC):
    @abstractmethod
    def get(self) -> List[str]:
        pass


class PublisherEventQueue(EventQueue):
    def __init__(self) -> None:
        self._event_queue: pg.event = pg.event

    def get(self) -> List[Message]:
        events = self._event_queue.get()
        messages = []
        for event in events:
            extra = None
            # This is a hacky way to mask events for both the publisher and the subscriber
            if event.type == pg.KEYDOWN and event.key == pg.K_TAB:
                event = PyGameEvent(CustomPyGameEvents.MAP_CYCLE_STATE)
            elif event.type == pg.DROPFILE:
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


class SubscriberEventQueue(EventQueue):
    def __init__(self, subscriber: Subscriber) -> None:
        self._subscriber: Subscriber = subscriber

    def get(self) -> List[Message]:
        _ = pg.event.get()
        events = []
        while event := self._subscriber.get():
            events.append(event)

        return events
