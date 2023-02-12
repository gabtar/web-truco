import pytest

from repositories.repository import InMemoryGamesRepository, InMemoryPlayersRepository
from models.models import Player, Hand, Round


@pytest.fixture()
def fake_hands_repository(fake_full_hand, fake_empty_hand):
    fake_repository = InMemoryGamesRepository()
    fake_repository.save(fake_full_hand)
    fake_repository.save(fake_empty_hand)

    return fake_repository


@pytest.fixture()
def fake_players_repository():
    repository = InMemoryPlayersRepository()
    player1 = Player()
    player1.id = '1'
    player2 = Player()
    player2.id = '2'
    repository.save(player1)
    repository.save(player2)
    return repository


@pytest.fixture()
def fake_empty_hand() -> Hand:
    hand = Hand(id=0)
    return hand


@pytest.fixture()
def fake_full_hand(fake_players_repository) -> Hand:
    player1 = fake_players_repository.get_by_id(id='1')
    player2 = fake_players_repository.get_by_id(id='2')
    hand = Hand(id=0)
    hand.cards_dealed[player1.id] = []
    hand.cards_dealed[player2.id] = []
    hand.player_dealer = player1.id
    hand.player_hand = player2.id
    hand.player_turn = player2.id
    hand.players.extend([player1, player2])
    hand.rounds = [Round(cards_played={player1.id: None, player2.id: None})]
    return hand
