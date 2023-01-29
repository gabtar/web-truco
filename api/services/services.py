import random

from typing import List, Dict, Optional
from models.models import Hand, Suit, Rank, Card, Score
# Games repository dependence
from repositories.repository import (
        AbstractHandRepository, dep_games_repository,
        AbstractScoreRepository, dep_scores_repository
)


class GameException(Exception):
    def __init__(self, message='Error en la partida'):
        self.message = message

    def __str__(self):
        return str(self.message)


class HandManager:
    """ Manages hands of Truco """
    hands: AbstractHandRepository

    def __init__(self, hands: AbstractHandRepository = dep_games_repository()):
        self.hand_repository = hands
        self.deck = [Card(suit=suit, rank=rank) for rank in Rank for suit in Suit]

    # TODO, get hand by id from repository
    def get_hand(self, id: int):
        pass

    def deal_cards(self, hand_id: int, player_id: str) -> Dict[str, List[Card]]:
        """ Deals cards for all players for an specific game/hand_id """
        hand = self.hand_repository.get_by_id(id=hand_id)

        if player_id not in hand.players or player_id != hand.player_dealer:
            raise GameException('Acción inválida')

        cards = random.sample(range(40), len(hand.players) * 3)

        for player in hand.players:
            for i in range(3):
                hand.cards_dealed[player].append(self.deck[cards.pop()])

        self.hand_repository.update(hand)

        return hand.cards_dealed

    def play_card(self, hand_id: int, player_id: str, rank: str, suit: str) -> Dict[str, List[Card]]:
        """ Performs a card play on a game

            Returns:
                cards: Dict[str, List[Card]] the cards played on the hand
        """
        card = Card(suit=suit, rank=rank)
        hand = self.hand_repository.get_by_id(id=hand_id)

        if card not in hand.cards_dealed[player_id]:
            raise GameException('No tienes ésa carta')

        if hand.player_turn != player_id:
            raise GameException('No es tu turno')

        # TODO, en realidad no sería necesario porque cuando juega la carta cambia
        # de turno, y/o pasa al siguiente round
        # if len(hand.cards_played[player_id]) > hand.current_round:
        #     raise GameException('Ya has jugado una carta')

        # Juega la carta y la elimina de las cartas en mano
        hand.cards_dealed[player_id].remove(card)
        hand.cards_played[player_id].append(card)

        # Dar Turno al siguiente jugador
        round_finished = True
        for player in hand.players:
            if len(hand.cards_played[player]) < hand.current_round + 1:
                hand.player_turn = player
                round_finished = False

        if round_finished:
            hand.current_round += 1
        self.hand_repository.update(hand)

        return hand.cards_played

    def avaliable_games(self) -> List[Hand]:
        """ Returns the games avaliable to join """
        return self.hand_repository.get_availables()

    def join_hand(self, hand_id: int, player_id: str) -> None:
        """ Joins to an specific hand """
        hand = self.hand_repository.get_by_id(id=hand_id)

        if len(hand.players) >= 2:
            raise GameException('Partida completa')

        # Inicializa las variables del jugador en la mano
        hand.cards_played[player_id] = []
        hand.cards_dealed[player_id] = []

        hand.players.append(player_id)

        # If hand is complete, initialize the hand and set the dealer, hand, etc
        if len(hand.players) == 2:
            self.initialize_hand(hand_id=hand.id)

        self.hand_repository.update(hand)

    def initialize_hand(self, hand_id: int):
        """ Sets the dealer, the player who is hand, and initialize hand variables """
        hand = self.hand_repository.get_by_id(id=hand_id)

        if len(hand.players) < 2:
            raise GameException('No hay suficientes jugadores')

        # TODO, sorteo de la mano?
        hand.player_dealer = hand.players[0]
        for player in hand.players:
            if player != hand.player_dealer:
                hand.player_turn = player
                hand.player_hand = player

        hand.current_round = 0
        self.hand_repository.update(hand)

    def new_hand(self, player_id: str) -> int:
        """ Creates a new hand/game """
        hand = Hand()
        self.hand_repository.save(hand)

        return hand.id


class ScoreManager:
    """ Manages scores of hands of truco """
    score_repository: AbstractScoreRepository

    def __init__(self, score_repository: AbstractScoreRepository = dep_scores_repository()):
        self.score_repository = score_repository

    def initialize_score(self, hand: Hand):
        score: Score = Score()
        score.id = hand.id
        score.score = {}
        for player in hand.players:
            score.score[player] = 0
        self.score_repository.save(score)

    def check_round_winner(self, hand: Hand, round_number: int) -> Optional[str]:
        """ Determines the winner of a round

        Returns: The (id: str) winner of the round or null if it's parda
        """
        # TODO, esto no va a funcionar para 4 o 6 jugadores
        cards_played_p1 = hand.cards_played[hand.players[0]]
        cards_played_p2 = hand.cards_played[hand.players[0]]

        card_p1: Card = hand.cards_played[hand.players[0]][round_number] if len(cards_played_p1) > round_number else None
        card_p2: Card = hand.cards_played[hand.players[1]][round_number] if len(cards_played_p2) > round_number else None

        if card_p1 is None or card_p2 is None:
            return None

        if card_p1 == card_p2:
            return None
        elif card_p1 > card_p2:
            return hand.players[0]
        elif card_p1 < card_p2:
            return hand.players[1]

    def hand_winner(self, hand: Hand) -> Optional[str]:
        """ Determines the winner of a hand """
        rounds_winned = [0, 0]  # Stores the rounds winned by each player

        # TODO ver de usar un iterador sobre las cartas en mesa
        for round in range(3):
            round_winner = self.check_round_winner(hand=hand, round_number=round)

            if round_winner is None:
                continue

            if round_winner == hand.players[0]:
                rounds_winned[0] += 1
            else:
                rounds_winned[1] += 1

        # Verificar si alguno ganó 2 rounds
        if 2 in rounds_winned:
            return hand.players[rounds_winned.index(max(rounds_winned))]

        return None

    def assign_score(self, hand: Hand):
        """ Assigns the score the the passed hand """
        score: Score = self.score_repository.get_by_id(id=hand.id)
        score.score[self.hand_winner(hand=hand)] += 1 * hand.truco_status

        self.score_repository.update(score)
