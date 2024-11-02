from typing import Tuple
import multiprocess as mp
from threading import Thread
import math
import time
import os
import pygame as pg
from pygame.event import Event as PyGameEvent
from screeninfo import get_monitors
from event_queue import PublisherEventQueue, SubscriberEventQueue, EventQueue
from publisher import Publisher
from subscriber import Subscriber
from models import Message
from settings import SettingsManager, GameSettings
import custom_events as CustomPyGameEvents


from map_manager import MapManager


class GameLogic(mp.Process):
    def __init__(self, name: str, message_queue: EventQueue) -> None:
        super().__init__()

        self._name: str = name
        self._message_queue: EventQueue = message_queue
        self._stop_event: mp.synchronize.Event = mp.Event()
        self._win: pg.Surface = None
        self._clock: pg.time.Clock = None

        self._settings: GameSettings = None
        self._map_manager: MapManager = None

    def _initialize_window(self, title: str) -> pg.Surface:
        resolution_settings = self._settings.resolution

        if resolution_settings.fullscreen:
            window = pg.display.set_mode((0, 0), pg.FULLSCREEN, 0, 0)
        else:
            window_size = (resolution_settings.width, resolution_settings.height)
            window = pg.display.set_mode(window_size, pg.RESIZABLE, 0, 0)

        pg.display.set_caption(title)
        return window

    def _initialize(self) -> None:

        settings_manager = SettingsManager()
        self._settings: GameSettings = settings_manager.settings
        self._clock = pg.time.Clock()
        self._map_manager = MapManager()
        self._win = self._initialize_window(self._name)
        pg.init()


    def _finalize(self) -> None:
        pg.quit()

    def _pre_message_handle_hook(self, message: Message) -> None:
        pass

    def _post_message_handle_hook(self, message: Message) -> None:
        pass

    def _handle_message(self, message: Message) -> None:
        event = message.event
        extra = message.extra

        if event.type == pg.QUIT:
            self._stop_event.set()
        elif event.type == CustomPyGameEvents.CHANGE_MAP_SPECIFIC:
            self._map_manager.set_map_image(f'maps/{extra["map"]}')
        elif event.type == CustomPyGameEvents.MAP_CYCLE_STATE:
            self._map_manager.cycle_state()
        elif event.type == CustomPyGameEvents.ADD_TOKEN:
            self._map_manager.add_token(extra["file"], extra["pos"])

        self._map_manager.handle_event(event)

    def _handle_messages(self, messages: list[Message]) -> None:
        for message in messages:
            self._pre_message_handle_hook(message)
            self._handle_message(message)
            self._post_message_handle_hook(message)

    def run(self) -> None:
        self._initialize()
        while not self._stop_event.is_set():
            messages = self._message_queue.get()
            self._handle_messages(messages)

            self._map_manager.step()
            self._map_manager.draw(self._win)

            pg.display.update()
            self._clock.tick(60)

        self._finalize()


class PublisherGameLogic(GameLogic):
    def __init__(self) -> None:
        super().__init__("DM Screen", PublisherEventQueue())
        self._publisher: Publisher = Publisher()
        self._publisher_thread: Thread = Thread(
            target=self._publisher.start, daemon=True
        )

    def _initialize(self) -> None:
        super()._initialize()
        self._publisher_thread.start()

        # DEMO
        event = PyGameEvent(CustomPyGameEvents.CHANGE_MAP_SPECIFIC)
        extra = {"map": "image_31.jfif"}
        self._publisher.publish(event, extra)
        self._map_manager.set_map_image(f'maps/{extra["map"]}')

    def _finalize(self) -> None:
        self._publisher.stop()
        self._publisher_thread.join()
        super()._finalize()

    def _pre_message_handle_hook(self, message):
        # if message.event.type == CustomPyGameEvents.CIRCLE_INTERACT:
        #     self._publisher.publish(message.event)
        self._publisher.publish(message.event, message.extra)
        if message.event.type == pg.QUIT:
            time.sleep(0.1)


class SubscriberGameLogic(GameLogic):
    def __init__(self) -> None:
        subscriber = Subscriber()
        super().__init__("Players Screen", SubscriberEventQueue(subscriber))
        self._subscriber: Subscriber = subscriber
        self._subscriber_thread: Thread = Thread(target=self._subscriber.start)

    def _initialize(self) -> None:
        monitors = get_monitors()
        if len(monitors) > 1:
            monitor = monitors[1]
            position = (monitor.x, monitor.y)
        else:
            position = (0, 0)

        os.environ['SDL_VIDEO_WINDOW_POS'] = f'{position[0]},{position[1]}'

        super()._initialize()
        self._subscriber_thread.start()

    def _finalize(self) -> None:
        self._subscriber.stop()
        self._subscriber_thread.join()

        super()._finalize()
