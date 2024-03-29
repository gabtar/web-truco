import random

from typing import List, Dict
from models.models import (
    Hand, Suit, Rank, Card, Player, Round, Truco, HandStatus, Envido, EnvidoLevels
)
from services.exceptions import GameException
from repositories.repository import (
        AbstractHandRepository, dep_hand_repository,
        AbstractPlayerRepository, dep_players_repository,
        AbstractGameRepository, dep_game_repository
)


class HandManager:
    """ Manages hands of Truco """
    _hand_repository: AbstractHandRepository
    _player_repository: AbstractPlayerRepository
    _game_repository: AbstractGameRepository

    def __init__(
            self,
            hands: AbstractHandRepository = dep_hand_repository(),
            players: AbstractPlayerRepository = dep_players_repository(),
            games: AbstractGameRepository = dep_game_repository()
            ):
        self._hand_repository = hands
        self._player_repository = players
        self._game_repository = games
        self.deck = [Card(suit=suit, rank=rank) for rank in Rank for suit in Suit]

    def get_hand(self, id: int) -> Hand:
        return self._hand_repository.get_by_id(id=id)

    def deal_cards(self, hand_id: int, player_id: str) -> Dict[str, List[Card]]:
        """ Deals cards for all players for an specific game/hand_id """
        hand: Hand = self._hand_repository.get_by_id(id=hand_id)
        players: List[Player] = self._game_repository.get_by_id(id=hand_id).players

        if player_id != hand.player_dealer:
            raise GameException('Acción inválida')

        cards = random.sample(range(40), len(players) * 3)

        for player in players:
            for i in range(3):
                hand.cards_dealed[player.id].append(self.deck[cards.pop()])

        hand.status = HandStatus.IN_PROGRESS
        self._hand_repository.update(hand)

        return hand.cards_dealed

    def play_card(self, hand_id: int, player_id: str, rank: str, suit: str) -> Hand:
        """ Performs a card play on a game

            Returns:
                cards: Dict[str, List[Card]] the cards played on the hand
        """
        card: Card = Card(suit=suit, rank=rank)
        hand: Hand = self._hand_repository.get_by_id(id=hand_id)
        players: List[Player] = self._game_repository.get_by_id(id=hand_id).players

        if card not in hand.cards_dealed[player_id]:
            raise GameException('No tienes ésa carta')

        if hand.player_turn != player_id:
            raise GameException('No es tu turno')

        if hand.status != HandStatus.IN_PROGRESS:
            raise GameException('Acción inválidad')

        # Juega la carta y actualiza los turnos
        hand.rounds[-1].cards_played[player_id] = card
        hand.player_turn = self._next_player_turn(hand=hand)
        hand.chant_turn = hand.player_turn

        round_finished = True
        for player in players:
            if hand.rounds[-1].cards_played[player.id] is None:
                round_finished = False

        if round_finished and len(hand.rounds) < 3:
            cards_played = {player.id: None for player in players}
            hand.rounds.append(Round(cards_played=cards_played))

        if hand.check_winner:
            hand.winner = hand.check_winner

        self._hand_repository.update(hand)

        return hand

    def initialize_hand(self, hand_id: int) -> None:
        """ Sets the dealer, the player who is hand, and initialize hand variables """
        hand = self._hand_repository.get_by_id(id=hand_id)
        players = self._game_repository.get_by_id(id=hand_id).players

        if len(players) < 2:
            raise GameException('No hay suficientes jugadores')

        hand.player_dealer = random.choice(players).id
        for player in players:
            hand.cards_dealed[player.id] = []

            if player.id != hand.player_dealer:
                hand.player_turn = player.id
                hand.chant_turn = player.id
                hand.player_hand = player.id

        cards_played = {player.id: None for player in players}
        hand.rounds = [Round(cards_played=cards_played)]
        hand.status = HandStatus.NOT_STARTED
        hand.truco_status = Truco.NO_CANTADO
        hand.winner = None
        hand.envido = Envido()

        self._hand_repository.update(hand)

    def go_to_deck(self, game_id: str, player_id: str) -> None:
        """ The player_id abandons the hand """
        hand: Hand = self._hand_repository.get_by_id(id=game_id)
        players: List[Player] = self._game_repository.get_by_id(id=game_id).players

        if hand.player_turn != player_id:
            raise GameException('No es tu turno')

        opponent = [player for player in players if player.id != player_id]

        # Si no terminó el envido son 2 puntos, envido no querido y truco no querido
        if hand.envido.status != 'FINISHED' and len(hand.rounds) == 1:
            # Hay que setear el envido como iniciado por el oponente
            hand.envido.chanted.append(EnvidoLevels.ENVIDO)
            hand.envido.points += 1  # no aceptado
            hand.envido.winner = opponent[0].id

        # Sets the opponent as winner in truco
        hand.winner = opponent[0].id

        self._hand_repository.update(hand=hand)

    def new_hand(self, game_id: str):
        """ Creates a new hand/game """
        hand = Hand()
        hand.id = game_id
        self._hand_repository.save(hand)

    # TODO, improve for multiple players
    def _next_player_turn(self, hand: Hand) -> str:
        """ Determines the turn of the next player in the hand """
        players = self._game_repository.get_by_id(id=hand.id).players

        # Reglas para determinar el turno:
        # Siempre empieza el jugador a la derecha de la 'mano' y gira el turno hasta llegar al repartidor
        # El que ganó el round es el que inicia el próximo round y rota en el mismo sentino
        # Si va parda juega la siguiente carta el ultimo que empardó

        # Si ya hay ganador, empieza el nuevo round el que ganó el anterior
        if hand.rounds[-1].winner:
            # Ojo, devuelve al último de la lista, que no necesariamente es el último que empardó
            return hand.rounds[-1].winner[-1]
        else:
            # Sino sigo el orden normal de la lista hasta que todos juegan la carta y haya ganador
            player = [player for player in players if player.id == hand.player_turn]
            player_turn_index = players.index(player[0])

            if player_turn_index == len(players) - 1:
                return players[0].id
            else:
                return players[player_turn_index + 1].id
