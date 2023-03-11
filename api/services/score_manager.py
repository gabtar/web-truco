from models.models import Game, Hand, Score
from repositories.repository import (
        AbstractHandRepository, dep_hand_repository,
        AbstractScoreRepository, dep_scores_repository,
        AbstractGameRepository, dep_game_repository
)


class ScoreManager:
    """ Manages scores of hands of truco """
    _score_repository: AbstractScoreRepository
    _game_repository: AbstractGameRepository
    _hand_repository: AbstractHandRepository

    def __init__(
            self,
            score_repository: AbstractScoreRepository = dep_scores_repository(),
            game_repository: AbstractGameRepository = dep_game_repository(),
            hand_repository: AbstractHandRepository = dep_hand_repository(),
            ):
        self._score_repository = score_repository
        self._game_repository = game_repository
        self._hand_repository = hand_repository

    def get_score(self, game_id: int) -> Score:
        self._score_repository.get_by_id(id=game_id)

    def initialize_score(self, game_id: str) -> None:
        game: Game = self._game_repository.get_by_id(id=game_id)
        score: Score = Score()
        score.id = game_id
        for player in game.players:
            # TODO, En realidad el juego debearia tener los equipos
            score.score[player.id] = 0
        self._score_repository.save(score)

    def assign_truco_score(self, game_id: str) -> Score:
        # TODO get the hand and set the winner
        """ Assigns the score the the passed hand """
        score: Score = self._score_repository.get_by_id(id=game_id)
        hand: Hand = self._hand_repository.get_by_id(id=game_id)
        score.score[hand.winner] += hand.truco_status

        self._score_repository.update(score)
        return score

    def assign_envido_score(self, hand: Hand) -> Score:
        """ Assigns the score of the envido of the passed hand """
        score: Score = self._score_repository.get_by_id(id=hand.id)
        score.score[hand.envido.winner] += hand.envido.points

        self._score_repository.update(score)
        return score
