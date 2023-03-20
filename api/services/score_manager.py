from models.models import Game, Hand, Score
from repositories.repository import (
        AbstractHandRepository, dep_hand_repository,
        AbstractScoreRepository, dep_scores_repository,
        AbstractGameRepository, dep_game_repository,
        AbstractPlayerRepository, dep_players_repository
)


class ScoreManager:
    """ Manages scores of hands of truco """
    _score_repository: AbstractScoreRepository
    _game_repository: AbstractGameRepository
    _hand_repository: AbstractHandRepository
    _player_repository: AbstractPlayerRepository

    def __init__(
            self,
            score_repository: AbstractScoreRepository = dep_scores_repository(),
            game_repository: AbstractGameRepository = dep_game_repository(),
            hand_repository: AbstractHandRepository = dep_hand_repository(),
            player_repository: AbstractPlayerRepository = dep_players_repository(),
            ):
        self._score_repository = score_repository
        self._game_repository = game_repository
        self._hand_repository = hand_repository
        self._player_repository = player_repository

    def get_score(self, game_id: str) -> Score:
        return self._score_repository.get_by_id(id=game_id)

    def initialize_score(self, game_id: str) -> Score:
        """ Initializes the score of a game """
        game: Game = self._game_repository.get_by_id(id=game_id)
        score: Score = Score()
        score.id = game_id
        for player in game.players:
            # TODO, En realidad el juego debearia tener los equipos
            score.score[player.id] = 0
        self._score_repository.save(score)
        return score

    def assign_truco_score(self, game_id: str) -> Score:
        """ Assigns the score the the passed hand """
        score: Score = self._score_repository.get_by_id(id=game_id)
        hand: Hand = self._hand_repository.get_by_id(id=game_id)
        score.score[hand.winner] += hand.truco_status

        self._score_repository.update(score=score)
        self._check_winner(game_id=hand.id)
        return score

    # TODO/REFACTOR, debería pasarle directamente el game_id
    def assign_envido_score(self, hand: Hand) -> Score:
        """ Assigns the score of the envido of the passed hand """
        score: Score = self._score_repository.get_by_id(id=hand.id)
        score.score[hand.envido.winner] += hand.envido.points

        self._score_repository.update(score=score)
        self._check_winner(game_id=hand.id)
        return score

    # TODO, define el ganador si alcanzo el max score de la partida
    def _check_winner(self, game_id: str) -> None:
        """ Sets the winner of a game (if exists) """
        game: Game = self._game_repository.get_by_id(id=game_id)
        score: Score = self._score_repository.get_by_id(id=game_id)

        for player, points in score.score.items():
            if points >= game.rules['max_score']:
                game.winner = self._player_repository.get_by_id(id=player)
                self._game_repository.update(game)
