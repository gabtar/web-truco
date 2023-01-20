import pytest

from api.models.models import Player, Hand, Card, Suit, Rank


def test_create_new_player():
    """ Tests that a new player is created succesfully """
    new_player = Player().save()

    player_from_db = Player.get_by_id(player_id=new_player.id)

    assert new_player.name == player_from_db.name
    assert new_player.id == player_from_db.id


def test_update_player():
    """ Tests that a can update a player's fields """
    new_player = Player().save()

    new_player.name = "NewName"
    new_player.update()

    player_from_db = Player.get_by_id(player_id=new_player.id)

    assert player_from_db.name == "NewName"


@pytest.mark.skip(reason="Necesita un db de pruebas sin cartas")
def test_create_card():
    card = Card(id=1, rank=Rank.CINCO, suit=Suit.ORO, value=1)
    card.save()

    card_from_db = Card.get_by_id(card.id)

    assert card.rank == card_from_db.rank
    assert card.suit == card_from_db.suit
    assert card.value == card_from_db.value


def test_add_new_hand():
    """ Test a new hand is created on db """
    hand = Hand(id=1).save()
    hand_from_db = Hand.get_by_id(hand_id=hand.id)

    assert hand_from_db.name == hand.name


def test_update_a_hand():
    """ Test a new hand is created on db """
    hand = Hand(id=1).save()
    hand.current_round = 2
    hand.update()

    hand_from_db = Hand.get_by_id(hand_id=hand.id)

    assert hand_from_db.current_round == 2


def test_get_current_hand_players():
    """ Test that a hand can return the players """
    player1 = Player().save()
    player2 = Player().save()

    hand = Hand(id=1).save()

    player1.playing_hand = hand.id
    player1.update()
    player2.playing_hand = hand.id
    player2.update()

    assert player1 in hand.get_current_players()
    assert player2 in hand.get_current_players()


def test_get_cards_dealed_to_player():
    """ Test that a hand can return the cards dealed to players """
    player1 = Player().save()
    card = Card.get_by_id(1)

    hand = Hand(id=1).save()

    hand.deal_card_to_player(player_id=player1.id, card_id=card.id)

    assert card in hand.get_cards_dealed(player_id=player1.id)


def test_play_a_card_in_a_hand():
    """ Tests that a card can be played on a hand """
    player1 = Player().save()
    card = Card.get_by_id(1)

    hand = Hand(id=1).save()

    hand.play_card(player_id=player1.id, card_id=card.id)

    card_played_in_db = hand.get_card_played(player_id=player1.id, round_number=0)

    assert card.id == card_played_in_db.id
    assert card.suit == card_played_in_db.suit
    assert card.rank == card_played_in_db.rank
    assert card.value == card_played_in_db.value


def test_get_all_hands():
    """ Test can get all hands """
    hand1 = Hand(id=1).save()
    hand2 = Hand(id=2).save()

    all_hands = Hand.get_all()

    assert hand1 in all_hands
    assert hand2 in all_hands
