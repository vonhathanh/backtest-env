from backtest_env.agent import Agent


class Env:
    def __init__(self):
        # list of active agents
        self.agents = []
        # message queue to process events/requests from agents
        self.queue = None
        # database backend to store order history, positions
        self.db = None

    def step(self) -> bool:
        # moves forward one candle in the predefined time range
        # return None if data is not available
        pass

    def set_backtest_range(self, start_time: int, end_time: int = 0):
        pass

    def run(self):
        while self.step():
            self.process_events()
            for agent in self.agents:
                agent.run()

    def load_data(self, symbols: list[str], timeframes: list[str]):
        assert len(symbols) == len(timeframes)

    def add_agent(self, agent: Agent):
        self.agents.append(agent)

    def process_events(self):
        pass
