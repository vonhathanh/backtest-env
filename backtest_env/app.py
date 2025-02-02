import multiprocessing

from fastapi import FastAPI, WebSocket

event_queue = multiprocessing.Queue()

ws_clients: set[WebSocket] = set()

app = FastAPI()


@app.get("/")
async def index():
    return {"status": "OK"}


@app.websocket("/ws")
async def websocket_connected(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"msg": "hello websocket"})
    ws_clients.add(websocket)


async def send_message_to_websocket_client():
    event = event_queue.get()
    for client in ws_clients.copy():
        try:
            await client.send_text(event)
        except:
            ws_clients.remove(client)
