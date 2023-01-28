import random

from typing import List, Dict
from models.models import Hand, Suit, Rank, Card
# Games repository dependence
from repositories.repository import AbstractHandRepository, dep_games_repository


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
        """ Performs a card play on a game """
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

        # SHOULD I RETURN THE CARD PLAYED AND THE WITH THE ROUND NUMBER?
        # OR THE CARDS IN MESA?
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
