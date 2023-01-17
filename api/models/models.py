from __future__ import annotations
import uuid
import sqlite3

from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional


class NotFound(Exception):
    pass


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
    name: str = "Anonymous"
    playing_hand: Optional[int]

    @classmethod
    def get_by_id(cls, id: str) -> Player:
        con = sqlite3.connect("db.sqlite3")
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("SELECT * FROM player WHERE id = ?", (id,))

        record = cur.fetchone()

        if record is None:
            raise NotFound

        player = cls(**record)  # Row can be unpacked as dict
        con.close()

        return player

    def update(self) -> Player:
        with sqlite3.connect("db.sqlite3") as con:
            cur = con.cursor()
            cur.execute(
                "UPDATE player SET name=?,playing_hand=? WHERE id = ?",
                (self.name, self.playing_hand, self.id)
            )
            con.commit()

        return self

    def save(self) -> Player:
        with sqlite3.connect("db.sqlite3") as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO player (id,name) VALUES(?, ?)",
                (self.id, self.name)
            )
            con.commit()

        return self


# TODO, rename to CardDealer o algo parecido?
class PlayerCard(BaseModel):
    """ The cards the player is holding during a Hand event """
    player_id: str
    card_id: int

    @classmethod
    def get_cards_by_player_id(cls, player_id: str) -> List[Card]:
        con = sqlite3.connect("db.sqlite3")
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("SELECT * FROM playercard WHERE player_id = ?", (player_id,))

        records = cur.fetchall()

        if records is None:
            raise NotFound

        cards = [Card.get_by_id(card[1]) for card in records]
        con.close()

        return cards

    # deal_card?
    def save(self) -> Card:
        with sqlite3.connect("db.sqlite3") as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO playercard (player_id, card_id) VALUES(?, ?)",
                (self.player_id, self.card_id)
            )
            con.commit()

        return Card.get_by_id(self.card_id)


class Card(BaseModel):
    """ A card in the game """
    id: int
    suit: Suit
    rank: Rank
    value: int

    def __eq__(self, other) -> bool:
        """ Define equal cards """
        return self.value == other.value

    def __lt__(self, other) -> bool:
        """ Define if a card is lower than other """
        return self.value < other.value

    def __gt__(self, other) -> bool:
        """ Define if a card is higher than other """
        return self.value > other.value

    @classmethod
    def get_by_id(cls, id: int) -> Card:
        con = sqlite3.connect("db.sqlite3")
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("SELECT * FROM card WHERE id = ?", (id,))

        record = cur.fetchone()

        if record is None:
            raise NotFound

        card = cls(**record)
        con.close()

        return card

    def save(self) -> Card:
        with sqlite3.connect("db.sqlite3") as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO card (id,suit,rank,value) VALUES(?, ?, ?, ?)",
                (self.id, self.suit, self.rank, self.value)
            )
            con.commit()

        return self


class Hand(BaseModel):
    id: int
    name: str = 'Nueva Mano'
    player_turn: Optional[str]
    current_round: int = 0
    # table -> Cards played during the hand

    @classmethod
    def get_by_id(cls, hand_id: int):
        con = sqlite3.connect("db.sqlite3")
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("SELECT * FROM hand WHERE id = ?", (hand_id,))

        record = cur.fetchone()

        if record is None:
            raise NotFound

        hand = cls(**record)
        con.close()

        return hand

    @classmethod
    def get_current_players(cls, hand_id: int) -> List[Player]:
        con = sqlite3.connect("db.sqlite3")
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("SELECT * FROM player WHERE playing_hand = ?", (hand_id,))

        records = cur.fetchall()

        players = [Player(**player) for player in records]
        con.close()

        return players

    @classmethod
    def get_all(cls) -> List[Hand]:
        con = sqlite3.connect("db.sqlite3")
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("SELECT * FROM hand")

        records = cur.fetchall()

        if records is None:
            raise NotFound

        hands = [cls(**hand) for hand in records]
        con.close()

        return hands

    def update(self) -> Hand:
        with sqlite3.connect("db.sqlite3") as con:
            cur = con.cursor()
            cur.execute(
                "UPDATE hand SET name=?,player_turn=?,current_round=? WHERE hand_id = ?",
                (self.name, self.player_turn, self.current_round, self.id)
            )
            con.commit()

        return self

    def save(self) -> Hand:
        with sqlite3.connect("db.sqlite3") as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO hand (id,name,player_turn,current_round) VALUES(?, ?, ?, ?)",
                (self.id, self.name, self.player_turn, self.current_round)
            )
            con.commit()

        return self
