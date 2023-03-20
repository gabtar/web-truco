import uuid

from typing import List, Optional, Dict, Union
from models.models import Game
from services.exceptions import GameException

from repositories.repository import (
        AbstractPlayerRepository, dep_players_repository,
        AbstractGameRepository, dep_game_repository,
)


class GameManager:
    """ Manages games of truco """
    _game_repository: AbstractGameRepository
    _player_repository: AbstractPlayerRepository

    def __init__(self,
                 games: AbstractGameRepository = dep_game_repository(),
                 players: AbstractPlayerRepository = dep_players_repository(),
                 ):
        self._game_repository = games
        self._player_repository = players

    def get_game(self, id: str) -> Optional[Game]:
        """ Returns a game """
        return self._game_repository.get_by_id(id=id)

    def create(self, rules: Dict[str, Union[int, bool]]) -> Game:
        """ Creates a new game of truco in the server """
        game: Game = Game(rules=rules)
        game.id = str(uuid.uuid4())
        self._game_repository.save(game)

        return game

    def join_game(self, game_id: str, player_id: str) -> None:
        """ Joins the passed player to the passed game_id """
        game: Game = self._game_repository.get_by_id(id=game_id)

        if len(game.players) >= game.rules['num_players']:
            raise GameException('Partida completa')

        game.players.append(self._player_repository.get_by_id(id=player_id))

    def get_available_games(self) -> List[Game]:
        """ Returns available games to join """
        return self._game_repository.avaliable_games()


def dep_game_manager():
    return GameManager()
