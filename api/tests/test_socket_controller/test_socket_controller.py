import pytest

from models.models import Player
from events.socket_events import dep_socket_controller
from repositories.repository import InMemoryPlayersRepository


# TODO, test socket events
def test_updates_current_games(fake_player_repository):
    """ Tests that updates the current games to all players """
    # Debería tener un mock del conection manager
    # socket_controller = dep_socket_controller()
    # Assert se llamó al método del connection manager# con los argumentos?



    
