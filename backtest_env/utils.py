import json


def load_params(config_file_path: str):
    with open(config_file_path, "r") as f:
        configs = json.load(f)
        print(configs)
    return configs


def load_data(symbols: list[str], timeframes: list[str]):
    assert len(symbols) == len(timeframes)