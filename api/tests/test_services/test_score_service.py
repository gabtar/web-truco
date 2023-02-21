import pytest

from models.models import Score, Hand, Card, Round
from services.services import ScoreManager
from repositories.repository import InMemoryScoreRepository, InMemoryGamesRepository


@pytest.fixture()
def fake_hands_repository(fake_players_repository):
    hand = Hand(id=0)
    player1 = fake_players_repository.get_by_id(id='1')
    player2 = fake_players_repository.get_by_id(id='2')
    hand.player_dealer = player1.id
    hand.player_hand = player2.id
    hand.player_turn = player2.id
    hand.players.extend([player1, player2])

    # Playing in this order the winner of the hand is player 2
    cards_p1 = [Card(suit='E', rank='4'), Card(suit='B', rank='7')]
    cards_p2 = [Card(suit='C', rank='4'), Card(suit='C', rank='12')]

    hand.rounds = [
            Round(cards_played={player1.id: cards_p1[0], player2.id: cards_p2[0]}),
            Round(cards_played={player1.id: cards_p1[1], player2.id: cards_p2[1]})
    ]

    fake_repository = InMemoryGamesRepository()
    fake_repository.save(hand)

    return fake_repository


@pytest.fixture()
def fake_score_repository():
    return InMemoryScoreRepository()


def test_assing_score(fake_score_repository, fake_hands_repository):
    """ Test the score of a hand is assigned correctly """
    score_manager = ScoreManager(score_repository=fake_score_repository)
    hand = fake_hands_repository.get_by_id(id=0)
    hand.winner = hand.players[1].id
    score_repository = fake_score_repository

    score_manager.initialize_score(hand=hand)
    score_manager.assign_truco_score(hand=hand)

    hand_score: Score = score_repository.get_by_id(id=hand.id)

    assert hand_score.score[hand.players[0].id] == 0
    assert hand_score.score[hand.players[1].id] == 1
