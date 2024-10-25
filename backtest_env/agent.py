from backtest_env.env import Env
from backtest_env.strategies.strategy import Strategy


class Agent:
    # in reality, agent will receive data through websocket + API call
    # we'll simulate websocket event using a queue, API call by a middleware (OrderDispatcher)
    def __init__(self, env: Env, params: dict):
        self.env = env
        self.env.load_data(params["symbols"], params["timeframes"])
        self.env.add_agent(self)
        self.strategy = Strategy(params["strategy"])

    def run(self):
        # collect new information from the environment and send them to the strategy
        data = self.get_data()
        self.strategy.run(data)

    def report(self):
        pass

    def get_data(self) -> object:
        return None