from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from broker import MessageBroker


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

broker = MessageBroker()


@app.websocket("/ws/subscriber")
async def websocket_subscribe(websocket: WebSocket) -> None:
    await websocket.accept()
    await broker.register(websocket)

    try:
        while True:
            # holding the connection open
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        await broker.unregister(websocket)


@app.websocket("/ws/publisher")
async def websocket_publish(websocket: WebSocket) -> None:
    await websocket.accept()

    try:
        while True:
            message = await websocket.receive_text()
            await broker.publish(message)
    except WebSocketDisconnect:
        pass
