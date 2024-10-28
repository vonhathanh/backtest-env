from backtest_env.order_dispatcher import OrderDispatcher
from backtest_env.env import Env
from backtest_env.strategies.strategy import Strategy


class Agent:
    # in reality, agent will receive data through websocket + API call
    # we'll simulate websocket event using a queue, API call by a middleware (OrderDispatcher)
    def __init__(self, env: Env, params: dict):
        self.env = env
        # env load the requested data from agent params
        self.env.load_data(params["symbols"], params["timeframes"])
        # register agent to the env
        self.env.add_agent(self)
        # init agent's strategy
        self.strategy = Strategy(params["strategy"])
        # agent also has a queue to process event from the engine
        self.queue = None

    def run(self):
        # collect new information from the environment and send them to the strategy
        # data can be candlestick prices, agent's order history...
        while self.step():
            # process events based on new data
            self.process_events()
            # strategy will determine whether there is a trading opportunity or not
            orders = self.strategy.run(**kwargs)
            # validate the orders in agent's perspective
            # orders might conflict with it current positions
            orders = self.validate_orders(orders)
            # submit orders using the dispatcher
            OrderDispatcher.dispatch(orders)

    def report(self):
        pass

    def get_data(self) -> object:
        return None