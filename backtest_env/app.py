import os
from contextlib import asynccontextmanager
from multiprocessing import Process

import uvicorn
import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backtest_env.constants import DATA_DIR
from backtest_env.strategies import STRATEGIES
from backtest_env.utils import extract_metadata_in_batch
from backtest_env.logger import logger

processes: dict[str, Process] = {}

origins = ["http://localhost:5173", "http://localhost:8000"]


@asynccontextmanager
async def lifespan(application: FastAPI):
    os.makedirs(DATA_DIR, exist_ok=True)
    yield
    for process in processes.values():
        process.join()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

sio = socketio.AsyncServer(cors_allowed_origins=origins, async_mode="asgi")
socketio_app = socketio.ASGIApp(sio, app)


@app.get("/")
def index():
    return {"msg": "OK"}


@app.get("/strategies")
def get_strategies():
    return [
        {"name": strategy, "params": STRATEGIES[strategy].get_required_params()}
        for strategy in STRATEGIES
    ]


@app.get("/files/metadata")
async def get_files_metadata():
    return await extract_metadata_in_batch(os.listdir(DATA_DIR))


@sio.event
def connect(sid, environ, auth):
    logger.info(f"Client: {sid} connected")


@sio.event
def disconnect(sid, reason):
    logger.info(f"Client: {sid} disconnected, reason: {reason}")
    if sid in processes:
        processes[sid].terminate()
        del processes[sid]


@sio.on("backtest")
def backtest(sid, data: dict):
    logger.info(f"Start backtest process {sid} with params: {data}")
    backtest_process = Process(target=start, args=(data,))
    backtest_process.start()

    processes[sid] = backtest_process


@sio.on("*")
async def generic_event_handler(event, sid, data):
    await sio.emit(event, data, skip_sid=sid)


def start(args: dict):
    strategy = STRATEGIES[args["strategy"]].from_cfg(args)
    strategy.run_with_live_updates() if args["allowLiveUpdates"] else strategy.run()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
