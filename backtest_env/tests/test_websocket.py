from fastapi.testclient import TestClient

from backtest_env.app import app


def test_websocket():
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()
        assert data == {"msg": "hello websocket"}
