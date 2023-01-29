from __future__ import annotations
import uuid
import random

from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from fastapi import Depends


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
    value: int = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.value = get_value_of_card(rank=self.rank, suit=self.suit)

    def __eq__(self, other) -> bool:
        """ Define equal cards """
        return self.value == other.value

    def __lt__(self, other) -> bool:
        """ Define if a card is lower than other """
        return self.value < other.value

    def __gt__(self, other) -> bool:
        """ Define if a card is higher than other """
        return self.value > other.value


class Truco(int, Enum):
    """ Ranges of truco in a Hand """
    NO_CANTADO = 1
    TRUCO = 2
    RETRUCO = 3
    VALE_CUATRO = 4


class Envido(int, Enum):
    """ Ranges of truco in a Hand """
    NINGUNO = 0
    ENVIDO = 1
    REAL_ENVIDO = 2
    FALTA_ENVIDO = 3


class Hand(BaseModel):
    """ A hand of truco """
    id: Optional[int]  # TODO, debería autogenerarse por la db, persistencia
    name: str = 'Nueva Mano'
    player_turn: Optional[str]  # Al jugador que le toca tirar carta
    player_hand: Optional[str]  # El jugador que es mano
    player_dealer: Optional[str]  # El que reparte la mano
    current_round: Optional[int]
    cards_dealed: Dict[str, List[Card]] = {}
    cards_played: Dict[str, List[Card]] = {}
    players: List[Player] = []
    truco_status: Truco = Truco.NO_CANTADO
    envido: Envido = Envido.NINGUNO


class Score(BaseModel):
    """ Score of a truco game """
    id: Optional[int]  # El id de la partida
    # NOTA, Siempre van a ser 2 ya sea los jugadores o equipos
    score: Optional[Dict[str, int]] # Por ahora queda con el id del jugador y puntaje
