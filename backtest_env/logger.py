import logging
import sys

logger = logging.getLogger("backtest_env")
logger.propagate = False

formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s")

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)

logger.handlers = [stream_handler]

logger.setLevel(logging.INFO)