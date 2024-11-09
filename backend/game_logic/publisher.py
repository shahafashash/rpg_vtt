from threading import Thread
import time
import pygame as pg
from pygame.event import Event as PyGameEvent
from backend.network.publisher import Publisher
from backend.event_queues import PublisherEventQueue
from backend.game_logic import GameLogic
import backend.custom_events as CustomPyGameEvents

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
        self._map.set_map_image(f'assets/maps/{extra["map"]}')

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

    def draw(self) -> None:
        # Add GUI here
        # ...

        super().draw()