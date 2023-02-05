from datetime import datetime
import json
import pytest

from unittest import mock
from models.models import Player, Hand
from services.connection_manager import ConnectionManager
from events.socket_events import send_message, games_update, join_hand

pytest_plugins = ('pytest_asyncio',)


@pytest.fixture()
def mock_connection_manager():
    return mock.AsyncMock(ConnectionManager)


@pytest.fixture()
def mock_hand_manager():
    fake_hand = Hand()
    fake_hand.id = 0
    fake_hand.players = ['1234']
    fake_hand.player_hand = ""
    fake_hand.player_dealer = ""
    fake_hand.player_turn = ""
    fake_hand.name = 'Test'

    hand_manager = mock.MagicMock()
    hand_manager.avaliable_games.return_value = []
    hand_manager.get_hand.return_value = fake_hand

    return hand_manager


@pytest.fixture()
def mock_player_manager():
    player = Player()
    player.id = '1234'
    player.name = 'Anónimo'

    player_manager = mock.MagicMock()
    player_manager.find_player.return_value = player

    return player_manager

@pytest.mark.asyncio
async def test_send_message(mock_connection_manager, mock_player_manager):
    """ Tests that a message is sent correctly in the socket controller """

    await send_message(
            playerId='1234',
            message='test',
            connection_manager=mock_connection_manager,
            player_manager=mock_player_manager
            )

    data = json.dumps({
        "event": "message",
        "payload": {"message": {
            "text": 'test',
            "player": 'Anónimo',
            "time": str(datetime.now().strftime("%H:%M:%S"))
            }
        }})
    mock_connection_manager.broadcast.assert_called_once_with(json_string=data)


@pytest.mark.asyncio
async def test_games_update(mock_connection_manager, mock_hand_manager):
    """ Tests that a message is sent correctly in the socket controller """

    await games_update(
            connection_manager=mock_connection_manager,
            hand_manager=mock_hand_manager
            )
    data = json.dumps({
        "event": "gamesUpdate",
        "payload": {"gamesList": []}
        })
    mock_connection_manager.broadcast.assert_called_once_with(json_string=data)


@pytest.mark.asyncio
async def test_join_hand(mock_connection_manager, mock_hand_manager, mock_player_manager):

    await join_hand(
            handId=0,
            playerId='aaaa',
            connection_manager=mock_connection_manager,
            player_manager=mock_player_manager,
            hand_manager=mock_hand_manager
            )

    data = json.dumps({
            'event': 'joinedHand',
            'payload': {'handId': 0,
                        'name': 'Test',
                        'currentPlayers': [{'id': '1234', 'name': 'Anónimo'}],
                        'playerHand': '',
                        'playerDealer': ''
                        }
    })
    mock_connection_manager.send.assert_called_once_with(json_string=data, player_id='1234')
