import pytest

from repositories.repository import InMemoryHandRepository, InMemoryPlayersRepository, InMemoryGameRepository
from models.models import Player, Hand, Round, HandStatus, Game


@pytest.fixture()
def fake_hands_repository(fake_full_hand, fake_empty_hand):
    fake_repository = InMemoryHandRepository()
    fake_repository.save(fake_full_hand)
    fake_repository.save(fake_empty_hand)

    return fake_repository


@pytest.fixture()
def fake_players_repository():
    repository = InMemoryPlayersRepository()
    player1 = Player()
    player1.id = 'player1'
    player2 = Player()
    player2.id = 'player2'
    repository.save(player1)
    repository.save(player2)
    return repository


@pytest.fixture()
def fake_empty_hand() -> Hand:
    hand = Hand(id='game0')
    return hand


@pytest.fixture()
def fake_full_hand(fake_players_repository) -> Hand:
    player1 = fake_players_repository.get_by_id(id='player1')
    player2 = fake_players_repository.get_by_id(id='player2')
    hand = Hand(id='game1')
    hand.cards_dealed[player1.id] = []
    hand.cards_dealed[player2.id] = []
    hand.player_dealer = player1.id
    hand.player_hand = player2.id
    hand.player_turn = player2.id
    hand.chant_turn = player2.id
    hand.status = HandStatus.IN_PROGRESS
    hand.rounds = [Round(cards_played={player1.id: None, player2.id: None})]
    return hand


@pytest.fixture()
def fake_games_repository(fake_players_repository) -> InMemoryGameRepository:
    games_repository: InMemoryGameRepository = InMemoryGameRepository()

    fake_empty_game: Game = Game(rules=2)
    fake_empty_game.id = 'game0'
    games_repository.save(fake_empty_game)

    fake_full_game: Game = Game(rules=2)
    player1: Player = fake_players_repository.get_by_id(id='player1')
    player2: Player = fake_players_repository.get_by_id(id='player2')
    fake_full_game.players = [player1, player2]
    fake_full_game.id = 'game1'

    games_repository.save(fake_full_game)

    return games_repository
