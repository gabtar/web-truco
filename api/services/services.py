import json
import random

from typing import Optional
from fastapi import Depends
from models.models import Player, Hand
from services.connection_manager import ConnectionManager, dep_connection_manager


class GameException(Exception):
    def __init__(self, message='Error en la partida'):
        self.message = message

    def __str__(self):
        return str(self.message)


class HandManager:
    """ Manages hands of Truco """
    connection_manager: ConnectionManager

    def __init__(self, connection_manager: ConnectionManager = Depends(dep_connection_manager)):
        self.connection_manager = connection_manager

    async def deal_cards(self, hand_id: int, player_id: str):
        """ Deals cards for all players for an specific game/hand_id """
        player = Player.get_by_id(player_id=player_id)
        hand = Hand.get_by_id(hand_id=hand_id)
        players = hand.get_current_players()

        if player.id != hand.player_hand or player not in players:
            raise GameException('Acción inválida')

        # TODO, más adelante cambiar esto para jugar de a 4 o 6
        if len(hand.get_current_players()) < 2:
            raise GameException('No hay suficientes jugadores')

        card_ids = random.sample(range(1, 41), len(players) * 3)

        for player in players:
            cards_dealed = []
            for i in range(3):
                cards_dealed.append(hand.deal_card_to_player(player_id=player.id, card_id=card_ids.pop()))

            cards_list = [card.dict(include={'rank', 'suit'}) for card in cards_dealed]
            message = json.dumps({"event": "receiveDealedCards", "cards": cards_list})
            await self.connection_manager.send(json_string=message,player_id=player.id)

    async def play_card(self, hand_id: int, player_id: str, card_id: int):
        """ Performs a card play on a game """
        hand = Hand.get_by_id(hand_id)

        if hand.get_card_played(player_id=player_id, round_number=hand.current_round) is not None:
            raise GameException('Ya has jugado una carta')

        card = hand.play_card(player_id=player_id, card_id=card_id)

        message = json.dumps({"event": "cardPlayed", "card": card.dict(include={'rank', 'suit'})})

        for player in hand.get_current_players():
            await self.connection_manager.send(json_string=message, player_id=player.id)

        # TODO si ya jugaron todos una carta pasar al siguiente round
        # TODO, si la carta finaliza el round -> asignar score y reiniciar mano
        # hand.current_round += 1
        # hand.update()

    async def games_update(self, player_id: Optional[str] = None):
        """ Updates the games list to all players connected in WebSocket """
        # Debería ser get_avaliables_games() -> sólo aquellos que tienen lugares disponibles
        # O tal vez poner un estado que sea EN_JUEGO, SIN_COMENZAR, FINALIZADO
        games_list = Hand.get_all()
        current_games = [game.dict(include={'id', 'name'}) for game in games_list]
        games_update = json.dumps({"event": "gamesUpdate", "currentGames": current_games})

        if player_id:
            await self.connection_manager.send(json_string=games_update, player_id=player_id)
        else:
            await self.connection_manager.broadcast(games_update)

    async def join_hand(self, hand_id: int, player_id: str):
        """ Joins to an specific hand """
        hand = Hand.get_by_id(hand_id=hand_id)
        player = Player.get_by_id(player_id=player_id)

        if player.playing_hand is not None:
            raise GameException('Ya estás en una partida')

        if len(hand.get_current_players()) >= 2:
            raise GameException('Partida completa')

        player.playing_hand = hand_id
        player.update()

        message = json.dumps({"event": "joinedHand", "handId": hand_id})
        await self.connection_manager.send(json_string=message, player_id=player_id)

    async def new_hand(self, player_id: str) -> int:
        """ Creates a new hand/game """
        player = Player.get_by_id(player_id=player_id)

        if player.playing_hand is not None:
            raise GameException('Ya estás en una partida')

        # TODO hacer el insert directamente con el autoincrement
        hand = Hand(id=len(Hand.get_all())+1, player_hand=player_id).save()
        player.playing_hand = hand.id
        player.update()

        message = json.dumps({"event": "joinedHand", "handId": hand.id})
        await self.connection_manager.send(json_string=message, player_id=player_id)

        return hand.id
