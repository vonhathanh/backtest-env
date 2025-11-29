import os

from huggingface_hub import snapshot_download

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
# to seed data, we'll just simply download prepared-data from cloud storage to local repository
# this script will never validate/ensure the correctness of the data it downloaded. That's another script's job
snapshot_download("hanhvn/binance-data-collection", repo_type="dataset", local_dir=DATA_DIR)
# remove all unneccessary files
os.remove(os.path.join(DATA_DIR, ".cache"))
os.remove(os.path.join(DATA_DIR, ".gitattributes"))