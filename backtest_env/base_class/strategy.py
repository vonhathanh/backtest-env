import time
from enum import Enum
from typing import TypeVar, Type
from abc import ABC, abstractmethod

from socketio import Client

from backtest_env.constants import SOCKETIO_URL
from backtest_env.dto import Args
from backtest_env.order_manager import OrderManager
from backtest_env.position_manager import PositionManager
from backtest_env.price import PriceDataSet
from backtest_env.logger import logger

T = TypeVar("T", bound="Strategy")


class State(Enum):
    READY = (1,)
    PROCESSING = 2


class Strategy(ABC):
    # base class for all strategies
    def __init__(self, args: Args):
        self.symbol = args.symbol
        self.socketio: Client = None
        self.init_socketio(args)
        self.data = PriceDataSet(
            args.symbol, args.timeframe, args.startTime, args.endTime, self.socketio
        )
        self.position_manager = PositionManager(args.initialBalance, self.socketio)
        self.order_manager = OrderManager(
            self.position_manager, self.data, self.socketio, args.symbol
        )
        self.state = State.READY

    def init_socketio(self, args: Args):
        if not args.allowLiveUpdates:
            return
        self.socketio = Client()
        self.socketio.connect(SOCKETIO_URL)
        self.socketio.on("next", self.next)

    def run(self):
        # main event loop: getting new candle stick and then process data based on update() logic
        # child class must override update() to specify their own trading logic
        while self.data.step():
            self.update() if self.data.next() else self.cleanup()

    def run_with_live_updates(self):
        # manually emit the first `ready` event using data.step() because FE needs BE to go first
        self.socketio.emit("ready", {})
        # waits for all data to be consumed by `render_finished` event
        while self.data.next():
            time.sleep(1)

    def next(self, data):
        if self.state != State.READY:
            return
        self.state = State.PROCESSING
        self.process()
        self.state = State.READY

    def process(self):
        self.data.step()
        if self.data.next():
            self.update()
            self.position_manager.emit_pnl(self.data.get_close_price())
            self.socketio.emit("ready", {})
        else:
            self.cleanup()

    @abstractmethod
    def update(self):
        # validate account's state: orders, positions,...
        # inspect new input data: prices, indicators,... from other sources
        # determine the next action: submit buy/sell order, cancel orders, close positions, ...
        pass

    def cleanup(self):
        self.clean_resources()
        self.report()
        time.sleep(1)  # small sleep so FE can receive all remain events before disconnection
        self.socketio.disconnect() if self.socketio else None

    def clean_resources(self):
        self.order_manager.cancel_all_orders()
        self.order_manager.close_all_positions(self.data.get_current_price())
        self.position_manager.emit_pnl(0.0)

    def report(self):
        logger.info(f"Backtest finished, pnl: {self.position_manager.get_pnl(0.0)}")

    @classmethod
    def from_cfg(cls: Type[T], kwargs):
        # Factory method design pattern, each subclass of Strategy decide the kwargs they want to initialize
        # read TrendFollower from_cfg() for example
        args = Args(**kwargs)
        return cls(args)

    @classmethod
    def get_required_params(cls: Type[T]) -> dict:
        # similar to from_cfg(), subclass might have other required params, and they can specify them here
        return {}
