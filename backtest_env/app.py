import os
from contextlib import asynccontextmanager
from multiprocessing import Process

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backtest_env.constants import DATA_DIR
from backtest_env.dto import Args, BacktestConfig
from backtest_env.strategies import STRATEGIES
from backtest_env.utils import extract_metadata_in_batch
from backtest_env.websocket_manager import WebsocketManager

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
            message = await websocket.receive_text()
            await websocket_manager.broadcast(message)
        except WebSocketDisconnect:
            websocket_manager.disconnect(websocket)


@app.post("/backtest")
def backtest(config: BacktestConfig):
    for strategy in config.strategies:
        backtest_process = Process(target=start, args=(strategy, config.generalConfig))
        backtest_process.start()

        processes.append(backtest_process)

    return {"msg": "OK"}


def start(strategy: tuple, general_config: Args):
    strategy_name, strategy_params = strategy
    # merge two dictionaries
    args = {**strategy_params, **general_config.model_dump()}

    strategy = STRATEGIES[strategy_name].from_cfg(args)
    strategy.run()


async def clean_resources():
    for process in processes:
        process.join()
