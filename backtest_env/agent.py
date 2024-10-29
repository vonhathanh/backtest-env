import time

from backtest_env.order_dispatcher import OrderDispatcher
from backtest_env.strategies import STRATEGIES
from backtest_env.utils import load_data


class Agent:
    # in reality, agent will receive data through websocket + API call
    # we'll simulate websocket event using a queue, API call by a middleware (OrderDispatcher)
    def __init__(self, env, params: dict):
        self.name = params["name"]
        # load the requested data from agent params
        env.load_data(params)

        self.data = None
        # init agent's strategy
        self.strategy = STRATEGIES[params["strategy"]]
        # agent also has a queue to process event from the engine
        self.queue = None

    def run(self, shm_id: str, data_size):
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
        time.sleep(1)
        print(f"{self.name} is stopped")

    def report(self):
        pass

    def get_data(self) -> object:
        return None

    def step(self):
        return False