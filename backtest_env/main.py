from backtest_env.agent import Agent
from backtest_env.env import Env
from backtest_env.utils import load_params


def main():
    env = Env()
    # each agent can have different params config
    # should an agent tests multiple symbols in single config? No
    # we can create multiple copies of that agent for testing with different symbols and tf
    # ideally they can run in parallel, each agent has one process
    params = load_params("../configs.json")
    for agent_config in params["agents"]:
        Agent(env, agent_config)

    env.run()


if __name__ == '__main__':
    main()