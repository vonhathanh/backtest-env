import os
from contextlib import asynccontextmanager
from multiprocessing import Process

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backtest_env.constants import DATA_DIR
from backtest_env.dto import Args
from backtest_env.strategies import STRATEGIES
from backtest_env.utils import extract_metadata_in_batch
from backtest_env.websocket_manager import WebsocketManager
from backtest_env.logger import logger

websocket_manager = WebsocketManager()

processes: list[Process] = []

origins = ["http://localhost:5173"]

@asynccontextmanager
async def lifespan(application: FastAPI):
    os.makedirs(DATA_DIR, exist_ok=True)
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
    return await extract_metadata_in_batch(filenames)


@app.websocket("/ws")
async def websocket_connected(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    while True:
        try:
            await handle_websocket(websocket)
        except WebSocketDisconnect as e:
            logger.info(f"ws disconnected: reason: {e}")
            break
    websocket_manager.disconnect(websocket)


async def handle_websocket(websocket: WebSocket):
    message = await websocket.receive_json()
    if message.get("type", "") == "backtest":
        backtest(message["params"])
    else:
        await websocket_manager.broadcast(message)


def backtest(args: dict):
    backtest_process = Process(target=start, args=(args,))
    backtest_process.start()

    processes.append(backtest_process)

    return {"msg": "OK"}


def start(args: Args):
    strategy = STRATEGIES[args["strategy"]].from_cfg(args)
    strategy.run()


async def clean_resources():
    for process in processes:
        process.join()
