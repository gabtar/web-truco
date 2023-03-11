import pytest

from models.models import Truco, Hand, HandStatus
from services.truco_manager import TrucoManager
from services.exceptions import GameException


def test_update_truco_level_during_a_round(
        fake_hands_repository, fake_games_repository
        ):
    """ Tests that can update the level of truco during a round """
    hand: Hand = fake_hands_repository.get_by_id(id='game1')
    truco_manager = TrucoManager(hands=fake_hands_repository, games=fake_games_repository)

    truco_manager.chant_truco(hand_id=hand.id, player_id=hand.player_turn, level=Truco.TRUCO)

    assert hand.truco_status == Truco.TRUCO


def test_cannot_update_truco_level_to_a_lower_level(
        fake_hands_repository, fake_games_repository
        ):
    """ Tests that cannot update the level of truco if the level is lower than 
        the current level
    """
    hand: Hand = fake_hands_repository.get_by_id(id='game1')
    truco_manager = TrucoManager(hands=fake_hands_repository, games=fake_games_repository)
    hand.truco_status = Truco.VALE_CUATRO

    with pytest.raises(GameException) as excep:
        truco_manager.chant_truco(hand_id=hand.id, player_id=hand.player_turn, level=Truco.TRUCO)

    assert 'Nivel de truco inválido' in str(excep)


def test_cannot_update_truco_level_when_its_not_player_turn(
        fake_hands_repository, fake_games_repository
        ):
    """ Tests that cannot update the level of truco if it's not player's turn """
    hand: Hand = fake_hands_repository.get_by_id(id='game1')
    truco_manager = TrucoManager(hands=fake_hands_repository, games=fake_games_repository)

    with pytest.raises(GameException) as excep:
        truco_manager.chant_truco(hand_id=hand.id, player_id=hand.player_dealer, level=Truco.TRUCO)

    assert 'No es tu turno' in str(excep)


def test_cannot_update_truco_level_if_player_already_updated_truco_level(
            fake_hands_repository, fake_games_repository
        ):
    """ Tests that cannot update the level of truco if player previously updated
        the level of truco
    """
    hand: Hand = fake_hands_repository.get_by_id(id='game1')
    truco_manager = TrucoManager(hands=fake_hands_repository, games=fake_games_repository)
    current_player_turn = hand.player_turn
    truco_manager.chant_truco(hand_id=hand.id, player_id=current_player_turn, level=Truco.TRUCO)

    with pytest.raises(GameException) as excep:
        truco_manager.chant_truco(hand_id=hand.id, player_id=current_player_turn, level=Truco.RETRUCO)

    assert 'No es tu turno' in str(excep)


def test_accept_response_to_truco(
            fake_hands_repository, fake_games_repository
        ):
    """ Test that a player can accept truco if chant with same level """
    hand: Hand = fake_hands_repository.get_by_id(id='game1')
    truco_manager = TrucoManager(hands=fake_hands_repository, games=fake_games_repository)
    truco_manager.chant_truco(hand_id=hand.id, player_id=hand.chant_turn, level=Truco.TRUCO)

    # El otro jugador acepta el truco
    truco_manager.response_to_truco(hand_id=hand.id, player_id=hand.chant_turn, level=Truco.TRUCO)

    assert hand.status == HandStatus.IN_PROGRESS
    assert hand.truco_status == Truco.TRUCO


def test_decline_response_to_truco(
            fake_hands_repository, fake_games_repository
        ):
    """ Test that a player can decline a truco and finish the hand """
    hand: Hand = fake_hands_repository.get_by_id(id='game1')
    truco_manager = TrucoManager(hands=fake_hands_repository, games=fake_games_repository)
    truco_manager.chant_truco(hand_id=hand.id, player_id=hand.chant_turn, level=Truco.TRUCO)

    # El otro jugador no acepta(se modela cantando el nivel inferior)
    truco_manager.response_to_truco(hand_id=hand.id, player_id=hand.chant_turn, level=Truco.NO_CANTADO)

    assert hand.status == HandStatus.FINISHED
    assert hand.truco_status == Truco.NO_CANTADO


def test_chant_again_in_response_to_truco(
            fake_hands_repository, fake_games_repository
        ):
    """ Test that a player can decline a truco and finish the hand """
    hand: Hand = fake_hands_repository.get_by_id(id='game1')
    truco_manager = TrucoManager(hands=fake_hands_repository, games=fake_games_repository)
    truco_manager.chant_truco(hand_id=hand.id, player_id=hand.player_turn, level=Truco.TRUCO)

    # El otro jugador canta retruco, entonces el jugador original debe aceptar/declinar
    truco_manager.response_to_truco(hand_id=hand.id, player_id=hand.chant_turn, level=Truco.RETRUCO)

    assert hand.status == HandStatus.LOCKED
    assert hand.truco_status == Truco.RETRUCO
    # La mano 'fake' de prueba se inicializa con turno a player2(el que es mano)
    assert hand.chant_turn == 'player2'
    assert hand.player_turn == 'player2'  # El turno sigue siendo del jugador original, el que es mano en la fake hand


def test_cannot_chant_when_cards_are_not_dealed(
            fake_hands_repository, fake_games_repository
        ):
    """ Test that a player cannot chant if cards are not dealed """
    hand: Hand = fake_hands_repository.get_by_id(id='game1')
    truco_manager = TrucoManager(hands=fake_hands_repository, games=fake_games_repository)
    # Se setea la mano como no iniciada
    hand.status = HandStatus.NOT_STARTED

    with pytest.raises(GameException) as excep:
        truco_manager.chant_truco(hand_id=hand.id, player_id=hand.player_turn, level=Truco.TRUCO)

    assert 'Deben repartirse las cartas primero' in str(excep)
