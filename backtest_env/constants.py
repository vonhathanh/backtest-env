import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "../configs.json")

with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

# order sides
BUY = "BUY"
SELL = "SELL"

# position side
LONG = "LONG"
SHORT = "SHORT"

DATA_DIR = os.path.join(BASE_DIR, "..", "data")
WEBSOCKET_URL = config["websocket_uri"]
