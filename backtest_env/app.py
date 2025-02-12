import os
from contextlib import asynccontextmanager
from multiprocessing import Process, Queue

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from backtest_env.constants import DATA_DIR
from backtest_env.dto import BacktestParam
from backtest_env.strategies import STRATEGIES
from backtest_env.utils import extract_metadata_in_batch

event_queue = Queue()

ws_clients: set[WebSocket] = set()

processes: list[Process] = []

origins = ["http://localhost:5173"]


@asynccontextmanager
async def lifespan(application: FastAPI):
    yield
    # run after "yield" due to "asynccontextmanager" decorator
    await clean_resources()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)


@app.get("/")
def index():
    return {"msg": "OK"}


@app.get("/strategies")
def get_strategies():
    strategies = []
    for strategy in STRATEGIES:
        strategies.append({"name": strategy, "params": STRATEGIES[strategy].get_required_params()})
    return strategies


@app.get("/files/metadata")
async def get_files_metadata():
    filenames = os.listdir(DATA_DIR)
    metadata = await extract_metadata_in_batch(filenames)
    return metadata


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


def start(strategy_id: str, args: BacktestParam):
    strategy = STRATEGIES[strategy_id].from_cfg(args)
    strategy.run()


async def send_message_to_websocket_client():
    event = event_queue.get()
    for client in ws_clients.copy():
        try:
            await client.send_text(event)
        except:
            ws_clients.remove(client)


async def clean_resources():
    for client in ws_clients:
        await client.close()
    for process in processes:
        process.join()
