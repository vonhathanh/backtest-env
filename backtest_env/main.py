from backtest_env.agent import Agent
from backtest_env.env import Env
from backtest_env.utils import load_params


def main():
    env = Env()
    # each agent can have different params config
    # ideally they can run in parallel, each agent has one process
    params = load_params("../configs.json")
    for agent_config in params["agents"]:
        agent = Agent(env, agent_config)
        agent.run()


if __name__ == '__main__':
    main()