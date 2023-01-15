import uuid
import json

from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from models.models import Hand


app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket):
        """ Adds a new websocket connection """
        await websocket.accept()
        player_id = str(uuid.uuid4())
        self.active_connections[player_id] = websocket
        await websocket.send_text(json.dumps({"event": "connect", "playerId": player_id}))

    def disconnect(self, websocket: WebSocket):
        """ Removes a websocket connection """
        player_id = None
        for id, socket in self.active_connections.items():
            if socket == websocket:
                player_id = id
        del self.active_connections[player_id]

    async def send(self, json_string: str, player_id: str):
        """ Sends a json string to a single websocket user """
        await self.active_connections[player_id].send_text(json_string)

    async def broadcast(self, json_string: str):
        """ Sends a json string all connected users """
        for connection in self.active_connections.values():
            await connection.send_text(json_string)


class HandManager:
    """ Manages hands of Truco """
    hand_list: List[Hand] = []

    def __init__(self, connection_manager):
        self.connection_manager = connection_manager

    async def deal_cards(self, hand_id: int):
        """ Deals cards for all players for an specific game/hand_id """
        hand_to_deal = None
        for hand in self.hand_list:
            if hand.hand_id == hand_id:
                hand_to_deal = hand

        hand_to_deal.deal_cards()

        for player in hand_to_deal.players:
            cards_list = [card.to_json() for card in hand_to_deal.cards_dealed[player]]
            message = json.dumps({"event": "receiveDealedCards", "cards": cards_list})
            await self.connection_manager.send(json_string=message,player_id=player)

    def play_card(self, hand_id: int, player_id: str, card_id: int):
        """ Performs a card play on a game """
        # jugar carta en juego
        # actualizar tablero en usuarios
        pass

    async def games_update(self):
        """ Updates the games list to all players connected in WebSocket """
        current_games = [game.to_json() for game in self.hand_list]
        games_update = json.dumps({"event": "gamesUpdate", "currentGames": current_games})
        await self.connection_manager.broadcast(games_update)

    async def join_hand(self, hand_id: int, player_id: str):
        """ Joins to an specific hand """
        # TODO, Validar que haya lugar y aniadir al jugador al juego
        self.hand_list[hand_id].players.append(player_id)
        # Send the hand id:
        message = json.dumps({"event": "joinedHand", "handId": hand_id})
        await self.connection_manager.send(json_string=message, player_id=player_id)

    async def new_hand(self, player_id: str) -> int:
        """ Creates a new hand/game """
        # TODO, validate user is not currently playing a game
        hand_id = len(self.hand_list)
        self.hand_list.append(Hand(hand_id=hand_id))
        return hand_id


manager = ConnectionManager()

# TODO, ojo, por ahora acá porque necesisto persistir las partidas en algún lado
game_manager = HandManager(manager)


@app.websocket("/ws")
# TODO, verificar si puedo pasarle el connection manager por DI, ver en la documentacion de fastapi -> Depends
# async def websocket_endpoint(websocket: WebSocket, manager: ConnectionManager = Depends(ConnectionManager)):
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    # TODO, Una vez connectado enviarle un update de las partidas en juego
    try:
        while True:
            # TODO, buscar algun tipo de routeo segun el tipo de evento
            # Una especie de controlador de WebSocket, ej
            # -> socketController.execute(action=data['event'], payload=data['payload'])
            data = await websocket.receive_json()
            print(f"Received message: {data}")
            print("Total connected users: ", len(manager.active_connections))

            if data['event'] == 'createNewGame':
                # Crea la partida, agrega al jugador, y actualiza lista de partidas
                new_hand_id = await game_manager.new_hand(data['playerId'])
                await game_manager.join_hand(player_id=data['playerId'], hand_id=new_hand_id)
                await game_manager.games_update()
            elif data['event'] == 'joinGame':
                await game_manager.join_hand(hand_id=int(data['handId']), player_id=data['playerId'])
                # Actualiza la lista por si alguna mano se llenó de jugadores
                await game_manager.games_update()
            elif data['event'] == 'dealCards':
                # Busco la mano asociada al id de usuario
                # Y reparto las cartas
                await game_manager.deal_cards(hand_id=int(data['handId']))
            elif data['event'] == 'message':
                message = json.dumps({"event": "message", "message": data['message']})
                await manager.broadcast(message)

    except WebSocketDisconnect:
        # TODO end the game, set a winner if user was playing a game
        manager.disconnect(websocket)
        print(" User disconected")


"""
# TODO, ver como documentar mejor
GAMES / WEBSOCKET EVENTS:
(Naming convenion used for json: camelCase)

Server -> Client events:

- "event" : "gamesUpdate" -> updates the online games list
--------------------------------------------------------------
 Data sent: "totalGames" : int (Later will be a games_id to join)
--------------------------------------------------------------

- "event" : "joinedHand" -> the user succesfully joined a hand
--------------------------------------------------------------
 Data sent: "hand_id" : int
--------------------------------------------------------------

- "event" : "receiveDealedCards" -> sends the cards to the player
--------------------------------------------------------------
 Data sent: "cards" : Array of cards
--------------------------------------------------------------



Client -> Server events:

- "event" : "createNewGame" -> the user succesfully creates a hand
--------------------------------------------------------------
 Data sent: "playerId" : int
 Response: event -> joinedHand
--------------------------------------------------------------

- "event" : "joinGame" -> the user joins an available game
--------------------------------------------------------------
 Data sent: "playerId" : int, "hand_id" : int
--------------------------------------------------------------

- "event" : "dealCards" -> the user deals the cards in the the current game
--------------------------------------------------------------
 Data sent: "playerId" : int
            "handId" : int
--------------------------------------------------------------

- "event" : "message" -> the user sends a global message
--------------------------------------------------------------
 Data sent: "message" : str
--------------------------------------------------------------



"""
