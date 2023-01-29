import pytest
import uuid

from models.models import Score, Hand, Card
from services.services import ScoreManager
from repositories.repository import InMemoryScoreRepository, InMemoryGamesRepository


@pytest.fixture()
def fake_hands_repository():
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

    # Playing in this order the winner of the hand is player 2
    cards_p1 = [Card(suit='E', rank='4'), Card(suit='E', rank='7'), Card(suit='O', rank='4')]
    cards_p2 = [Card(suit='E', rank='2'), Card(suit='C', rank='4'), Card(suit='B', rank='3')]

    hand.cards_played[players[0]] = cards_p1
    hand.cards_played[players[1]] = cards_p2

    fake_repository = InMemoryGamesRepository()
    fake_repository.save(hand)

    return fake_repository


@pytest.fixture()
def fake_score_repository():
    return InMemoryScoreRepository()


def test_check_round_winner(fake_score_repository, fake_hands_repository):
    """ Tests that the winner of each round of the fake hand """
    score_manager = ScoreManager(score_repository=fake_score_repository)

    hand = fake_hands_repository.get_by_id(id=0)

    first_round_winner = score_manager.check_round_winner(hand=hand, round_number=0)
    second_round_winner = score_manager.check_round_winner(hand=hand, round_number=1)
    third_round_winner = score_manager.check_round_winner(hand=hand, round_number=2)

    assert first_round_winner == hand.players[1]
    assert second_round_winner == hand.players[0]
    assert third_round_winner == hand.players[1]


def test_hand_winner(fake_score_repository, fake_hands_repository):
    """ Test the winner of a hand """
    score_manager = ScoreManager(score_repository=fake_score_repository)
    hand = fake_hands_repository.get_by_id(id=0)

    hand_winner = score_manager.hand_winner(hand=hand)

    assert hand_winner == hand.players[1]


def test_assing_score(fake_score_repository, fake_hands_repository):
    """ Test the score of a hand is assigned correctly """
    score_manager = ScoreManager(score_repository=fake_score_repository)
    hand = fake_hands_repository.get_by_id(id=0)
    score_repository = fake_score_repository

    score_manager.initialize_score(hand=hand)
    score_manager.assign_score(hand=hand)

    hand_score: Score = score_repository.get_by_id(id=0)

    assert hand_score.score[hand.players[0]] == 0
    assert hand_score.score[hand.players[1]] == 1
