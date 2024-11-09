from typing import List
import pygame as pg
from backend.models import Message
from backend.network.subscriber import Subscriber
from backend.event_queues.base import EventQueue


class SubscriberEventQueue(EventQueue):
    def __init__(self, subscriber: Subscriber) -> None:
        self._subscriber: Subscriber = subscriber

    def get(self) -> List[Message]:
        _ = pg.event.get()
        events = []
        while event := self._subscriber.get():
            events.append(event)

        return events