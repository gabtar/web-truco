import pytest
import uuid

from typing import List
from models.in_memory_models import Hand
from repositories.repository import InMemoryGamesRepository
from services.services import HandManager, GameException
# from unittest import mock


@pytest.fixture()
def fake_hands_repository() -> List[Hand]:
    return InMemoryGamesRepository()


@pytest.fixture()
def fake_empty_hand() -> Hand:
    hand = Hand(id=0)
    return hand


@pytest.fixture()
def fake_full_hand() -> Hand:
    hand = Hand(id=0)
    players = [uuid.uuid4(), uuid.uuid4()]
    hand.cards_dealed[players[0]] = []
    hand.cards_dealed[players[1]] = []
    hand.cards_played[players[0]] = []
    hand.cards_played[players[1]] = []
    hand.current_round = 0
    hand.player_dealer = players[0]
    hand.player_hand = players[1]
    hand.player_turn = players[1]
    hand.players.extend(players)
    return hand


def test_create_new_hand(fake_hands_repository):
    """ Test that a new hand is created """
    hand_manager = HandManager(hands=fake_hands_repository)
    player_id = 'aaaaaaaa'

    hand_id = hand_manager.new_hand(player_id=player_id)

    assert fake_hands_repository.get_by_id(id=hand_id) is not None


def test_join_hand(fake_hands_repository):
    """ Test that a user can join to an open hand"""
    hand_manager = HandManager(hands=fake_hands_repository)
    player_one_id = 'aaaaaaaa'
    player_two_id = 'bbbbbbbb'

    hand_id = hand_manager.new_hand(player_id=player_one_id)
    hand_manager.join_hand(player_id=player_one_id, hand_id=hand_id)
    hand_manager.join_hand(player_id=player_two_id, hand_id=hand_id)

    assert player_one_id in fake_hands_repository.get_by_id(id=hand_id).players
    assert player_two_id in fake_hands_repository.get_by_id(id=hand_id).players


def test_cannot_join_hand_when_is_complete(fake_full_hand, fake_hands_repository):
    """ Test that a user cannot join a hand when it's full"""
    hand_manager = HandManager(hands=fake_hands_repository)
    player_three_id = uuid.uuid4()
    hand_id = 0

    fake_hands_repository.save(fake_full_hand)

    with pytest.raises(GameException) as excep:
        hand_manager.join_hand(hand_id=hand_id, player_id=player_three_id)

    assert "Partida completa" in str(excep)
    assert player_three_id not in fake_hands_repository.get_by_id(id=hand_id).players


def test_when_player_completes_a_hand_is_automatically_initialized(fake_empty_hand, fake_hands_repository):
    """ Tests that when a player join completes a hand, the hand is started """
    hand_manager = HandManager(fake_hands_repository)

    player_one_id = 'aaaaaaaa'
    player_two_id = 'bbbbbbbb'
    hand_id = hand_manager.new_hand(player_id=player_one_id)
    new_hand = fake_hands_repository.get_by_id(id=hand_id)
    hand_manager.join_hand(player_id=player_one_id, hand_id=hand_id)
    hand_manager.join_hand(player_id=player_two_id, hand_id=hand_id)

    assert new_hand.current_round == 0
    assert new_hand.player_dealer is not None
    assert new_hand.player_turn is not None
    assert new_hand.player_hand is not None


def test_avaliable_games(fake_full_hand, fake_hands_repository):
    """ Test that returns all avaliable games to join"""
    full_hand = fake_full_hand
    empty_hand = Hand(id=1)
    fake_hands_repository.save(full_hand)
    fake_hands_repository.save(empty_hand)

    hand_manager = HandManager(fake_hands_repository)
    available_games = hand_manager.avaliable_games()

    assert empty_hand in available_games
    assert full_hand not in available_games


def test_can_deal_cards_in_a_hand(fake_full_hand, fake_hands_repository):
    """ Test that the hand player can deal in a hand """
    fake_hands_repository.save(fake_full_hand)
    hand = fake_hands_repository.get_by_id(id=0)
    players = hand.players

    hand_manager = HandManager(fake_hands_repository)

    cards_dealed = hand_manager.deal_cards(player_id=players[0], hand_id=0)

    assert cards_dealed == hand.cards_dealed


