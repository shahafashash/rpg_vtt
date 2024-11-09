from typing import Optional
import asyncio
import websockets as ws
from queue import Queue, Empty as QueueEmpty
from backend.models import Message


class Subscriber:
    def __init__(self) -> None:
        self._message_queue: Queue[Message] = Queue()
        self._uri: str = "ws://localhost:8000/ws/subscriber"
        self._stop_event: asyncio.Event = asyncio.Event()

    def get(self) -> Optional[Message]:
        try:
            return self._message_queue.get_nowait()
        except QueueEmpty:
            return None

    async def _consume_messages(self, websocket: ws.WebSocketClientProtocol) -> None:
        while not self._stop_event.is_set():
            try:
                message_str = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                message = Message.model_validate_json(message_str)
                self._message_queue.put_nowait(message)
            except asyncio.TimeoutError:
                pass
            except ws.exceptions.ConnectionClosed:
                break

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
        if not self._message_queue.empty():
            try:
                while self._message_queue.get_nowait():
                    self._message_queue.task_done()
            except QueueEmpty:
                pass
