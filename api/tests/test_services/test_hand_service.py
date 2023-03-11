import pytest

from models.models import Hand
from services.hand_manager import HandManager
from services.exceptions import GameException


def test_create_new_hand(fake_hands_repository, fake_games_repository):
    """ Test that a new hand is created """
    hand_manager = HandManager(hands=fake_hands_repository)
    game_id = fake_games_repository.get_by_id(id='game1')

    hand_manager.new_hand(game_id=game_id)

    assert fake_hands_repository.get_by_id(id=game_id) is not None


def test_when_player_completes_a_hand_is_automatically_initialized(
        fake_hands_repository,
        fake_players_repository,
        fake_games_repository
        ):
    """ Tests that when a player join completes a hand, the hand is started """
    hand_manager = HandManager(hands=fake_hands_repository, players=fake_players_repository, games=fake_games_repository)

    game_id = fake_games_repository.get_by_id(id='game1').id

    hand_manager.new_hand(game_id=game_id)
    new_hand = fake_hands_repository.get_by_id(id=game_id)
    hand_manager.initialize_hand(hand_id=game_id)

    assert len(new_hand.rounds) == 1
    assert new_hand.player_dealer is not None
    assert new_hand.player_turn is not None
    assert new_hand.player_hand is not None


def test_can_deal_cards_in_a_hand(fake_full_hand, fake_players_repository, fake_hands_repository, fake_games_repository):
    """ Test that the hand player can deal in a hand """
    hand = fake_hands_repository.get_by_id(id='game1')

    hand_manager = HandManager(
            hands=fake_hands_repository,
            players=fake_players_repository,
            games=fake_games_repository
    )

    cards_dealed = hand_manager.deal_cards(player_id=hand.player_dealer, hand_id='game1')

    assert cards_dealed == hand.cards_dealed


def test_cannot_deal_cards_if_is_not_the_dealer(fake_hands_repository, fake_players_repository, fake_games_repository):
    """ Test that returns all avaliable games to join"""
    hand_manager = HandManager(
            hands=fake_hands_repository,
            players=fake_players_repository,
            games=fake_games_repository
    )

    # Add only 1 player to the empty game
    game = fake_games_repository.get_by_id(id='game0')
    game.players.append(fake_players_repository.get_by_id('player1'))

    with pytest.raises(GameException) as excep:
        hand_manager.deal_cards(player_id='player1', hand_id='game0')

    assert "Acción inválida" in str(excep)


def test_play_card(fake_hands_repository, fake_players_repository, fake_games_repository):
    """ Test that a player can play a card """
    hand_manager = HandManager(
            hands=fake_hands_repository,
            players=fake_players_repository,
            games=fake_games_repository
    )

    hand: Hand = hand_manager.get_hand(id='game1')

    # player_hand always has the initial turn in the first round
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
            fake_hands_repository, fake_players_repository, fake_games_repository
        ):
    """ Tests that when all players plays a card the hand advances to next round """
    hand_manager = HandManager(
            hands=fake_hands_repository,
            players=fake_players_repository,
            games=fake_games_repository
    )
    hand: Hand = hand_manager.get_hand(id='game1')

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
            fake_hands_repository, fake_players_repository, fake_games_repository
        ):
    """ Test that a player cannot play a card he does not own """
    hand_manager = HandManager(
            hands=fake_hands_repository,
            players=fake_players_repository,
            games=fake_games_repository
    )
    hand: Hand = hand_manager.get_hand(id='game1')

    player_hand = hand.player_hand

    with pytest.raises(GameException) as excep:
        hand_manager.play_card(player_id=player_hand,
                               hand_id=hand.id,
                               suit='E',
                               rank='1')

    assert 'No tienes ésa carta' in str(excep)


def test_cannot_play_a_card_when_its_not_player_turn(
            fake_hands_repository, fake_players_repository, fake_games_repository
        ):
    """ Test that a player cannot play a if it is not his turn"""
    hand_manager = HandManager(
            hands=fake_hands_repository,
            players=fake_players_repository,
            games=fake_games_repository
    )
    hand: Hand = hand_manager.get_hand(id='game1')

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
