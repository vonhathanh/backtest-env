import multiprocessing
from multiprocessing import Process

from backtest_env.agent import Agent
from backtest_env.utils import load_params

if __name__ == '__main__':
    multiprocessing.freeze_support()

    # each agent can have different params config
    # should an agent tests multiple symbols in single config? No
    # we can create multiple copies of that agent for testing with different symbols and tf
    # ideally they can run in parallel, each agent has one process
    params = load_params("../../configs.json")

    agents = []
    for agent_config in params["agents"]:
        agents.append(Agent(agent_config))

    processes = []
    for i in range(len(agents)):
        p = Process(target=agents[i].run)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()