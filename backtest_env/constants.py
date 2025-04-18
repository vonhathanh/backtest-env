import json
import os
from typing import Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "../configs.json")

with open(CONFIG_PATH, "r") as f:
    config: dict[str, Any] = json.load(f)

DATA_DIR = os.path.join(BASE_DIR, "..", "data")
SOCKETIO_URL = str(config["socketio_url"])
ORDER_SIZE = int(config["order_size"])
