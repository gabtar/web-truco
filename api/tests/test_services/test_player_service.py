import pytest

from models.models import Player
from services.player_manager import PlayerManager
from repositories.repository import InMemoryPlayersRepository


@pytest.fixture()
def fake_player_repository():
    return InMemoryPlayersRepository()


def test_create_a_new_player(fake_player_repository):
    """ Tests that a player can create succesfully """
    repository = fake_player_repository
    player_manager = PlayerManager(repository)

    player: Player = player_manager.create()

    assert player is player_manager.find_player(player_id=player.id)
