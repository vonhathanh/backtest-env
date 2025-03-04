import json
from json import JSONDecodeError

from websockets import ConnectionClosed, ConcurrencyError
from websockets.sync.client import connect, ClientConnection

from backtest_env.constants import WEBSOCKET_URL
from backtest_env.logger import logger


class WebsocketClient:
    def __init__(self, client_id: str, timeout: float = 1.0):
        # client_id in websocket communication
        self.client_id = client_id
        self.timeout = timeout
        self.websocket: ClientConnection = connect(WEBSOCKET_URL)

    def process_client_messages(self):
        while True:
            try:
                # ignore all other messages except "render_finished"
                message = json.loads(self.websocket.recv(self.timeout))
                if message["message"] == "frontend_updated":
                    return
            except (
                ConnectionClosed,
                ConcurrencyError,
                JSONDecodeError,
                TypeError,
                TimeoutError,
            ) as e:
                logger.error(f"process client message error: {e}")
                return

    def emit(self, data: dict):
        message = json.dumps(
            {
                "type": "update",
                "message": data,
                "client_id": self.client_id,
            }
        )
        self.websocket.send(message)
