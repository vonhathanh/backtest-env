import json

with open("configs.json", "r") as f:
    config = json.load(f)

# order sides
BUY = "BUY"
SELL = "SELL"

# position side
LONG = "LONG"
SHORT = "SHORT"

DATA_DIR = config["data_dir"]