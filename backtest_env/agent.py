from multiprocessing import shared_memory

import numpy as np

from backtest_env.backend import Backend
from backtest_env.constants import BUY
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
        # index of current data point, data usually be time-series type
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
            if orders:
                print(f"{orders=}")
                # submit orders using the dispatcher
                OrderDispatcher.dispatch(orders, self)

        shm.close()

        print(f"{self.name} has finished back-testing")

    def report(self):
        # report the backtest progress, statistic, and might even plot the results
        pass

    def step(self) -> bool:
        # moves to the next data point
        self.cur_idx += 1
        return self.cur_idx < len(self.data)

    def process_events(self):
        # call process_order() repeatedly, each process_order() can only handle one order
        # why don't we just use for loop here? I forgot why, dear God please help me to remember
        list(map(self.process_order, list(self.pending_orders.values())))


    def process_order(self, order: dict):
        # process the order in agent's perspective
        # orders might conflict with it current positions
        # we assign this task to Agent because we want Strategy to have single responsibility: create orders,
        # Strategy can also access to current orders/positions, it depends on strategy's logics
        # ideally, we want a stateless Strategy so it can be used in other modules
        if order["type"] == "MARKET":
            self.fill_order(order)
        elif order["type"] == "LIMIT":
            pass
        elif order["type"] == "STOP":
            pass
        elif order["type"] == "TAKE_PROFIT":
            pass
        elif order["type"] == "STOP_MARKET":
            pass
        elif order["type"] == "TAKE_PROFIT_MARKET":
            pass
        elif order["type"] == "TRAILING_STOP_MARKET":
            pass
        else:
            raise ValueError("order type must be: "
                             "MARKET, LIMIT, STOP, TAKE_PROFIT, STOP_MARKET, TAKE_PROFIT_MARKET, TRAILING_STOP_MARKET")

    def get_prices(self, size: int=1) -> np.ndarray:
        size = min(self.cur_idx, size)
        return self.data[self.cur_idx-size:self.cur_idx] if size > 1 else self.data[self.cur_idx]

    def fill_order(self, order: dict):
        price = self.get_prices()[4] if "price" not in order else order["price"]
        # determine the amount cash needed for the order
        required_cash = order["quantity"] * price
        # if not enough cash -> raise an error
        if required_cash > self.balance:
            print(f"{order=} can't be filled, reason, insufficient fund")
        else:
            print(f"order {order['id']} filled")
            self.update_position(order, required_cash)
        del self.pending_orders[order["id"]]

    def update_position(self, order: dict, required_cash: float):
        # open/update position based on order symbol and side
        if order["side"] == BUY:
            self.position.long += order["quantity"]
        else:
            self.position.short += order["quantity"]
        # subtract the amount of cash required for order
        self.balance -= required_cash
        print(f"position: {self.position}, balance: {self.balance}, total asset: {self.get_total_wealth(price)}")
