# Base models for the game
from enum import Enum
from typing import List, Dict
from random import shuffle

# TODO
# Mas adelante armar los modelos con db -> sqlite?
# En la documentación de websockets con fastapi
# hay una forma de guardar las connexiones de socket con redis, averiguar
# Agregar tests -> pytest


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


class Card:
    """ A card in the game """
    suit: Suit
    rank: Rank
    value: int

    def __init__(self, suit, rank, value):
        self.suit = suit
        self.rank = rank
        self.value = value

    def to_json(self):
        """ Returns a dict representation of the class """
        # TODO, esto es to_dict porque el json.dumps lo hace json al final,
        # sino lo toma como string de json y con JSON.parse en js no lo parsea a objeto de js
        return {"rank": self.rank.value, "suit": self.suit.value}

    def __eq__(self, other) -> bool:
        """ Define equal cards """
        return self.value == other.value

    def __lt__(self, other) -> bool:
        """ Define if a card is lower than other """
        return self.value < other.value

    def __gt__(self, other) -> bool:
        """ Define if a card is higher than other """
        return self.value > other.value


class Deck:
    """ A deck of spanish cards for truco game """
    cards: List[Card] = []

    def __init__(self):
        for rank in Rank:
            for suit in Suit:
                self.cards.append(Card(suit, rank, get_value_of_card(rank, suit)))

    def shuffle(self):
        shuffle(self.cards)


class Hand:
    hand_id: int
    name: str
    deck: Deck
    players: List[str]
    cards_dealed: Dict[str, List[Card]]
    player_turn: str
    # cards_dealed: List[PlayerCards]
    current_round: int = 0
    # TODO, modelar las cartas en mesa
    # table: PlayerCards

    def __init__(self, hand_id: int):
        self.deck = Deck()
        self.players = []
        self.cards_dealed = {}
        self.hand_id = hand_id
        self.name = f"Mano #{hand_id}"

    def deal_cards(self):
        """ Deal 3 cards for each player """
        self.deck.shuffle()
        # TODO, ojo que con pop está mutando el mazo
        for player in self.players:
            self.cards_dealed[player] = [self.deck.cards.pop() for _ in range(3)]

    def play_card(self, player_id, card_id):
        """ Play a card """
        pass

    def to_json(self):
        # TODO, ojo aca!!! Debería ser to dict, porque el json.dump se hace después cuando
        # manda la lista de games
        return {"name": self.name, "handId": self.hand_id}
