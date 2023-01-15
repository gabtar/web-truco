import uuid
import json
import random

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends

from models.models import Player, Hand, PlayerCard


app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket):
        """ Adds a new websocket connection """
        await websocket.accept()
        player = Player().save()
        self.active_connections[player.id] = websocket
        await websocket.send_text(json.dumps({"event": "connect", "playerId": player.id}))

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

    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager

    async def deal_cards(self, hand_id: int):
        """ Deals cards for all players for an specific game/hand_id """
        hand = Hand.get_current_players(hand_id=hand_id)
        players = Hand.get_current_players(hand_id=hand_id)
        # Select N random cards
        card_ids = random.sample(range(1, 41), len(players) * 3) 
        current_card = 0

        for player in players:
            cards_dealed = []
            for i in range(3):
                cards_dealed.append(PlayerCard(player_id=player.id, card_id=card_ids[current_card]).save())
                current_card += 1

            cards_list = [card.dict(include={'rank', 'suit'}) for card in cards_dealed]
            message = json.dumps({"event": "receiveDealedCards", "cards": cards_list})
            await self.connection_manager.send(json_string=message,player_id=player.id)


    def play_card(self, hand_id: int, player_id: str, card_id: int):
        """ Performs a card play on a game """
        # jugar carta en juego
        # actualizar tablero en usuarios
        pass

    async def games_update(self):
        """ Updates the games list to all players connected in WebSocket """
        # Debería ser get_avaliables_games() -> sólo aquellos que tienen lugares disponibles
        games_list = Hand.get_all()
        current_games = [game.dict(include={'id', 'name'}) for game in games_list]
        games_update = json.dumps({"event": "gamesUpdate", "currentGames": current_games})
        # current_games = [game.to_json() for game in self.hand_list]
        # games_update = json.dumps({"event": "gamesUpdate", "currentGames": current_games})
        await self.connection_manager.broadcast(games_update)

    async def join_hand(self, hand_id: int, player_id: str):
        """ Joins to an specific hand """
        # TODO, Validar que haya lugar y aniadir al jugador al juego
        player = Player.get_by_id(id=player_id)

        # if player.playing_hand is not None:
        #     raise Exception

        player.playing_hand = hand_id
        player.update()

        message = json.dumps({"event": "joinedHand", "handId": hand_id})
        print(message)
        await self.connection_manager.send(json_string=message, player_id=player_id)

    async def new_hand(self, player_id: str) -> int:
        """ Creates a new hand/game """
        # TODO, validate user is not currently playing a game
        player = Player.get_by_id(id=player_id)
        hand = Hand(id=len(Hand.get_all())+1).save()

        return hand.id


manager = ConnectionManager()


@app.websocket("/ws")
# TODO, verificar si puedo pasarle el connection manager por DI, ver en la documentacion de fastapi -> Depends
# async def websocket_endpoint(websocket: WebSocket, manager: ConnectionManager = Depends(ConnectionManager)):
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    # TODO, Una vez connectado enviarle un update de las partidas en juego
    try:
        while True:
            game_manager = HandManager(manager)
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
