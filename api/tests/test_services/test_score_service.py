import pytest

from models.models import Score, Hand, Card, Round, Game
from services.score_manager import ScoreManager
from repositories.repository import InMemoryScoreRepository


@pytest.fixture()
def fake_score_repository():
    return InMemoryScoreRepository()


def test_assing_score(fake_score_repository, fake_games_repository, fake_hands_repository, fake_players_repository):
    """ Test the score of a hand is assigned correctly """
    hand: Hand = fake_hands_repository.get_by_id('game1')
    player1 = fake_players_repository.get_by_id('player1')
    player2 = fake_players_repository.get_by_id('player2')

    # Playing in this order the winner of the hand is player 2
    cards_p1 = [Card(suit='E', rank='4'), Card(suit='B', rank='7')]
    cards_p2 = [Card(suit='C', rank='4'), Card(suit='C', rank='12')]

    hand.rounds = [
            Round(cards_played={player1.id: cards_p1[0], player2.id: cards_p2[0]}),
            Round(cards_played={player1.id: cards_p1[1], player2.id: cards_p2[1]})
    ]
    hand.winner = hand.check_winner

    score_manager = ScoreManager(
            score_repository=fake_score_repository,
            game_repository=fake_games_repository,
            hand_repository=fake_hands_repository
        )
    hand = fake_hands_repository.get_by_id(id='game1')
    score_repository = fake_score_repository
    game: Game = fake_games_repository.get_by_id(id='game1')

    score_manager.initialize_score(game_id=game.id)
    score_manager.assign_truco_score(game_id=game.id)

    hand_score: Score = score_repository.get_by_id(id=hand.id)

    assert hand_score.score[game.players[0].id] == 0
    assert hand_score.score[game.players[1].id] == 1
