from backtest_env.agent import Agent
from backtest_env.env import Env


def main():
    env = Env()

    # each agent can have different params config
    # ideally they can run in parallel, each agent has one process
    params = load_params()
    agent_1 = Agent(env, params1)
    agent_2 = Agent(env, params2)
    agent_3 = Agent(env, params3)

    env.run()

    env.report()


if __name__ == '__main__':
    main()