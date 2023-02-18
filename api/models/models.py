from __future__ import annotations
import uuid

from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class Suit(str, Enum):
    """ Suits of spanish cards """
    BASTO = "B"
    ESPADA = "E"
    COPA = "C"
    ORO = "O"


class Rank(str, Enum):
    """ Ranks of spanish card for truco game, 8 and 9 are not present """
    AS = "1"
    DOS = "2"
    TRES = "3"
    CUATRO = "4"
    CINCO = "5"
    SEIS = "6"
    SIETE = "7"
    SOTA = "10"
    CABALLO = "11"
    REY = "12"


TRUCO_CARD_VALUES = {
        "0": {"rank": Rank.CUATRO,  "suit": [Suit.BASTO, Suit.COPA, Suit.ESPADA, Suit.ORO]},
        "1": {"rank": Rank.CINCO,  "suit": [Suit.BASTO, Suit.COPA, Suit.ESPADA, Suit.ORO]},
        "2": {"rank": Rank.SEIS,  "suit": [Suit.BASTO, Suit.COPA, Suit.ESPADA, Suit.ORO]},
        "3": {"rank": Rank.SIETE,  "suit": [Suit.BASTO, Suit.COPA]},
        "4": {"rank": Rank.SOTA,  "suit": [Suit.BASTO, Suit.COPA, Suit.ESPADA, Suit.ORO]},
        "5": {"rank": Rank.CABALLO,  "suit": [Suit.BASTO, Suit.COPA, Suit.ESPADA, Suit.ORO]},
        "6": {"rank": Rank.REY,  "suit": [Suit.BASTO, Suit.COPA, Suit.ESPADA, Suit.ORO]},
        "7": {"rank": Rank.AS,  "suit": [Suit.COPA, Suit.ORO]},
        "8": {"rank": Rank.DOS,  "suit": [Suit.BASTO, Suit.COPA, Suit.ESPADA, Suit.ORO]},
        "9": {"rank": Rank.TRES,  "suit": [Suit.BASTO, Suit.COPA, Suit.ESPADA, Suit.ORO]},
        "10": {"rank": Rank.SIETE,  "suit": [Suit.ORO]},
        "11": {"rank": Rank.SIETE,  "suit": [Suit.ESPADA]},
        "12": {"rank": Rank.AS,  "suit": [Suit.BASTO]},
        "13": {"rank": Rank.AS,  "suit": [Suit.ESPADA]}
}


def get_value_of_card(rank: Rank, suit: Suit) -> int:
    """ Returns the value of a card acording to the Truco card score """
    for value, cards in TRUCO_CARD_VALUES.items():
        if cards["rank"] == rank and suit in cards["suit"]:
            return int(value)

    return -1


class Player(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Anónimo"


class Card(BaseModel):
    """ A card in the game """
    suit: Suit
    rank: Rank
    _value: int = None

    class Config:
        # Para que no serialize el _value
        underscore_attrs_are_private = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._value = get_value_of_card(rank=self.rank, suit=self.suit)


class Truco(int, Enum):
    """ Ranges of truco in a Hand, the integer values are the score winned """
    NO_CANTADO = 1
    TRUCO = 2
    RETRUCO = 3
    VALE_CUATRO = 4


class Envido(int, Enum):
    """ Ranges of truco in a Hand """
    NO_CANTADO = 0
    ENVIDO = 1
    REAL_ENVIDO = 2
    FALTA_ENVIDO = 3


class HandStatus(str, Enum):
    """ The status of a hand """
    NOT_STARTED = 'NOT_STARTED'
    IN_PROGRESS = 'IN_PROGRESS'
    LOCKED = 'LOCKED'
    FINISHED = 'FINISHED'


class Round(BaseModel):
    """ A Round of a hand of truco """
    cards_played: Dict[str, Optional[Card]]

    @property
    def finished(self) -> bool:
        """ Check if the round is finished """
        for card in self.cards_played.values():
            if card is None:
                return False
        return True

    @property
    def winner(self) -> Optional[str]:
        """ Determines the winner of a round in a Hand of truco

        Returns:
            player(Optional[List[str]]): An string array of the ids of the
                                        player(s) who won the round
        """
        # Si el round sigue activo, no hay ganador
        if not self.finished:
            return None

        # Get the highest card
        highest_value = max([card._value
                             for card in self.cards_played.values()])
        return [player
                for player, card in self.cards_played.items()
                if card._value == highest_value]


class Hand(BaseModel):
    """ A hand of truco """
    id: Optional[int]
    name: str = 'Nueva Mano'
    players: List[Player] = []
    player_turn: Optional[str]  # Al jugador que le toca tirar carta
    chant_turn: Optional[str]  # Al jugador que le toca cantar/aceptar
    player_hand: Optional[str]  # El jugador que es mano
    player_dealer: Optional[str]  # El que reparte la mano
    cards_dealed: Dict[str, List[Card]] = {}
    rounds: List[Round] = []
    truco_status: Truco = Truco.NO_CANTADO
    envido: Envido = Envido.NO_CANTADO
    winner: Optional[str]
    status: HandStatus = HandStatus.NOT_STARTED

    @property
    def check_winner(self) -> Optional[str]:
        """ Determines the winner of the hand according to the rules of Truco """
        rounds_winned_by_player = {player.id: 0 for player in self.players}

        for round in self.rounds:
            if round.winner is None:
                continue

            for player_id in round.winner:
                rounds_winned_by_player[player_id] += 1

        # Si ganó 2 y es unique -> Hay ganador
        # Si ganó 2 y multiples ganadores define ganador del 3 round
        # Si ganó 3 y multiples ganadores define el jugador que es mano
        winned_2_rounds = [player for player, wins in rounds_winned_by_player.items() if wins == 2]
        winned_3_rounds = [player for player, wins in rounds_winned_by_player.items() if wins == 3]

        if len(winned_2_rounds) == 1 and len(winned_3_rounds) == 0:
            return winned_2_rounds[0]
        elif len(winned_3_rounds) == 1:
            return winned_3_rounds[0]
        elif len(self.rounds) == 3 and self.rounds[2].winner is not None:
            return self.player_hand

        return None

    @property
    def update_turn_to_next_player(self):
        """ Updates turn to next player in the player list """
        player = [player for player in self.players if player.id == self.player_turn]
        player_turn_index = self.players.index(player[0])

        if player_turn_index == len(self.players) - 1:
            self.player_turn = self.players[0].id
        else:
            self.player_turn = self.players[player_turn_index + 1].id

    @property
    def update_chant_turn_to_opponent(self):
        """ Updates the chant turn to the opponent """
        player = [player for player in self.players if player.id == self.chant_turn]
        chant_turn_index = self.players.index(player[0])

        if chant_turn_index == len(self.players) - 1:
            self.chant_turn = self.players[0].id
        else:
            self.chant_turn = self.players[chant_turn_index + 1].id


class Score(BaseModel):
    """ Score of a truco game """
    id: Optional[int]  # El id de la partida
    # NOTA, Siempre van a ser 2 ya sea los jugadores o equipos
    score: Optional[Dict[str, int]] = {} # Por ahora queda con el id del jugador y puntaje
