from typing import Optional
from models.models import Player
from repositories.repository import AbstractPlayerRepository, dep_players_repository


class PlayerManager:
    """ Manages players of the game """
    _player_repository: AbstractPlayerRepository

    def __init__(self, players: AbstractPlayerRepository = dep_players_repository()):
        self._player_repository = players

    def create(self) -> Player:
        player = Player()
        player.name = f'Anónimo#{len(self._player_repository._players)}'
        self._player_repository.save(player)
        return player

    def find_player(self, player_id: str) -> Optional[Player]:
        return self._player_repository.get_by_id(id=player_id)
