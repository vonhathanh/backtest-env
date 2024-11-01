from multiprocessing import shared_memory

import numpy as np

from backtest_env.backend import Backend
from backtest_env.order_dispatcher import OrderDispatcher
from backtest_env.strategies import STRATEGIES


class Agent(Backend):
    # in reality, Agent will receive data through websocket + API call
    # we'll simulate websocket event using a queue, API call by a middleware (OrderDispatcher)
    def __init__(self, env, params: dict):
        self.name = params["name"]

        self.balance = params["init_balance"]

        env.add_agent(self)
        # load the requested data from agent's params and store the shared_memory id for future access
        self.shm_id = env.load_data(params)
        # data will be inited by env
        self.data = None
        # init agent's strategy
        self.strategy = STRATEGIES[params["strategy"]].from_cfg(params)
        # agent also has a queue to process event from the engine
        self.queue = None

        self.cur_idx = -1

    def run(self, shape):
        shm = shared_memory.SharedMemory(name=self.shm_id)
        self.data = np.ndarray(shape, dtype=np.float64, buffer=shm.buf)

        print(f"{self.name} is running")

        # collect new information from the environment and send them to the strategy
        # data can be candlestick prices, agent's order history...
        while self.step():
            # process events based on new data, check if an order can be filled/stopped, update pnl
            self.process_events()
            # strategy will determine whether there is a trading opportunity or not
            orders = self.strategy.run(self)
            print(f"{orders=}")
            # validate the orders in agent's perspective
            # orders might conflict with it current positions
            # we assign this task to Agent because we want Strategy to have single responsibility: create orders,
            # Strategy can also access to current orders/positions, it depends on strategy's logics
            # ideally, we want a stateless Strategy so it can be used in other modules
            orders = self.validate_orders(orders)
            # submit orders using the dispatcher
            OrderDispatcher.dispatch(orders)

        shm.close()

        print(f"{self.name} has finished back-testing")

    def report(self):
        # report the backtest progress, statistic, and might even plot the results
        pass

    def step(self) -> bool:
        self.cur_idx += 1
        return self.cur_idx >= len(self.data)

    def process_events(self):
        pass