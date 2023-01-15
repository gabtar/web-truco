import pytest

from api.models.models import Player, Hand, PlayerCard, Card, Suit, Rank


def test_create_new_player():
    """ Tests that a new player is created succesfully """
    new_player = Player().save()

    player_from_db = Player.get_by_id(id=new_player.id)

    assert new_player.name == player_from_db.name
    assert new_player.id == player_from_db.id


def test_update_player():
    """ Tests that a can update a player's fields """
    new_player = Player().save()

    new_player.name = "NewName"
    new_player.update()

    player_from_db = Player.get_by_id(id=new_player.id)

    assert player_from_db.name == "NewName"


def test_create_card():
    card = Card(id=1, rank=Rank.CINCO, suit=Suit.ORO, value=1)
    card.save()

    card_from_db = Card.get_by_id(card.id)

    assert card.rank == card_from_db.rank
    assert card.suit == card_from_db.suit
    assert card.value == card_from_db.value


def test_add_card_to_player():
    card = Card(id=2, rank=Rank.SEIS, suit=Suit.ORO, value=2).save()
    new_player = Player().save()

    PlayerCard(player_id=new_player.id, card_id=card.id).save()

    assert card in PlayerCard.get_cards_by_player_id(player_id=new_player.id)


def test_add_new_hand():
    hand = Hand(id=1).save()
    hand_from_db = Hand.get_by_id(hand_id=hand.id)

    assert hand_from_db.name == hand.name
