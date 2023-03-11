import json
import pytest

from datetime import datetime

from unittest import mock
from services.connection_manager import ConnectionManager
from events.socket_events import SocketController
from services.hand_manager import HandManager
from services.player_manager import PlayerManager
from services.game_manager import GameManager

pytest_plugins = ('pytest_asyncio',)


@pytest.fixture()
def mock_connection_manager() -> mock.AsyncMock:
    return mock.AsyncMock(ConnectionManager)


@pytest.fixture()
def fake_hand_manager(fake_players_repository, fake_hands_repository, fake_games_repository):
    return HandManager(
            hands=fake_hands_repository,
            players=fake_players_repository,
            games=fake_games_repository
        )


@pytest.fixture()
def fake_game_manager(fake_games_repository, fake_players_repository):
    return GameManager(games=fake_games_repository, players=fake_players_repository)


@pytest.fixture()
def fake_player_manager(fake_players_repository):
    return PlayerManager(players=fake_players_repository)


@pytest.mark.asyncio
async def test_send_message(mock_connection_manager, fake_player_manager, fake_hand_manager, fake_game_manager):
    """ Tests that a message is sent correctly in the socket controller """
    socket = SocketController(
            connection_manager=mock_connection_manager,
            game_manager=fake_game_manager,
            hand_manager=fake_hand_manager,
            player_manager=fake_player_manager
            )
    await socket.call_event(event='message', payload={'playerId': 'player1', 'message': 'test'})

    expected_message = json.dumps({
        'event': 'message',
        'payload': {'message': {
            'text': 'test',
            'player': 'Anónimo',
            'time': str(datetime.now().strftime('%H:%M:%S'))
            }
        }})
    mock_connection_manager.broadcast.assert_called_once_with(json_string=expected_message)


@pytest.mark.asyncio
async def test_games_update(mock_connection_manager, fake_game_manager):
    """ Tests that a message is sent correctly in the socket controller """
    socket = SocketController(
            connection_manager=mock_connection_manager,
            game_manager=fake_game_manager
            )
    await socket.call_event(event='gamesUpdate', payload={})

    expected_message = json.dumps({
        'event': 'gamesUpdate',
        'payload': {'gamesList': [{"id": "game0", "name": "Nueva partida", "currentPlayers": 0}]}
        })
    mock_connection_manager.broadcast.assert_called_once_with(json_string=expected_message)


@pytest.mark.asyncio
async def test_hand_update(mock_connection_manager, fake_player_manager, fake_hand_manager, fake_game_manager):
    """ Test updates the hand to all players playing/joined to the hand """
    socket = SocketController(
            connection_manager=mock_connection_manager,
            game_manager=fake_game_manager,
            hand_manager=fake_hand_manager,
            player_manager=fake_player_manager
            )
    await socket.call_event(event='handUpdate', payload={'hand_id': 'game1'})

    expected_message = json.dumps({
        "event": "handUpdated",
        "payload": {
            "hand": {
                'id': 'game1',
                'player_turn': 'player2', 'chant_turn': 'player2', 'player_hand': 'player2',
                'player_dealer': 'player1', 'cards_dealed': [],
                'rounds': [{"cards_played": {"player1": None, "player2": None}}],
                'envido': {
                    "chanted": [], "points": 0,
                    "cards_played": {}, "winner": None,
                    "status": "NOT_STARTED"
                },
                'truco_status': 1, 'winner': None,
                'status': 'IN_PROGRESS',
                }
            }
        })
    mock_connection_manager.send.assert_called_with(json_string=expected_message, player_id='player2')


@pytest.mark.asyncio
async def test_join_hand(mock_connection_manager, fake_player_manager, fake_hand_manager, fake_game_manager):
    socket = SocketController(
            connection_manager=mock_connection_manager,
            game_manager=fake_game_manager,
            hand_manager=fake_hand_manager,
            player_manager=fake_player_manager
            )
    await socket.call_event(event='joinGame', payload={'gameId': 'game0', 'playerId': 'player1'})
    """ Tests that a player can join a hand """
    expected_message = json.dumps({'event': 'joinedHand'})

    mock_connection_manager.send.assert_any_call(json_string=expected_message, player_id='player1')
