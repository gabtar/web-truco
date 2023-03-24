from typing import List

from models.models import Hand, Truco, HandStatus, Player
from services.exceptions import GameException
from repositories.repository import (
    AbstractHandRepository, dep_hand_repository,
    AbstractGameRepository, dep_game_repository
)


class TrucoManager:
    """ Handles the truco status/levels in a hand """
    _hand_repository: AbstractHandRepository
    _game_repository: AbstractGameRepository

    def __init__(self,
                 hands: AbstractHandRepository = dep_hand_repository(),
                 games: AbstractGameRepository = dep_game_repository()
                 ):
        self._hand_repository = hands
        self._game_repository = games

    def chant_truco(self, hand_id: int, player_id: str, level: Truco):
        """ Chants truco to the opponent player """
        hand: Hand = self._hand_repository.get_by_id(id=hand_id)

        if hand.status == HandStatus.NOT_STARTED:
            raise GameException('Deben repartirse las cartas primero')

        if hand.chant_turn != player_id:
            raise GameException('No es tu turno')

        if level - hand.truco_status != 1:
            raise GameException('Nivel de truco inválido')

        hand.truco_status = level
        hand.status = HandStatus.LOCKED
        hand.chant_turn = self._next_player_chant_turn(hand=hand)

        self._hand_repository.update(hand)

    def response_to_truco(self, hand_id: int, player_id: str, level: Truco):
        """ Response to the truco chant. If level is same of current truco_status
            its accepted. If it's is +1 higher, is chanted again to the other
            player, and if it's -1 level its declined and the hand ends
        """
        hand: Hand = self._hand_repository.get_by_id(id=hand_id)

        if hand.chant_turn != player_id:
            raise GameException('No es tu turno')

        if level == hand.truco_status:
            # Return control to original player
            hand.chant_turn = self._next_player_chant_turn(hand=hand)
            hand.status = HandStatus.IN_PROGRESS
        elif level == hand.truco_status - 1:
            hand.winner = hand.player_turn
            hand.status = HandStatus.FINISHED
            hand.truco_status = hand.truco_status - 1  # No querído
        elif level == hand.truco_status + 1:
            return self.chant_truco(hand_id=hand_id, player_id=player_id, level=hand.truco_status + 1)
        else:
            raise GameException('Nivel de truco inválido')

        self._hand_repository.update(hand)

    def _next_player_chant_turn(self, hand: Hand) -> str:
        """ Determines the chant turn of the next player in the hand """
        players: List[Player] = self._game_repository.get_by_id(id=hand.id).players

        player = [player for player in players if player.id == hand.chant_turn]
        chant_turn_index = players.index(player[0])

        if chant_turn_index == len(players) - 1:
            return players[0].id
        else:
            return players[chant_turn_index + 1].id
