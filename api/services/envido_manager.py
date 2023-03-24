from typing import List
from models.models import (
    Hand, Card, Player, HandStatus, EnvidoLevels, EnvidoStatus
)
from services.exceptions import GameException
from repositories.repository import (
        AbstractHandRepository, dep_hand_repository,
        AbstractGameRepository, dep_game_repository
)


class EnvidoManager:
    """ Handles the envido status during a Hand of truco """
    _hand_repository: AbstractHandRepository
    _game_repository: AbstractGameRepository

    def __init__(self,
                 hands: AbstractHandRepository = dep_hand_repository(),
                 games: AbstractGameRepository = dep_game_repository()
                 ):
        self._hand_repository = hands
        self._game_repository = games

    def chant_envido(self, hand_id: int, player_id: str, level: EnvidoLevels):
        """ Chants envido to the opponent player """
        hand: Hand = self._hand_repository.get_by_id(id=hand_id)
        players: List[Player] = self._game_repository.get_by_id(id=hand_id).players

        if hand.status == HandStatus.NOT_STARTED:
            raise GameException('Deben repartirse las cartas primero')

        if len(hand.rounds) > 0 and hand.rounds[0].finished:
            raise GameException('No se puede cantar después de la primera ronda')

        if hand.envido.status == EnvidoStatus.FINISHED:
            raise GameException('El envido ya ha finalizado')

        if hand.chant_turn != player_id:
            raise GameException('No es tu turno')

        hand.envido.cards_played = {player.id: [] for player in players}
        hand.envido.chanted.append(level)
        hand.envido.status = EnvidoStatus.CHANTING
        hand.chant_turn = self._next_player_chant_turn(hand=hand)
        hand.status = HandStatus.ENVIDO

        self._hand_repository.update(hand)

    def response_to_envido(self, hand_id: int, player_id: str, level: EnvidoLevels):
        """ Responses to an envido chant """
        hand: Hand = self._hand_repository.get_by_id(id=hand_id)

        if hand.chant_turn != player_id:
            raise GameException('No es tu turno')

        if hand.envido.chanted[-1] != EnvidoLevels.ENVIDO and level <= hand.envido.chanted[-1]:
            raise GameException('No se puede cantar un nivel inferior')

        hand.envido.chanted.append(level)
        hand.chant_turn = self._next_player_chant_turn(hand=hand)
        self._hand_repository.update(hand)

    def accept_envido(self, hand_id: int, player_id: str):
        """ Accepts chant/current level of envido and sets the points to win"""
        hand: Hand = self._hand_repository.get_by_id(id=hand_id)

        if hand.chant_turn != player_id:
            raise GameException('No es tu turno')

        for level in hand.envido.chanted:
            hand.envido.points += level

        # Usar el chant turn para cantar la jugada/cartas luego
        hand.envido.status = EnvidoStatus.ACCEPTED
        hand.chant_turn = self._next_player_chant_turn(hand=hand)
        self._hand_repository.update(hand)

    def decline_envido(self, hand_id: int, player_id: str):
        """ Declines the current envido levels(s) sets the points and the winner """
        hand: Hand = self._hand_repository.get_by_id(id=hand_id)

        if hand.chant_turn != player_id:
            raise GameException('No es tu turno')

        for level in hand.envido.chanted[:-1]:
            hand.envido.points += level
        hand.envido.points += 1  # El que no fue aceptado

        hand.chant_turn = self._next_player_chant_turn(hand=hand)
        hand.envido.winner = hand.player_turn
        hand.envido.status = EnvidoStatus.FINISHED
        hand.status = HandStatus.IN_PROGRESS  # Reanuda la mano
        self._hand_repository.update(hand)

    def play_envido(self, hand_id: int, player_id: str, cards: List[Card]):
        """ Plays cards during envido """
        hand: Hand = self._hand_repository.get_by_id(id=hand_id)

        # TODO, Faltan validaciones, si tiene las cartas, etc
        hand.envido.cards_played[player_id] = cards
        hand.chant_turn = self._next_player_chant_turn(hand=hand)

        # Verificar ganador
        if hand.envido.all_played:
            envido_scores = {
                    player: self._calculate_envido(hand.envido.cards_played[player])
                    for player in hand.envido.cards_played.keys()
            }
            highest_score = max(envido_scores.values())
            winner = [player for player, score in envido_scores.items() if score == highest_score]

            if len(winner) == 1:
                hand.envido.winner = winner[0]
            else:
                hand.envido.winner = hand.player_hand

            hand.envido.status = EnvidoStatus.FINISHED
            hand.status = HandStatus.IN_PROGRESS # Continúa la mano para jugar cartas

        self._hand_repository.update(hand)

    def _calculate_envido(self, cards: List[Card]) -> int:
        """ Calculates the envido value for the cards passed """
        if len(cards) == 2:
            score = 20
            for card in cards:
                score += int(card.rank) if int(card.rank) < 10 else 0
            return score
        else:
            return int(cards[0].rank) if int(cards[0].rank) < 10 else 0

    def _next_player_chant_turn(self, hand: Hand) -> str:
        """ Determines the chant turn of the next player in the hand """
        players: List[Player] = self._game_repository.get_by_id(id=hand.id).players

        player = [player for player in players if player.id == hand.chant_turn]
        chant_turn_index = players.index(player[0])

        if chant_turn_index == len(players) - 1:
            return players[0].id
        else:
            return players[chant_turn_index + 1].id
