import pytest
from fastapi.testclient import TestClient

from backtest_env.app import app


def test_receive_json():
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()
        assert data == {"msg": "hello websocket"}

def test_close_websocket():
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as websocket:
            websocket.send_json({"data": "hello world"})