import json
from abc import ABC
from json import JSONDecodeError

from websockets import ConnectionClosed, ConcurrencyError
from websockets.sync.client import connect, ClientConnection

from backtest_env.constants import WEBSOCKET_URL
from backtest_env.dto import Args
from backtest_env.logger import logger
from backtest_env.strategies.strategy import Strategy


class WebsocketStrategy(Strategy, ABC):
    # base class for all strategies that maintains a websocket connection with client to stream trading progress

    def __init__(self, args: Args):
        super().__init__(args)
        # client_id in websocket communication
        self.client_id = self.__class__.__name__
        self.websocket: ClientConnection = connect(WEBSOCKET_URL)

    def run(self):
        while self.data.step():
            self.process_client_messages()
            self.emit(self.data.get_current_price().to_json())
            self.update()
        logger.info("Backtest finished")

    def process_client_messages(self):
        while True:
            try:
                # ignore all other messages except "render_finished"
                message = json.loads(self.websocket.recv(1))
                if message["message"] == "render_finished":
                    return
            except (ConnectionClosed, ConcurrencyError, JSONDecodeError, TypeError, TimeoutError) as e:
                logger.error(f"process client message error: {e}")
                return

    def emit(self, message: dict, event_type: str = "new_candle"):
        self.websocket.send(json.dumps({
            "type": event_type,
            "message": message,
            "client_id": self.client_id
        }))
