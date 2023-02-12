import random

from typing import List, Dict, Optional
from models.models import Hand, Suit, Rank, Card, Score, Player, Round
# Games repository dependence
from repositories.repository import (
        AbstractHandRepository, dep_games_repository,
        AbstractScoreRepository, dep_scores_repository,
        AbstractPlayerRepository, dep_players_repository
)


class GameException(Exception):
    def __init__(self, message='Error en la partida'):
        self.message = message

    def __str__(self):
        return str(self.message)


class PlayerManager:
    """ Manages players of the game """
    players_repository: AbstractPlayerRepository

    def __init__(self, players_repository: AbstractPlayerRepository = dep_players_repository()):
        self.players_repository = players_repository

    def create(self) -> Player:
        player = Player()
        # TODO, ver de asignar nombre random?
        player.name = f'Anónimo#{len(self.players_repository._players)}'
        self.players_repository.save(player)
        return player

    def find_player(self, player_id: str) -> Optional[Player]:
        return self.players_repository.get_by_id(id=player_id)


class HandManager:
    """ Manages hands of Truco """
    hand_repository: AbstractHandRepository
    player_repository: AbstractPlayerRepository

    def __init__(
            self,
            hands: AbstractHandRepository = dep_games_repository(),
            players: AbstractPlayerRepository = dep_players_repository()
            ):
        self.hand_repository = hands
        self.players_repository = players
        self.deck = [Card(suit=suit, rank=rank) for rank in Rank for suit in Suit]

    def get_hand(self, id: int) -> Hand:
        return self.hand_repository.get_by_id(id=id)

    def deal_cards(self, hand_id: int, player_id: str) -> Dict[str, List[Card]]:
        """ Deals cards for all players for an specific game/hand_id """
        hand = self.hand_repository.get_by_id(id=hand_id)

        # TODO, check player is plaing hand -> player_id not in hand.players or
        if player_id != hand.player_dealer:
            raise GameException('Acción inválida')

        cards = random.sample(range(40), len(hand.players) * 3)

        for player in hand.players:
            for i in range(3):
                hand.cards_dealed[player.id].append(self.deck[cards.pop()])

        self.hand_repository.update(hand)

        return hand.cards_dealed

    def play_card(self, hand_id: int, player_id: str, rank: str, suit: str) -> Hand:
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

        # Juega la carta y la elimina de las cartas en mano
        hand.cards_dealed[player_id].remove(card)
        hand.rounds[-1].cards_played[player_id] = card

        # Dar Turno al siguiente jugador
        round_finished = True
        for player in hand.players:
            if hand.rounds[-1].cards_played[player.id] is None:
                hand.player_turn = player.id
                round_finished = False

        if round_finished and len(hand.rounds) < 3:
            # Crea el nuevo round!
            cards_played = {player.id: None for player in hand.players}
            hand.rounds.append(Round(cards_played=cards_played))

        self.hand_repository.update(hand)

        return hand

    def avaliable_games(self) -> List[Hand]:
        """ Returns the games avaliable to join """
        return self.hand_repository.get_availables()

    def join_hand(self, hand_id: int, player_id: str) -> None:
        """ Joins to an specific hand """
        hand = self.hand_repository.get_by_id(id=hand_id)
        player = self.players_repository.get_by_id(id=player_id)

        if len(hand.players) >= 2:
            raise GameException('Partida completa')

        hand.players.append(player)

        # If hand is complete, initialize the hand and set the dealer, hand, etc
        if len(hand.players) == 2:
            self.initialize_hand(hand_id=hand.id)

        # Inicializa las variables del jugador en la mano
        hand.cards_dealed[player_id] = []

        self.hand_repository.update(hand)

    def initialize_hand(self, hand_id: int) -> None:
        """ Sets the dealer, the player who is hand, and initialize hand variables """
        hand = self.hand_repository.get_by_id(id=hand_id)

        if len(hand.players) < 2:
            raise GameException('No hay suficientes jugadores')

        hand.player_dealer = random.choice(hand.players).id
        for player in hand.players:
            # TODO, necesario por ahora para limpiar las cartas repartidas
            # Cuando se reinicia la mano
            hand.cards_dealed[player.id] = []

            if player.id != hand.player_dealer:
                hand.player_turn = player.id
                hand.player_hand = player.id

        cards_played = {player.id: None for player in hand.players}
        hand.rounds = [Round(cards_played=cards_played)]

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

    def get_score(self, hand_id: int) -> Score:
        self.score_repository.get_by_id(id=hand_id)

    def initialize_score(self, hand: Hand) -> None:
        score: Score = Score()
        score.id = hand.id
        for player in hand.players:
            score.score[player.id] = 0
        self.score_repository.save(score)

    def assign_score(self, hand: Hand) -> Score:
        """ Assigns the score the the passed hand """
        score: Score = self.score_repository.get_by_id(id=hand.id)
        score.score[hand.winner] += 1 * hand.truco_status
        # TODO asignar score del envido

        self.score_repository.update(score)
        return score