def test_cannot_deal_cards_if_hand_is_still_open(fake_hands_repository):
    """ Test that returns all avaliable games to join"""
    hand_manager = HandManager(fake_hands_repository)
    player_id = 'aaaaaaaa'

    hand_id = hand_manager.new_hand(player_id=player_id)
    hand_manager.join_hand(hand_id=hand_id, player_id=player_id)

    with pytest.raises(GameException) as excep:
        hand_manager.deal_cards(player_id=player_id, hand_id=hand_id)

    assert "Acción inválida" in str(excep)


def test_cannot_deal_cards_if_is_not_the_dealer(fake_hands_repository):
    """ Tests tha cannot deal cards if the player is not the dealer of the hand """
    hand_manager = HandManager(fake_hands_repository)
    player_id = 'aaaaaaaa'
    player_id_two = 'bbbbbbbb'

    hand_id = hand_manager.new_hand(player_id=player_id)
    hand_manager.join_hand(hand_id=hand_id, player_id=player_id)
    hand_manager.join_hand(hand_id=hand_id, player_id=player_id_two)

    with pytest.raises(GameException) as excep:
        hand_manager.deal_cards(player_id=player_id_two, hand_id=hand_id)

    assert "Acción inválida" in str(excep)


def test_play_card(fake_hands_repository, fake_full_hand):
    """ Test that a player can play a card """
    hand = fake_full_hand
    hands_repository = fake_hands_repository
    hands_repository.save(hand)
    hand_manager = HandManager(hands_repository)
    hand_manager.initialize_hand(hand.id)

    # He has the initial turn in the first round
    player_hand = hand.player_hand
    cards_dealed = hand_manager.deal_cards(player_id=hand.player_dealer, hand_id=hand.id)
    suit = cards_dealed[player_hand][0].suit
    rank = cards_dealed[player_hand][0].rank

    hand_manager.play_card(player_id=player_hand,
                           hand_id=hand.id,
                           suit=suit,
                           rank=rank)

    assert hand.cards_played[player_hand][0].suit == suit
    assert hand.cards_played[player_hand][0].rank == rank
    assert hand.current_round == 0


def test_play_card_advances_to_next_round_when_all_players_played_a_card(
        fake_hands_repository, fake_full_hand):
    """ Tests that when all players plays a card the hand advances to next round """
    hand = fake_full_hand
    hands_repository = fake_hands_repository
    hands_repository.save(hand)
    hand_manager = HandManager(hands_repository)
    hand_manager.initialize_hand(hand.id)

    # He has the initial turn in the first round
    player_hand = hand.player_hand
    player_dealer = hand.player_dealer
    cards_dealed = hand_manager.deal_cards(player_id=hand.player_dealer, hand_id=hand.id)

    hand_manager.play_card(player_id=player_hand,
                           hand_id=hand.id,
                           suit=cards_dealed[player_hand][0].suit,
                           rank=cards_dealed[player_hand][0].rank)
    hand_manager.play_card(player_id=player_dealer,
                           hand_id=hand.id,
                           suit=cards_dealed[player_dealer][0].suit,
                           rank=cards_dealed[player_dealer][0].rank)

    assert hand.current_round == 1


def test_cannot_play_a_card_that_has_not_been_dealed_to_player(
        fake_hands_repository, fake_full_hand
        ):
    """ Test that a player cannot play a card he does not own """
    hand = fake_full_hand
    hands_repository = fake_hands_repository
    hands_repository.save(hand)
    hand_manager = HandManager(hands_repository)
    hand_manager.initialize_hand(hand.id)

    player_hand = hand.player_hand

    with pytest.raises(GameException) as excep:
        hand_manager.play_card(player_id=player_hand,
                               hand_id=hand.id,
                               suit='E',
                               rank='1')

    assert 'No tienes ésa carta' in str(excep)


def test_cannot_play_a_card_when_its_not_player_turn(
        fake_hands_repository, fake_full_hand
        ):
    """ Test that a player cannot play a if it is not his turn"""
    hand = fake_full_hand
    hands_repository = fake_hands_repository
    hands_repository.save(hand)
    hand_manager = HandManager(hands_repository)
    hand_manager.initialize_hand(hand.id)

    # It's not hes turn because he is the dealer
    player_dealer = hand.player_dealer

    cards_dealed = hand_manager.deal_cards(player_id=hand.player_dealer, hand_id=hand.id)
    suit = cards_dealed[player_dealer][0].suit
    rank = cards_dealed[player_dealer][0].rank

    with pytest.raises(GameException) as excep:
        hand_manager.play_card(player_id=player_dealer,
                               hand_id=hand.id,
                               suit=suit,
                               rank=rank)

    assert 'No es tu turno' in str(excep)
    assert not hand.cards_played[player_dealer]


