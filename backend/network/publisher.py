from typing import Optional, Dict, Any
import asyncio
import websockets as ws
from queue import Queue, Empty as QueueEmpty
from pygame.event import Event as PyGameEvent
from backend.models import Message


class Publisher:
    def __init__(self) -> None:
        self._message_queue: Queue[Message] = Queue()
        self._uri: str = "ws://localhost:8000/ws/publisher"
        self._stop_event: asyncio.Event = asyncio.Event()

    def publish(
        self, event: PyGameEvent, extra: Optional[Dict[str, Any]] = None
    ) -> None:
        message = Message(event=event, extra=extra)
        self._message_queue.put_nowait(message)

    async def _send_message(
        self, websocket: ws.WebSocketClientProtocol, message: Message
    ) -> None:
        try:
            await websocket.send(message.model_dump_json())
        except Exception as e:
            print(f"Error while publishing message: {message}\n{e}")

    async def _consume_messages(self, websocket: ws.WebSocketClientProtocol) -> None:
        while not self._stop_event.is_set():
            try:
                message = self._message_queue.get_nowait()
            except QueueEmpty:
                await asyncio.sleep(0.01)
                continue

            await self._send_message(websocket, message)
            self._message_queue.task_done()

    async def run(self) -> None:
        try:
            async with ws.connect(self._uri) as websocket:
                await self._consume_messages(websocket)
        except Exception as e:
            print(f"Error while connecting to server: {e}")

    def start(self) -> None:
        asyncio.run(self.run())

    def stop(self) -> None:
        self._stop_event.set()
        try:
            while self._message_queue.get_nowait():
                self._message_queue.task_done()
        except QueueEmpty:
            pass
