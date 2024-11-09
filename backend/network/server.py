from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from backend.network.broker import MessageBroker


server = FastAPI()
server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

broker = MessageBroker()


@server.websocket("/ws/subscriber")
async def websocket_subscribe(websocket: WebSocket) -> None:
    await websocket.accept()
    await broker.register(websocket)

    try:
        while True:
            # holding the connection open
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        await broker.unregister(websocket)


@server.websocket("/ws/publisher")
async def websocket_publish(websocket: WebSocket) -> None:
    await websocket.accept()

    try:
        await broker.assign_publisher(websocket)
    except Exception as e:
        return await websocket.send_text(str(e))

    try:
        while True:
            message = await websocket.receive_text()
            await broker.publish(message)
    except WebSocketDisconnect:
        pass
