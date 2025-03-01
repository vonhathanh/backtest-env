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
            self.update()
            self.emit_system_states()
        self.cleanup()
        self.report()

    def process_client_messages(self):
        while True:
            try:
                # ignore all other messages except "render_finished"
                message = json.loads(self.websocket.recv(1))
                if message["message"] == "frontend_updated":
                    return
            except (ConnectionClosed, ConcurrencyError, JSONDecodeError, TypeError, TimeoutError) as e:
                logger.error(f"process client message error: {e}")
                return

    def emit_system_states(self):
        price = self.data.get_current_price()
        long, short = self.position_manager.get_positions()
        orders = self.order_manager.get_all_orders()
        order_history = self.order_manager.get_order_history()

        message = json.dumps({
            "type": "update",
            "message": {
                "price": price.json(),
                "positions": [long.json(), short.json()],
                "orders": [order.json() for order in orders],
                "orderHistory": [order.json() for order in order_history]
            },
            "client_id": self.client_id
        })

        self.websocket.send(message)
