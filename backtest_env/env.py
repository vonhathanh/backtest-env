from backtest_env.agent import Agent


class Env:
    def __init__(self):
        self.agents = []
        self.queue = None

    def step(self):
        # move forward one candle
        pass

    def set_backtest_range(self, start_time: int, end_time: int = 0):
        pass

    def run(self):
        while True:
            self.step()
            self.process_events()
            for agent in self.agents:
                agent.run()

    def load_data(self, symbols: list[str], timeframes: list[str]):
        assert len(symbols) == len(timeframes)

    def add_agent(self, agent: Agent):
        self.agents.append(agent)

    def process_events(self):
        pass
