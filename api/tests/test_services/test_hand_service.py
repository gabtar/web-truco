import pytest
import uuid

from models.models import Hand
from services.services import HandManager, GameException


def test_create_new_hand(fake_hands_repository):
    """ Test that a new hand is created """
    hand_manager = HandManager(hands=fake_hands_repository)
    player_id = 'aaaaaaaa'

    hand_id = hand_manager.new_hand(player_id=player_id)

    assert fake_hands_repository.get_by_id(id=hand_id) is not None


def test_join_hand(fake_hands_repository, fake_players_repository):
    """ Test that a user can join to an open hand"""
    hand_manager = HandManager(hands=fake_hands_repository, players=fake_players_repository)

    hand_id = hand_manager.new_hand(player_id='1')
    hand_manager.join_hand(player_id='1', hand_id=hand_id)
    hand_manager.join_hand(player_id='2', hand_id=hand_id)

    assert fake_players_repository.get_by_id(id='1') in fake_hands_repository.get_by_id(id=hand_id).players
    assert fake_players_repository.get_by_id(id='2') in fake_hands_repository.get_by_id(id=hand_id).players


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


def test_when_player_completes_a_hand_is_automatically_initialized(
        fake_empty_hand,
        fake_hands_repository,
        fake_players_repository
        ):
    """ Tests that when a player join completes a hand, the hand is started """
    hand_manager = HandManager(hands=fake_hands_repository, players=fake_players_repository)
    player1 = fake_players_repository.get_by_id(id='1')
    player2 = fake_players_repository.get_by_id(id='2')

    hand_id = hand_manager.new_hand(player_id=player1.id)
    new_hand = fake_hands_repository.get_by_id(id=hand_id)
    hand_manager.join_hand(player_id=player1.id, hand_id=hand_id)
    hand_manager.join_hand(player_id=player2.id, hand_id=hand_id)

    assert len(new_hand.rounds) == 1
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

    cards_dealed = hand_manager.deal_cards(player_id=hand.player_dealer, hand_id=0)

    assert cards_dealed == hand.cards_dealed


def test_cannot_deal_cards_if_hand_is_still_open(fake_hands_repository, fake_players_repository):
    """ Test that returns all avaliable games to join"""
    hand_manager = HandManager(hands=fake_hands_repository, players=fake_players_repository)

    hand_id = hand_manager.new_hand(player_id='1')
    hand_manager.join_hand(hand_id=hand_id, player_id='1')

    with pytest.raises(GameException) as excep:
        hand_manager.deal_cards(player_id='1', hand_id=hand_id)

    assert "Acción inválida" in str(excep)


def test_cannot_deal_cards_if_is_not_the_dealer(fake_hands_repository, fake_players_repository):
    """ Tests that cannot deal cards if the player is not the dealer of the hand """
    hand_manager = HandManager(hands=fake_hands_repository, players=fake_players_repository)

    hand_id = hand_manager.new_hand(player_id='1')
    hand_manager.join_hand(hand_id=hand_id, player_id='1')
    hand_manager.join_hand(hand_id=hand_id, player_id='2')

    with pytest.raises(GameException) as excep:
        player_hand = hand_manager.get_hand(id=hand_id).player_hand
        hand_manager.deal_cards(player_id=player_hand, hand_id=hand_id)

    assert "Acción inválida" in str(excep)


def test_play_card(fake_hands_repository, fake_full_hand):
    """ Test that a player can play a card """
    hand = fake_full_hand
    hands_repository = fake_hands_repository
    hands_repository.save(hand)
    hand_manager = HandManager(hands_repository)

    # He has the initial turn in the first round
    player_hand = hand.player_hand
    cards_dealed = hand_manager.deal_cards(player_id=hand.player_dealer, hand_id=hand.id)
    suit = cards_dealed[player_hand][0].suit
    rank = cards_dealed[player_hand][0].rank

    hand_manager.play_card(player_id=player_hand,
                           hand_id=hand.id,
                           suit=suit,
                           rank=rank)

    assert hand.rounds[0].cards_played[player_hand].suit == suit
    assert hand.rounds[0].cards_played[player_hand].rank == rank


def test_play_card_advances_to_next_round_when_all_players_played_a_card(
        fake_hands_repository, fake_full_hand):
    """ Tests that when all players plays a card the hand advances to next round """
    hand = fake_full_hand
    hands_repository = fake_hands_repository
    hands_repository.save(hand)
    hand_manager = HandManager(hands_repository)

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

    assert len(hand.rounds) == 2


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
    assert hand.rounds[0].cards_played[player_dealer] is None
