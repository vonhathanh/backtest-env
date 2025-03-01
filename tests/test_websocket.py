from fastapi.testclient import TestClient

from backtest_env.app import app

HELLO_MSG = {"msg": "hello websocket"}

def test_receive_json():
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        websocket.send_json(HELLO_MSG)
        data = websocket.receive_json()
        assert data == HELLO_MSG
