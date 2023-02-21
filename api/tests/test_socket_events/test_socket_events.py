import json
import pytest

from datetime import datetime

from unittest import mock
from services.services import HandManager, PlayerManager
from services.connection_manager import ConnectionManager
from events.socket_events import SocketController

pytest_plugins = ('pytest_asyncio',)


@pytest.fixture()
def mock_connection_manager() -> mock.AsyncMock:
    return mock.AsyncMock(ConnectionManager)


@pytest.mark.asyncio
async def test_send_message(mock_connection_manager, fake_hands_repository, fake_players_repository):
    """ Tests that a message is sent correctly in the socket controller """
    socket = SocketController(
            connection_manager=mock_connection_manager,
            hand_manager=HandManager(hands=fake_hands_repository, players=fake_players_repository),
            player_manager=PlayerManager(players_repository=fake_players_repository)
            )
    await socket.call_event(event='message', payload={'playerId': '1', 'message': 'test'})

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
async def test_games_update(mock_connection_manager,fake_players_repository, fake_hands_repository):
    """ Tests that a message is sent correctly in the socket controller """
    socket = SocketController(
            connection_manager=mock_connection_manager,
            hand_manager=HandManager(hands=fake_hands_repository, players=fake_players_repository),
            player_manager=PlayerManager(players_repository=fake_players_repository)
            )
    await socket.call_event(event='gamesUpdate', payload={})

    expected_message = json.dumps({
        'event': 'gamesUpdate',
        'payload': {'gamesList': [{"id": 1, "name": "Nueva Mano", "currentPlayers": 0}]}
        })
    mock_connection_manager.broadcast.assert_called_once_with(json_string=expected_message)


@pytest.mark.asyncio
async def test_hand_update(mock_connection_manager, fake_players_repository, fake_hands_repository):
    """ Test updates the hand to all players playing/joined to the hand """
    socket = SocketController(
            connection_manager=mock_connection_manager,
            hand_manager=HandManager(hands=fake_hands_repository, players=fake_players_repository),
            player_manager=PlayerManager(players_repository=fake_players_repository)
            )
    await socket.call_event(event='handUpdate', payload={'hand_id': 0})

    expected_message = json.dumps({
        "event": "handUpdated",
        "payload": {
            "hand": {
                'id': 0, 'name': 'Nueva Mano',
                'players': [
                    {'id': '1', 'name': 'Anónimo'},
                    {'id': '2', 'name': 'Anónimo'}
                ],
                'player_turn': '2', 'chant_turn': '2', 'player_hand': '2',
                'player_dealer': '1', 'cards_dealed': [],
                'rounds': [{"cards_played": {"1": None, "2": None}}],
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
    mock_connection_manager.send.assert_called_with(json_string=expected_message, player_id='2')


@pytest.mark.asyncio
async def test_join_hand(
        mock_connection_manager, fake_players_repository, fake_hands_repository
        ):
    socket = SocketController(
            connection_manager=mock_connection_manager,
            hand_manager=HandManager(hands=fake_hands_repository, players=fake_players_repository),
            player_manager=PlayerManager(players_repository=fake_players_repository)
            )
    await socket.call_event(event='joinGame', payload={'handId': 1, 'playerId': '1'})
    """ Tests that a player can join a hand """
    expected_message = json.dumps({'event': 'joinedHand'})

    mock_connection_manager.send.assert_any_call(json_string=expected_message, player_id='1')
