from multiprocessing import Process, Queue
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket

from backtest_env.dto import BacktestParam
from backtest_env.strategies import STRATEGIES

event_queue = Queue()

ws_clients: set[WebSocket] = set()

processes: list[Process] = []

@asynccontextmanager
async def lifespan(application: FastAPI):
    yield
    # Clean up resources on shutdown, must run after "yield" due to "asynccontextmanager" decorator
    for client in ws_clients:
        await client.close()
    for process in processes:
        process.join()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def index():
    return {"msg": "OK"}

@app.get("/strategies")
def index():
    return {"data": list(STRATEGIES.keys())}

@app.websocket("/ws")
async def websocket_connected(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"msg": "hello websocket"})

    ws_clients.add(websocket)

@app.post("/backtest")
def backtest(params: BacktestParam):
    for strategy in params.strategies:
        backtest_process = Process(target=start, args=(strategy, params))
        backtest_process.start()

        processes.append(backtest_process)

    return {"msg": "OK"}


def start(args: BacktestParam, strategy_id: str):
    strategy = STRATEGIES[strategy_id].from_cfg(args)
    strategy.run()


async def send_message_to_websocket_client():
    event = event_queue.get()
    for client in ws_clients.copy():
        try:
            await client.send_text(event)
        except:
            ws_clients.remove(client)
