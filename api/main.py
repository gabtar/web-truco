import uuid
import json

from typing import List, TypedDict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from models import Hand

app = FastAPI()

"""
Ideas/Notas
Primero usar todo con objectos en memoria para probar el front
Averiguar lo de broadcaster, pero esta en alpha por ahora.

En el conection manager debería guardar el player id y el el websocket


El game manager maneja la partida actual
- Reparte cartas
- Acepta jugadas, etc
"""


class OnlinePlayer(TypedDict):
    id: str
    socket: WebSocket
    name: str

    def __init_(self, id, socket):
        self.id = id
        self.socket = socket
        self.name = f"User#{len(manager.active_connections)}"


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        player_id = str(uuid.uuid4())
        self.active_connections[player_id] = websocket
        # Send the id to the player to identify the connection on recieve?
        await websocket.send_text(json.dumps({"event": "connect", "player_id": player_id}))

    def disconnect(self, websocket: WebSocket):
        player_id = None
        for id, socket in self.active_connections.items():
            if socket == websocket:
                player_id = id
        del self.active_connections[player_id]

    async def send(self, json: str, websocket: WebSocket):
        await websocket.send_text(json)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)



# TODO, normalizar los eventos en back y front por nombres/acciones

class GameManager:
    # This may be a repository or something via DI
    hand_list: List[Hand] = []

    def __init__(self, connection_manager):
        self.connection_manager = connection_manager

    def deal_cards(self, hand_id: int):
        # repartir

        # enviar por el conection manager a todos los usuarios
        pass

    def play_card(self, hand_id: int, player_id: str, card_id: int):
        # jugar carta en juego

        # actualizar tablero en usuarios
        pass

    async def join_hand(self, hand_id: int, player_id: str):
        # TODO, Validar que haya lugar
        # y aniadir al jugador al juego
        self.hand_list[hand_id].players.append(player_id)
        # Send the hand id:
        message = json.dumps({"event": "joinHand", "hand_id": hand_id})
         
        # await self.connection_manager.send(message)

    async def new_hand(self, player_id: str):
        self.hand_list.append(Hand())
        await self.join_hand(len(self.hand_list) - 1, player_id)
        # TODO, update games list, to all or rest of the players?
        games_update = json.dumps({"event": "gamesUpdate", "total_games": len(self.hand_list)})
        await self.connection_manager.broadcast(games_update)


manager = ConnectionManager()
game_manager = GameManager(manager)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    # TODO, Una vez connectado enviarle un update de las partidas en juego
    try:
        while True:
            data = await websocket.receive_json()
            print(f"Received message: {data}")
            print("Total connected users: ", len(manager.active_connections))

            if data['event'] == 'createNewGame':
                await game_manager.new_hand(data['player_id'])
                print(game_manager.hand_list)
                # Crea la partida y actualiza el listado de partidas

            elif data['event'] == 'message':
                message = json.dumps({"event": "message", "message": data['message']})
                await manager.broadcast(message)

    except WebSocketDisconnect:
        # TODO end the game, set a winner
        manager.disconnect(websocket)
        print(" User disconected")


"""
Socket Json messages:
    {
            "event" : ""
            "playerId" : ""
            // Rest of the parameters
            // Each event has specific parameters
    }

ServerEvents
join_hand: hand_id
create_hand:


PlayerEvents
join_hand
create_hand

"""
