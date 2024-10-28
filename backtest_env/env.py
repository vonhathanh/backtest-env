from backtest_env.agent import Agent


class Env:
    # env will serve as centralized data store for all agents
    # agents create copy of data they need and then run idependently
    def __init__(self):
        # list of active agents
        self.agents = []
        # message queue to process events/requests from agents
        self.queue = None
        # database backend to store order history, positions,...
        self.db = None

    def run(self):
        # create a pool of worker processes and start agent's main loop
        with Pool(processes=len(self.agents)) as pool:
            for i in range(len(self.agents)):
                pool.map(self.agents[i].run, ())

    def load_data(self, symbols: list[str], timeframes: list[str]):
        assert len(symbols) == len(timeframes)

    def add_agent(self, agent: Agent):
        self.agents.append(agent)

    def process_events(self):
        pass
