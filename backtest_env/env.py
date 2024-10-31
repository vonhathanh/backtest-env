from multiprocessing import shared_memory, Pool
from backtest_env.agent import Agent
from backtest_env.constants import DATA_DIR
import numpy as np

from backtest_env.utils import load_data


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
                _, data_size = self.shared_data[self.agents[i].shm_id]
                pool.map(self.agents[i].run, (data_size,))

        # free resources
        for k, v in self.shared_data.items():
            shm, _ = self.shared_data[k]
            shm.close()
            shm.unlink()

    def load_data(self, params: dict):
        # create shared memory of price data for agents
        symbol, tf, start, end = params["symbol"], params["tf"], params["start"], params["end"]

        shm_id = "_".join([symbol, tf, str(start), str(end)])

        if shm_id not in self.shared_data:
            data = load_data(DATA_DIR, symbol, tf, start, end)
            shm = shared_memory.SharedMemory(create=True, size=data.size * data.itemsize, name=shm_id)
            # copy the original data into shared memory
            shared_data = np.ndarray(data.shape, dtype=data.dtype, buffer=shm.buf)
            shared_data[:] = data
            # store a reference to shm to release it when we are finished
            self.shared_data[shm_id] = (shm, data.shape)

        return shm_id


    def add_agent(self, agent: Agent):
        self.agents.append(agent)

    def process_events(self):
        pass
