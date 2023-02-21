import json
from datetime import datetime
from typing import Dict, List
from fastapi.encoders import jsonable_encoder
from models.models import Hand, Player, Score, Card
from services.connection_manager import ConnectionManager, dep_connection_manager
from services.services import (
    HandManager, ScoreManager, PlayerManager, TrucoManager, EnvidoManager
)


class SocketController:
    """ Controls socket events """
    _connection_manager: ConnectionManager
    _hand_manager: HandManager
    _player_manager: PlayerManager
    _score_manager: ScoreManager
    _truco_manager: TrucoManager
    _envido_manager: EnvidoManager

    def __init__(
            self,
            connection_manager: ConnectionManager = dep_connection_manager(),
            hand_manager: HandManager = HandManager(),
            player_manager: PlayerManager = PlayerManager(),
            score_manager: ScoreManager = ScoreManager(),
            truco_manager: TrucoManager = TrucoManager(),
            envido_manager: EnvidoManager = EnvidoManager()
            ):
        self._connection_manager = connection_manager
        self._hand_manager = hand_manager
        self._player_manager = player_manager
        self._score_manager = score_manager
        self._truco_manager = truco_manager
        self._envido_manager = envido_manager

    async def call_event(self, event: str, payload: Dict):
        # Calls the method name by the event string passed as argument
        if hasattr(self, event) and callable(func := getattr(self, event)):
            await func(**payload)
        else:
            raise Exception('Method not exists')

    async def message(self, playerId: str, message: str):
        """ Receives a message from a player and re sends it to all connected users

        Args:
            playerId (str): the id of the player who sent the message.
            message (str): the text of the message sent by the player.
        """
        player: Player = self._player_manager.find_player(player_id=playerId)

        data = json.dumps({
            "event": "message",
            "payload": {"message": {
                "text": message,
                "player": player.name,
                "time": str(datetime.now().strftime("%H:%M:%S"))
                }
            }
        })
        await self._connection_manager.broadcast(json_string=data)

    async def gamesUpdate(self, playerId: str = None):
        """ Sends an update of the current games avaliables in the server.

        If an optional player_id argument is passed it only sends the message
        to socket of that user

        Args:
            playerId (str): the id of the player to send the update status of games.
        """
        games_list = [game.dict(include={'id', 'name', 'players'})
                      for game in self._hand_manager.avaliable_games()]
        for game in games_list:
            game['currentPlayers'] = len(game['players'])
            del game['players']

        message = json.dumps({
                'event': 'gamesUpdate',
                'payload': {'gamesList': games_list}
        })

        if playerId is not None:
            await self._connection_manager.send(json_string=message, player_id=playerId)
        else:
            await self._connection_manager.broadcast(json_string=message)

    async def handUpdate(self, hand_id: int):
        """ Updates the hand status to all players playing the hand

        Args:
            handId (int): the id of the hand
        """
        hand: Hand = self._hand_manager.get_hand(id=hand_id)

        for player in hand.players:
            hand_status = jsonable_encoder(hand)
            # Manda sólo las cartas del jugador corriente
            hand_status['cards_dealed'] = jsonable_encoder(hand.cards_dealed[player.id]) if hand.status != 'NOT_STARTED' else []
            hand_status['winner'] = hand.check_winner

            data = json.dumps({
                "event": "handUpdated",
                "payload": {
                    "hand": hand_status
                    }
                })

            await self._connection_manager.send(json_string=data, player_id=player.id)

    async def joinGame(self, handId: int, playerId: str):
        """ Joins a player to a hand

        Args:
            playerId (str): the id of the player to add to the hand.
            handId (int): the id of the hand to add a new player.
        """
        self._hand_manager.join_hand(hand_id=handId, player_id=playerId)

        await self._connection_manager.send(
                json_string=json.dumps({'event': 'joinedHand'}),
                player_id=playerId
        )
        await self.handUpdate(hand_id=handId)
        await self.gamesUpdate()

    async def createNewGame(self, playerId: str):
        """ Creates a new game

        Args:
            playerId (str): id of the player who creates the hand.
        """
        hand_id = self._hand_manager.new_hand(player_id=playerId)
        # Joins the user to the recently created hand
        await self.joinGame(playerId=playerId, handId=hand_id)

    async def dealCards(self, playerId: str, handId: int):
        """ Deals cards in a hand

        Args:
            playerId (str): id of the player who wants to deal cards.
            handId (int): id of the hand to deal cards.
        """
        self._hand_manager.deal_cards(hand_id=handId, player_id=playerId)
        self._score_manager.initialize_score(hand=self._hand_manager.get_hand(id=handId))

        await self.handUpdate(hand_id=handId)

    async def playCard(self, playerId: str, handId: int, rank: str, suit: str):
        """ Plays a card in a hand
        If the card played finish the hand, also notifies the result to all players

        Args:
            playerId (str): id of the player who is playing the card.
            handId (int): id of the hand to play the card.
            suit (str): the suit of the card to be played.
            rank (str): the rank of the card to be played.
        """
        hand = self._hand_manager.play_card(hand_id=handId, player_id=playerId,
                                            rank=rank, suit=suit)

        await self.handUpdate(hand_id=hand.id)

        if hand.winner is not None:
            await self.updateScore(handId=hand.id)

    async def updateScore(self, handId: int):
        """ Updates the score in a game to all players

        Args:
            handId (int): id of the hand to play the card.
        """
        # TODO, por ahora queda todo harcodeado así, mejorar todo
        hand: Hand = self._hand_manager.get_hand(id=handId)

        if hand.envido.winner is not None and hand.winner is None:
            # Acutaliza sólo envido
            score: Score = self._score_manager.assign_envido_score(hand=hand)

            data = json.dumps({
                "event": "updateScore",
                "payload": {
                    "score": jsonable_encoder(score)
                },
            })

            for player in hand.players:
                await self._connection_manager.send(json_string=data, player_id=player.id)

        else: # Actualiza el score del truco y reinicia la mano
            score: Score = self._score_manager.assign_truco_score(hand=hand)

            data = json.dumps({
                "event": "updateScore",
                "payload": {
                    "score": jsonable_encoder(score)
                },
            })

            for player in hand.players:
                await self._connection_manager.send(json_string=data, player_id=player.id)

            # TODO, por ahora reinicia toda la mano
            # En realidad hay que cambiar de repartidor, mano, y turno al jugador contrario
            # al que estaba
            self._hand_manager.initialize_hand(hand_id=hand.id)
            await self.handUpdate(hand_id=hand.id)

    async def chantTruco(self, playerId: str, handId: int, level: int):
        """ Handles the truco status of a hand

        Args:
            playerId (str): id of the player who is playing the card.
            handId (int): id of the hand to play the card.
            level (Truco): the level of the truco chanted/accepted/declined.
        """
        hand = self._hand_manager.get_hand(id=handId)
        self._truco_manager.chant_truco(player_id=playerId, hand_id=handId, level=level)

        await self.handUpdate(hand_id=hand.id)

    async def responseToTruco(self, playerId: str, handId: int, level: int):
        """ Response to a chantTruco event
        If level is higher than the actual, it's chanted again to the opponent.
        If level is the same, then it's accepted.
        If level is lower than current, then it's declined.

        Args:
            playerId (str): id of the player who is playing the card.
            handId (int): id of the hand to play the card.
            level (Truco): the level of the truco chanted/accepted/declined.
        """
        hand = self._hand_manager.get_hand(id=handId)
        self._truco_manager.response_to_truco(player_id=playerId, hand_id=handId, level=level)

        if hand.winner:
            await self.updateScore(handId=hand.id)
            return

        await self.handUpdate(hand_id=hand.id)

    async def chantEnvido(self, playerId: str, handId: int, level: int):
        """ Chants envido to the opponent

        Args:
            playerId (str): id of the player who is playing the card.
            handId (int): id of the hand to play the card.
            level (Truco): the level of the truco chanted/accepted/declined.
        """
        self._envido_manager.chant_envido(player_id=playerId, hand_id=handId, level=level)

        await self.handUpdate(hand_id=handId)

    async def responseToEnvido(self, playerId: str, handId: int, level: int):
        """ Response to a envido to the opponent """
        self._envido_manager.response_to_envido(player_id=playerId, hand_id=handId, level=level)

        await self.handUpdate(hand_id=handId)

    async def acceptEnvido(self, playerId: str, handId: int):
        """ Accepts an envido play """
        self._envido_manager.accept_envido(player_id=playerId, hand_id=handId)

        await self.handUpdate(hand_id=handId)

    async def declineEnvido(self, playerId: str, handId: int):
        """ Declines envido in a Hand of Truco """
        hand: Hand = self._hand_manager.get_hand(id=handId)
        self._envido_manager.decline_envido(player_id=playerId, hand_id=handId)
        # TODO should I also set envido score?
        if hand.envido.winner is not None:
            await self.updateScore(handId=hand.id)

        await self.handUpdate(hand_id=handId)

    async def playEnvido(self, playerId: str, handId: int, cards: List):
        """ Plays the cards for envido """
        hand: Hand = self._hand_manager.get_hand(id=handId)
        envido_cards = [Card(**card) for card in cards]
        self._envido_manager.play_envido(hand_id=handId, player_id=playerId, cards=envido_cards)

        # Si hay ganador, update score y continuar la mano
        if hand.envido.winner is not None:
            await self.updateScore(handId=hand.id)

        await self.handUpdate(hand_id=handId)


socket = SocketController()


def dep_socket_controller():
    return socket
