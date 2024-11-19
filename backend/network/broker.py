from typing import Set, List
import asyncio
from fastapi import WebSocket


class MessageBroker:
    def __init__(self) -> None:
        self._subscribers: Set[WebSocket] = set()
        self._message_queue: List[str] = []
        self._publisher: WebSocket = None
        self._lock: asyncio.Lock = asyncio.Lock()
        

    async def assign_publisher(self, websocket: WebSocket) -> None:
        if self._publisher:
            raise Exception("Publisher already assigned")
        self._publisher = websocket

    async def register(self, websocket: WebSocket) -> None:
        self._subscribers.add(websocket)

        # need to replace this by just informing the subscriber of the current game state
        # else, the queue will blow up fast...
        
        async with self._lock:
            if self._message_queue:
                await asyncio.gather(*[websocket.send_text(message) for message in self._message_queue])

    async def unregister(self, websocket: WebSocket) -> None:
        self._subscribers.remove(websocket)

    async def publish(self, message: str) -> None:
        async with self._lock:
            self._message_queue.append(message)

        if self._subscribers:
            await asyncio.gather(
                *[ws.send_text(message) for ws in self._subscribers]
            )


