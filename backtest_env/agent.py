import time
from multiprocessing import shared_memory

import numpy as np

from backtest_env.order_dispatcher import OrderDispatcher
from backtest_env.strategies import STRATEGIES


class Agent:
    # in reality, agent will receive data through websocket + API call
    # we'll simulate websocket event using a queue, API call by a middleware (OrderDispatcher)
    def __init__(self, env, params: dict):
        self.name = params["name"]

        env.add_agent(self)
        # load the requested data from agent params and store the shared_memory id for future access
        self.shm_id = env.load_data(params)

        self.data = None
        # init agent's strategy
        self.strategy = STRATEGIES[params["strategy"]]
        # agent also has a queue to process event from the engine
        self.queue = None

    def run(self, shape):
        shm = shared_memory.SharedMemory(name=self.shm_id)
        self.data = np.ndarray(shape, dtype=np.float64, buffer=shm.buf)

        print(f"{self.name} is running")

        # collect new information from the environment and send them to the strategy
        # data can be candlestick prices, agent's order history...
        while self.step():
            # process events based on new data
            self.process_events()
            # strategy will determine whether there is a trading opportunity or not
            orders = self.strategy.run(None)
            # validate the orders in agent's perspective
            # orders might conflict with it current positions
            orders = self.validate_orders(orders)
            # submit orders using the dispatcher
            OrderDispatcher.dispatch(orders)

        shm.close()

        print(f"{self.name} has finished back-testing")

    def report(self):
        pass

    def get_data(self) -> object:
        return None

    def step(self):
        return False