import time
from multiprocessing import Process, Queue

from pydantic import BaseModel
from fastapi import FastAPI, WebSocket

event_queue = Queue()

ws_clients: set[WebSocket] = set()

processes: list[Process] = []

app = FastAPI()


class BacktestParam(BaseModel):
    id: int

@app.get("/")
def index():
    return {"msg": "OK"}

@app.on_event("shutdown")
def shutdown():
    for client in ws_clients:
        client.close()

    for process in processes:
        process.join()


@app.websocket("/ws")
async def websocket_connected(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"msg": "hello websocket"})

    ws_clients.add(websocket)

@app.post("/backtest")
def backtest(args: BacktestParam):
    backtest_process = Process(target=f, args=(args, ))
    backtest_process.start()

    processes.append(backtest_process)

    return {"msg": "OK"}


def f(args):
    time.sleep(5)
    print("f completed")

async def send_message_to_websocket_client():
    event = event_queue.get()
    for client in ws_clients.copy():
        try:
            await client.send_text(event)
        except:
            ws_clients.remove(client)
