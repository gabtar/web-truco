import uuid

from typing import List, Optional, Dict, Union
from models.models import Game, Hand
from services.exceptions import GameException
from services.hand_manager import HandManager
from services.score_manager import ScoreManager

from repositories.repository import (
        AbstractPlayerRepository, dep_players_repository,
        AbstractGameRepository, dep_game_repository,
        AbstractHandRepository, dep_hand_repository
)


class GameManager:
    """ Manages games of truco """
    _game_repository: AbstractGameRepository
    _player_repository: AbstractPlayerRepository
    _hand_manager: HandManager = HandManager()
    _score_manager: ScoreManager = ScoreManager()

    def __init__(self,
                 games: AbstractGameRepository = dep_game_repository(),
                 players: AbstractPlayerRepository = dep_players_repository(),
                 hands: AbstractHandRepository = dep_hand_repository()
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

    def join_game(self, game_id: str, player_id: str) -> Game:
        """ Joins the passed player to the passed game_id """
        game: Game = self._game_repository.get_by_id(id=game_id)

        if len(game.players) >= game.rules['num_players']:
            raise GameException('Partida completa')

        game.players.append(self._player_repository.get_by_id(id=player_id))

        # Initialize hand if game is full of players
        if len(game.players) == game.rules['num_players']:
            game.status = 'STARTED'
            self._hand_manager.new_hand(game_id=game_id)
            self._hand_manager.initialize_hand(hand_id=game_id)
            self._score_manager.initialize_score(game_id=game_id)

        self._game_repository.update(game)
        return game

    def get_available_games(self) -> List[Game]:
        """ Returns available games to join """
        return self._game_repository.avaliable_games()

    def remove_game(self, gameId: str) -> None:
        """ Deletes the game from server """
        game: Game = self.get_game(id=gameId)
        hand: Hand = self._hand_repository.get_by_id(id=gameId)
        self._game_repository.remove(game)
        self._hand_repository.remove(hand)


def dep_game_manager():
    return GameManager()
