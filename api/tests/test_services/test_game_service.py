import pytest

from models.models import Game, Player
from services.game_manager import GameManager
from services.exceptions import GameException


def test_create_2_player_game(fake_games_repository):
    """ Test that a new game for 2 players is created """
    games_repository = fake_games_repository
    game_manager: GameManager = GameManager(games=games_repository)
    game: Game = game_manager.create(rules={'num_players': 2, 'max_score': 15, 'flor': False})

    assert games_repository.get_by_id(id=game.id) is game


def test_join_to_a_game_when_slots_are_available(fake_games_repository, fake_players_repository):
    """ Test that a player can join a game when there is a free slot """
    games_repository = fake_games_repository
    game_manager: GameManager = GameManager(games=games_repository, players=fake_players_repository)
    game: Game = game_manager.create(rules={'num_players': 2, 'max_score': 15, 'flor': False})
    player = fake_players_repository.get_by_id(id='player1')

    game_manager.join_game(player_id=player.id, game_id=game.id)

    assert player in game.players


def test_cannot_join_to_a_game_when_no_slots_are_available(fake_games_repository, fake_players_repository):
    """ Test that a player cannot join a game when the game if full of players """
    games_repository = fake_games_repository
    game_manager: GameManager = GameManager(games=games_repository, players=fake_players_repository)
    player = Player()

    with pytest.raises(GameException) as excep:
        game_manager.join_game(player_id=player.id, game_id='game1')

    assert 'Partida completa' in str(excep)
    assert player not in game_manager.get_game(id='game1')


def test_can_retrieve_all_available_games(fake_games_repository, fake_players_repository):
    """ Tests that can obtain all available games """
    games_repository = fake_games_repository
    game_manager: GameManager = GameManager(games=games_repository, players=fake_players_repository)

    # Create 2 availables/empty game
    game_manager.create(rules={'num_players': 2, 'max_score': 15, 'flor': False})
    game_manager.create(rules={'num_players': 2, 'max_score': 15, 'flor': False})

    # In fake repository there is already an empty game, so it should be 3 availables games
    assert len(game_manager.get_available_games()) == 3
