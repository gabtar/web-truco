from __future__ import annotations
import uuid
import os
import sqlite3

from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional


def get_connection():
    """
    Helper for database connection
    If tests are running will return a connection to a test db
    """
    con = sqlite3.connect(os.getenv("TEST_DB", "db.sqlite3"))
    con.row_factory = sqlite3.Row

    return con


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
    name: str = "Anónimo"
    playing_hand: Optional[int]

    @classmethod
    def get_by_id(cls, player_id: str) -> Player:
        con = get_connection()

        cur = con.cursor()
        cur.execute("SELECT * FROM player WHERE id = ?", (player_id,))

        record = cur.fetchone()

        if record is None:
            raise NotFound

        player = cls(**record)
        con.close()

        return player

    def update(self) -> Player:
        with get_connection() as con:
            cur = con.cursor()
            cur.execute(
                "UPDATE player SET name=?,playing_hand=? WHERE id = ?",
                (self.name, self.playing_hand, self.id)
            )
            con.commit()

        return self

    def save(self) -> Player:
        with get_connection() as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO player (id,name) VALUES(?, ?)",
                (self.id, self.name)
            )
            con.commit()

        return self


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
        con = get_connection()

        cur = con.cursor()
        cur.execute("SELECT * FROM card WHERE id = ?", (id,))

        record = cur.fetchone()

        if record is None:
            raise NotFound

        card = cls(**record)
        con.close()

        return card

    def save(self) -> Card:
        with get_connection() as con:
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
    player_turn: Optional[str] # Al jugador que le toca tirar carta
    player_hand: Optional[str] # El jugador que es mano
    current_round: int = 0

    @classmethod
    def get_by_id(cls, hand_id: int):
        con = get_connection()

        cur = con.cursor()
        cur.execute("SELECT * FROM hand WHERE id = ?", (hand_id,))

        record = cur.fetchone()

        if record is None:
            raise NotFound

        hand = cls(**record)
        con.close()

        return hand

    def get_current_players(self) -> List[Player]:
        """ Returns the current players of the hand """
        con = get_connection()

        cur = con.cursor()
        cur.execute("SELECT * FROM player WHERE playing_hand = ?", (self.id,))

        records = cur.fetchall()

        players = [Player(**player) for player in records]
        con.close()

        return players

    def get_cards_dealed(self, player_id: str) -> List[Card]:
        """ Gets the cards dealed to player """
        con = get_connection()

        cur = con.cursor()
        cur.execute("SELECT * FROM playercard WHERE player_id = ?", (player_id,))

        records = cur.fetchall()

        cards = [Card.get_by_id(card[1]) for card in records]
        con.close()

        return cards

    # TODO tendría que tener un método para resetear la mano/devolver 
    # las cartas al mazo y limpiar las relaciones?
    def deal_card_to_player(self, player_id: str, card_id: int) -> Card:
        """ Insert card/player relation in current hand """
        with get_connection() as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO playercard (player_id, card_id) VALUES(?, ?)",
                (player_id, card_id)
            )
            con.commit()

        return Card.get_by_id(card_id)


    def play_card(self, player_id: str, card_id: int) -> Card:
        """ Inserts the relation with the round table in sqlite """
        with get_connection() as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO round (hand_id, card_id, player_id, round_number) VALUES(?, ?, ?, ?)",
                (self.id, card_id, player_id, self.current_round)
            )
            con.commit()

        return Card.get_by_id(card_id)

    def get_card_played(self, player_id: str, round_number: int) -> Optional[Card]:
        """ Gets the card played by player in an specific round of the hand """
        con = get_connection()

        cur = con.cursor()
        cur.execute("SELECT card_id FROM round WHERE hand_id = ? AND player_id = ? AND round_number = ? ", (self.id, player_id, round_number))

        record = cur.fetchone()

        if record is None:
            con.close()
            return None

        card = Card.get_by_id(record[0])
        con.close()

        return card

    @classmethod
    def get_all(cls) -> List[Hand]:
        con = get_connection()

        cur = con.cursor()
        cur.execute("SELECT * FROM hand")

        records = cur.fetchall()

        if records is None:
            raise NotFound

        hands = [cls(**hand) for hand in records]
        con.close()

        return hands

    def update(self) -> Hand:
        with get_connection() as con:
            cur = con.cursor()
            cur.execute(
                "UPDATE hand SET name=?,player_turn=?,player_hand=?,current_round=? WHERE id = ?",
                (self.name, self.player_turn, self.player_hand, self.current_round, self.id)
            )
            con.commit()

        return self

    def save(self) -> Hand:
        with get_connection() as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO hand (id,name,player_turn,player_hand,current_round) VALUES(?, ?, ?, ?, ?)",
                (self.id, self.name, self.player_turn, self.player_hand, self.current_round)
            )
            con.commit()

        return self
