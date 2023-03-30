import json

from fastapi import WebSocket
from services.player_manager import PlayerManager
from repositories.repository import dep_players_repository


class ConnectionManager:
    """ Handles real time connections via websockets """
    active_connections: dict[str, WebSocket] = {}
    player_service: PlayerManager = PlayerManager(dep_players_repository())

    async def connect(self, websocket: WebSocket) -> str:
        """ Adds a new websocket connection """
        await websocket.accept()
        player = self.player_service.create()
        self.active_connections[player.id] = websocket
        await websocket.send_text(
                json.dumps({"event": "connect",
                            "payload": {
                                "player": {"id": player.id, "name": player.name}
                                }
                            })
            )
        return player.id

    def disconnect(self, websocket: WebSocket):
        """ Removes a websocket connection """
        player_id = None
        for id, socket in self.active_connections.items():
            if socket == websocket:
                player_id = id
        self.player_service.remove_player(player_id=player_id)
        del self.active_connections[player_id]

    async def send(self, json_string: str, player_id: str):
        """ Sends a json string to a single websocket user """
        await self.active_connections[player_id].send_text(json_string)

    async def broadcast(self, json_string: str):
        """ Sends a json string all connected users """
        for connection in self.active_connections.values():
            await connection.send_text(json_string)


manager = ConnectionManager()


def dep_connection_manager():
    return manager
