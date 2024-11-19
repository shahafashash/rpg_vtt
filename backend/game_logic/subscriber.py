from threading import Thread
import os
from screeninfo import get_monitors
from backend.network.subscriber import Subscriber
from backend.event_queues import SubscriberEventQueue
from backend.game_logic import GameLogic
from backend.settings.settings import SettingsManager, GameSettings

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
            monitor = monitors[0]
            position = (0, 0)

        settings = SettingsManager().settings
        width = settings.resolution.width
        height = settings.resolution.height
        position = (position[0] + (monitor.width // 2) - (width // 2),
                    position[1] + (monitor.height // 2) - (height // 2))

        os.environ['SDL_VIDEO_WINDOW_POS'] = f'{position[0]},{position[1]}'
        print(position)

        super()._initialize()
        self._subscriber_thread.start()

    def _finalize(self) -> None:
        self._subscriber.stop()
        self._subscriber_thread.join()

        super()._finalize()
