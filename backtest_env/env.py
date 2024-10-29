from multiprocessing import shared_memory
from backtest_env.agent import Agent

import numpy as np


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
        # shared_data is a mapping from symbol_tf to SharedMemory object
        self.shared_data = {}

    def run(self):
        # create a pool of worker processes and start agent's main loop
        with Pool(processes=len(self.agents)) as pool:
            for i in range(len(self.agents)):
                pool.map(self.agents[i].run, ())

    def load_data(self, params: dict):
        symbols, timeframes, starts, ends = params["symbols"], params["timeframes"], params["starts"], params["ends"]
        assert len(symbols) == len(timeframes) == len(starts) == len(ends)

        for symbol, tf, start, end in zip(symbols, timeframes, starts, ends):
            shm_id = "_".join([symbol, tf, start, end])
            if shm_id in self.shared_data:
                continue
            data = np.random.randn(100, 4)
            data_size = data.size * data.itemsize
            shm = shared_memory.SharedMemory(create=True, size=data_size)
            self.shared_data[shm_id] = (shm, data_size)


    def add_agent(self, agent: Agent):
        self.agents.append(agent)

    def process_events(self):
        pass
