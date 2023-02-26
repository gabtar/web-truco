import random

from typing import List, Dict, Optional
from models.models import (
    Hand, Suit, Rank, Card, Score, Player, Round, Truco, HandStatus,
    EnvidoLevels, Envido, EnvidoStatus
)
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

        if player_id != hand.player_dealer:
            raise GameException('Acción inválida')

        cards = random.sample(range(40), len(hand.players) * 3)

        for player in hand.players:
            for i in range(3):
                hand.cards_dealed[player.id].append(self.deck[cards.pop()])

        hand.status = HandStatus.IN_PROGRESS
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

        if hand.status != HandStatus.IN_PROGRESS:
            raise GameException('Acción inválidad')

        # Juega la carta y actualiza los turnos
        hand.rounds[-1].cards_played[player_id] = card
        hand.update_turn_to_next_player
        hand.chant_turn = hand.player_turn

        # TODO, podría extraer a método en dominio?
        round_finished = True
        for player in hand.players:
            if hand.rounds[-1].cards_played[player.id] is None:
                round_finished = False

        if round_finished and len(hand.rounds) < 3:
            cards_played = {player.id: None for player in hand.players}
            hand.rounds.append(Round(cards_played=cards_played))

        if hand.check_winner:
            hand.winner = hand.check_winner

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
                hand.chant_turn = player.id
                hand.player_hand = player.id

        cards_played = {player.id: None for player in hand.players}
        hand.rounds = [Round(cards_played=cards_played)]
        hand.status = HandStatus.NOT_STARTED
        hand.truco_status = Truco.NO_CANTADO
        hand.winner = None
        hand.envido = Envido()

        self.hand_repository.update(hand)

    def new_hand(self, player_id: str) -> int:
        """ Creates a new hand/game """
        hand = Hand()
        self.hand_repository.save(hand)

        return hand.id


class TrucoManager:
    """ Handles the truco status/levels in a hand """
    _hand_repository: AbstractHandRepository

    def __init__(self, hands: AbstractHandRepository = dep_games_repository()):
        self._hand_repository = hands

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
        hand.update_chant_turn_to_opponent

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
            hand.chant_turn = hand.player_turn
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


class EnvidoManager:
    """ Handles the envido status during a Hand of truco """
    _hand_repository: AbstractHandRepository

    def __init__(self, hands: AbstractHandRepository = dep_games_repository()):
        self._hand_repository = hands

    def chant_envido(self, hand_id: int, player_id: str, level: EnvidoLevels):
        """ Chants envido to the opponent player """
        hand: Hand = self._hand_repository.get_by_id(id=hand_id)

        if hand.status == HandStatus.NOT_STARTED:
            raise GameException('Deben repartirse las cartas primero')

        if len(hand.rounds) > 0 and hand.rounds[0].finished:
            raise GameException('No se puede cantar después de la primera ronda')

        if hand.envido.status == EnvidoStatus.FINISHED:
            raise GameException('El envido ya ha finalizado')

        if hand.chant_turn != player_id:
            raise GameException('No es tu turno')

        hand.envido.cards_played = {player.id: [] for player in hand.players}
        hand.envido.chanted.append(level)
        hand.envido.status = EnvidoStatus.CHANTING

        hand.status = HandStatus.ENVIDO
        hand.update_chant_turn_to_opponent
        self._hand_repository.update(hand)

    def response_to_envido(self, hand_id: int, player_id: str, level: EnvidoLevels):
        """ Responses to an envido chant """
        hand: Hand = self._hand_repository.get_by_id(id=hand_id)

        if hand.chant_turn != player_id:
            raise GameException('No es tu turno')

        if hand.envido.chanted[-1] != EnvidoLevels.ENVIDO and level <= hand.envido.chanted[-1]:
            raise GameException('No se puede cantar un nivel inferior')

        hand.envido.chanted.append(level)
        hand.update_chant_turn_to_opponent
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
        hand.update_chant_turn_to_opponent
        self._hand_repository.update(hand)

    def decline_envido(self, hand_id: int, player_id: str):
        """ Declines the current envido levels(s) sets the points and the winner """
        hand: Hand = self._hand_repository.get_by_id(id=hand_id)

        if hand.chant_turn != player_id:
            raise GameException('No es tu turno')

        for level in hand.envido.chanted[:-1]:
            hand.envido.points += level
        hand.envido.points += 1  # El que no fue aceptado

        hand.update_chant_turn_to_opponent
        hand.envido.winner = hand.chant_turn
        hand.envido.status = EnvidoStatus.FINISHED
        hand.status = HandStatus.IN_PROGRESS  # Reanuda la mano
        self._hand_repository.update(hand)

    def play_envido(self, hand_id: int, player_id: str, cards: List[Card]):
        """ Plays cards during envido """
        hand: Hand = self._hand_repository.get_by_id(id=hand_id)

        # TODO, Faltan validaciones, si tiene las cartas, etc
        hand.envido.cards_played[player_id] = cards
        hand.update_chant_turn_to_opponent

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

    def _calculate_envido(self, cards: List[Card]):
        """ Calculates the envido value for the cards passed """
        if len(cards) == 2:
            score = 20
            for card in cards:
                score += int(card.rank) if int(card.rank) < 10 else 0
            return score
        else:
            return int(cards[0].rank) if int(cards[0].rank) < 10 else 0


class ScoreManager:
    """ Manages scores of hands of truco """
    score_repository: AbstractScoreRepository

    def __init__(
            self,
            score_repository: AbstractScoreRepository = dep_scores_repository()
            ):
        self.score_repository = score_repository

    def get_score(self, hand_id: int) -> Score:
        self.score_repository.get_by_id(id=hand_id)

    def initialize_score(self, hand: Hand) -> None:
        score: Score = Score()
        score.id = hand.id
        for player in hand.players:
            score.score[player.id] = 0
        self.score_repository.save(score)

    def assign_truco_score(self, hand: Hand) -> Score:
        """ Assigns the score the the passed hand """
        score: Score = self.score_repository.get_by_id(id=hand.id)
        score.score[hand.winner] += hand.truco_status

        self.score_repository.update(score)
        return score

    def assign_envido_score(self, hand: Hand) -> Score:
        """ Assigns the score of the envido of the passed hand """
        score: Score = self.score_repository.get_by_id(id=hand.id)
        score.score[hand.envido.winner] += hand.envido.points

        self.score_repository.update(score)
        return score
