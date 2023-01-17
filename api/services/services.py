import json
import random

from fastapi import WebSocket, Depends
from models.models import Player, Hand, PlayerCard


class Singleton(type):
    """ Metaclass for generating singletons """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ConnectionManager:
    """ Handles real time connections via websockets """
    __metaclass__ = Singleton

    # TODO, pasarle un PlayerService/Manager para agregar/eliminar jugadores de la db
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

    def __init__(self, connection_manager: ConnectionManager = Depends(ConnectionManager)):
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
