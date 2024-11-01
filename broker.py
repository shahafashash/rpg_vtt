from typing import Set
from queue import Queue, Empty as QueueEmpty
import asyncio
from fastapi import WebSocket


class MessageBroker:
    def __init__(self) -> None:
        self._subscribers: Set[WebSocket] = set()
        self._message_queue: Queue[str] = Queue()

    async def register(self, websocket: WebSocket) -> None:
        self._subscribers.add(websocket)

    async def unregister(self, websocket: WebSocket) -> None:
        self._subscribers.remove(websocket)

    async def publish(self, message: str) -> None:
        if self._subscribers:
            try:
                while queued_message := self._message_queue.get_nowait():
                    await asyncio.wait(
                        [ws.send_text(queued_message) for ws in self._subscribers]
                    )
            except QueueEmpty:
                pass

            await asyncio.wait([ws.send_text(message) for ws in self._subscribers])
        else:
            self._message_queue.put_nowait(message)
