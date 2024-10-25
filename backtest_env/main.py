from backtest_env.agent import Agent
from backtest_env.env import Env


def main():
    env = Env()

    # each agent can have different params config
    agent_1 = Agent(env, params1)
    agent_2 = Agent(env, params2)
    agent_3 = Agent(env, params3)

    env.run()

    agent_1.report()
    agent_2.report()
    agent_3.report()


if __name__ == '__main__':
    main()