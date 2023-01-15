from api.main import app
from fastapi.testclient import TestClient


def test_websocket():
    # client = TestClient(app)
    # # app.dependency_overrides[] -> hay que mockearle el depends del connection manager
    # with client.websocket_connect("/ws") as websocket:
    #     data = websocket.receive_json()
    #     assert data == {"event": "connect", "playerId": "uuid"}  
    pass
