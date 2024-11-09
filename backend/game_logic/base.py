import multiprocess as mp
import pygame as pg
from backend.event_queues import EventQueue
from backend.models import Message
from backend.settings.settings import SettingsManager, GameSettings
import backend.custom_events as CustomPyGameEvents

from canvas import Canvas
from map_entities import Map


class GameLogic(mp.Process):
    def __init__(self, name: str, message_queue: EventQueue) -> None:
        super().__init__()

        self._name: str = name
        self._message_queue: EventQueue = message_queue
        self._stop_event: mp.synchronize.Event = mp.Event()
        self._win: pg.Surface = None
        self._clock: pg.time.Clock = None

        self._settings: GameSettings = None
        self._canvas: Canvas = None
        self._map: Map = None

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
        self._canvas = Canvas()
        self._map = Map(self._canvas)
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
            self._map.set_map_image(f'assets/maps/{extra["map"]}')
        # elif event.type == CustomPyGameEvents.ADD_TOKEN:
        #     self._map_manager.add_token(extra["file"], extra["pos"])

        self._map.handle_event(message)
        self._canvas.handle_event(message)

    def _handle_messages(self, messages: list[Message]) -> None:
        for message in messages:
            self._pre_message_handle_hook(message)
            self._handle_message(message)
            self._post_message_handle_hook(message)

    def draw(self) -> None:
        self._map.draw(self._win)

    def run(self) -> None:
        self._initialize()
        while not self._stop_event.is_set():
            messages = self._message_queue.get()
            self._handle_messages(messages)

            self._win.fill((0,0,0))
            self.draw()

            pg.display.update()
            self._clock.tick(60)

        self._finalize()