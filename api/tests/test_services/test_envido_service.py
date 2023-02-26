import pytest

from models.models import Envido, EnvidoLevels, Hand, HandStatus, Round, Player, Card
from services.services import EnvidoManager, GameException


@pytest.fixture()
def fake_hand():
    hand = Hand(id=-1)
    player1 = Player()
    player1.id = 'player1'
    player2 = Player()
    player2.id = 'player2'
    hand.players = [player1, player2]
    hand.status = HandStatus.ENVIDO

    hand.player_hand = 'player2'
    hand.player_turn = 'player1'
    hand.chant_turn = 'player1'
    hand.envido = Envido()


    hand.rounds = [
            Round(cards_played={'player1': None, 'player2': None}),
            Round(cards_played={'player1': None, 'player2': None}),
            Round(cards_played={'player1': None, 'player2': None}),
            ]

    return hand


def test_can_chant_envido_during_first_round(
        fake_hands_repository, fake_hand
        ):
    """ Test that a player can chant envido during the first round"""
    hand: Hand = fake_hand
    hands_repository = fake_hands_repository
    hands_repository.save(hand)
    envido_manager = EnvidoManager(hands_repository)
    envido_manager.chant_envido(hand_id=hand.id, player_id=hand.player_turn, level=EnvidoLevels.ENVIDO)

    assert EnvidoLevels.ENVIDO in hand.envido.chanted
    assert hand.status == HandStatus.ENVIDO


def test_cannot_chant_envido_if_first_round_has_finished(
        fake_hands_repository, fake_hand
        ):
    """ Test that a player cannot chant envido if not in first round """
    hand: Hand = fake_hand
    hand.rounds[0].cards_played['player1'] = Card(suit='E', rank='1')
    hand.rounds[0].cards_played['player2'] = Card(suit='B', rank='1')
    hands_repository = fake_hands_repository
    hands_repository.save(hand)
    envido_manager = EnvidoManager(hands_repository)

    with pytest.raises(GameException) as excep:
        envido_manager.chant_envido(hand_id=hand.id, player_id=hand.player_turn, level=EnvidoLevels.REAL_ENVIDO)

    assert 'No se puede cantar después de la primera ronda' in str(excep)


def test_cannot_chant_envido_if_not_player_turn(
        fake_hands_repository, fake_hand
        ):
    """ Test that a player cannot chant envido if not in first round """
    hand: Hand = fake_hand
    hands_repository = fake_hands_repository
    hands_repository.save(hand)
    envido_manager = EnvidoManager(hands_repository)

    with pytest.raises(GameException) as excep:
        envido_manager.chant_envido(hand_id=hand.id, player_id=hand.player_hand, level=EnvidoLevels.FALTA_ENVIDO)

    assert 'No es tu turno' in str(excep)


def test_response_to_envido_acumulates_levels(
        fake_hands_repository, fake_hand
        ):
    """ Test that a player cannot chant envido if not in first round """
    hand: Hand = fake_hand
    hands_repository = fake_hands_repository
    hands_repository.save(hand)
    envido_manager = EnvidoManager(hands_repository)

    envido_manager.chant_envido(hand_id=hand.id, player_id=hand.player_turn, level=EnvidoLevels.ENVIDO)
    envido_manager.response_to_envido(hand_id=hand.id, player_id=hand.player_hand, level=EnvidoLevels.ENVIDO)

    assert len(hand.envido.chanted) == 2
    assert hand.envido.chanted == [EnvidoLevels.ENVIDO, EnvidoLevels.ENVIDO]


def test_cannot_chant_lower_levels_when_last_chanted_was_higher_than_envido(
        fake_hands_repository, fake_hand
        ):
    """ Test that a player cannot chant a lover level of envido if the last chant
        was higher than EnvidoStatus.ENVIDO
    """
    hand: Hand = fake_hand
    hands_repository = fake_hands_repository
    hands_repository.save(hand)
    envido_manager = EnvidoManager(hands_repository)

    envido_manager.chant_envido(hand_id=hand.id, player_id=hand.player_turn, level=EnvidoLevels.ENVIDO)
    envido_manager.response_to_envido(hand_id=hand.id, player_id=hand.player_hand, level=EnvidoLevels.REAL_ENVIDO)

    with pytest.raises(GameException) as excep:
        envido_manager.response_to_envido(hand_id=hand.id, player_id=hand.player_turn, level=EnvidoLevels.ENVIDO)

    assert 'No se puede cantar un nivel inferior' in str(excep)
    assert len(hand.envido.chanted) == 2
    assert hand.envido.chanted == [EnvidoLevels.ENVIDO, EnvidoLevels.REAL_ENVIDO]


def test_that_opponent_can_accept_envido(
        fake_hands_repository, fake_hand
        ):
    """ Test that a player can accept envido """
    hand: Hand = fake_hand
    hands_repository = fake_hands_repository
    hands_repository.save(hand)
    envido_manager = EnvidoManager(hands_repository)

    envido_manager.chant_envido(hand_id=hand.id, player_id=hand.player_turn, level=EnvidoLevels.ENVIDO)
    envido_manager.accept_envido(hand_id=hand.id, player_id=hand.player_hand)

    assert hand.envido.chanted == [EnvidoLevels.ENVIDO]
    assert hand.envido.points == 2


def test_that_opponent_can_accept_multiples_levels_of_envido(
        fake_hands_repository, fake_hand
        ):
    """ Test that a player can accept multiples chants of envido """
    hand: Hand = fake_hand
    hands_repository = fake_hands_repository
    hands_repository.save(hand)
    envido_manager = EnvidoManager(hands_repository)

    envido_manager.chant_envido(hand_id=hand.id, player_id=hand.chant_turn, level=EnvidoLevels.ENVIDO)
    envido_manager.response_to_envido(hand_id=hand.id, player_id=hand.chant_turn, level=EnvidoLevels.REAL_ENVIDO)
    envido_manager.accept_envido(hand_id=hand.id, player_id=hand.chant_turn)

    assert hand.envido.chanted == [EnvidoLevels.ENVIDO, EnvidoLevels.REAL_ENVIDO]
    assert hand.envido.points == 5


def test_that_opponent_can_decline_envido(
        fake_hands_repository, fake_hand
        ):
    """ Test that a player can decline envido """
    hand: Hand = fake_hand
    hands_repository = fake_hands_repository
    hands_repository.save(hand)
    envido_manager = EnvidoManager(hands_repository)

    envido_manager.chant_envido(hand_id=hand.id, player_id=hand.player_turn, level=EnvidoLevels.ENVIDO)
    envido_manager.decline_envido(hand_id=hand.id, player_id=hand.player_hand)

    assert hand.envido.chanted == [EnvidoLevels.ENVIDO]
    assert hand.envido.points == 1
    assert hand.envido.winner == hand.player_turn
    assert hand.status == HandStatus.IN_PROGRESS


def test_that_opponent_can_decline_multiple_levels_of_envido(
        fake_hands_repository, fake_hand
        ):
    """ Test that a player can decline multiple levels of envido """
    hand: Hand = fake_hand
    hands_repository = fake_hands_repository
    hands_repository.save(hand)
    envido_manager = EnvidoManager(hands_repository)

    envido_manager.chant_envido(hand_id=hand.id, player_id=hand.player_turn, level=EnvidoLevels.ENVIDO)
    envido_manager.response_to_envido(hand_id=hand.id, player_id=hand.chant_turn, level=EnvidoLevels.ENVIDO)
    envido_manager.response_to_envido(hand_id=hand.id, player_id=hand.chant_turn, level=EnvidoLevels.REAL_ENVIDO)
    # Declina el oponente
    envido_manager.decline_envido(hand_id=hand.id, player_id=hand.chant_turn)

    assert hand.envido.chanted == [EnvidoLevels.ENVIDO, EnvidoLevels.ENVIDO, EnvidoLevels.REAL_ENVIDO]
    assert hand.envido.points == 5 # 2 envido + 1 por no querido
    assert hand.envido.winner == hand.player_turn
    assert hand.status == HandStatus.IN_PROGRESS


def test_can_play_cards_in_envido(
        fake_hands_repository, fake_hand
        ):
    """ Test that a player can plays cards in Envido """
    hand: Hand = fake_hand
    hands_repository = fake_hands_repository
    hands_repository.save(hand)
    envido_manager = EnvidoManager(hands_repository)

    envido_manager.chant_envido(hand_id=hand.id, player_id=hand.player_turn, level=EnvidoLevels.ENVIDO)
    envido_manager.accept_envido(hand_id=hand.id, player_id=hand.chant_turn)

    player_turn = hand.chant_turn
    envido_manager.play_envido(
            hand_id=hand.id,
            player_id=hand.chant_turn,
            cards=[Card(suit='E', rank='5'), Card(suit='E', rank='4')]
    )

    assert hand.envido.cards_played[player_turn] == [Card(suit='E', rank='5'), Card(suit='E', rank='4')]
    assert hand.envido.all_played is False


def test_if_player2_envido_score_is_higher_he_wins_the_envido(
        fake_hands_repository, fake_hand
        ):
    """ Test that higher envido scores wins the envido """
    hand: Hand = fake_hand
    hands_repository = fake_hands_repository
    hands_repository.save(hand)
    player1 = hand.players[0].id
    player2 = hand.players[1].id

    envido_manager = EnvidoManager(hands_repository)

    envido_manager.chant_envido(hand_id=hand.id, player_id=player1, level=EnvidoLevels.REAL_ENVIDO)
    envido_manager.accept_envido(hand_id=hand.id, player_id=player2)

    envido_manager.play_envido(
            hand_id=hand.id,
            player_id=player1,
            # 29
            cards=[Card(suit='E', rank='5'), Card(suit='E', rank='4')]
    )
    envido_manager.play_envido(
            hand_id=hand.id,
            player_id=player2,
            # 33
            cards=[Card(suit='B', rank='7'), Card(suit='B', rank='6')]
    )

    assert hand.envido.all_played is True
    assert hand.envido.winner == player2


def test_if_both_players_have_equal_score_the_hand_player_wins(
        fake_hands_repository, fake_hand
        ):
    """ Test that when both players place equal envido score, the player who is
        hand in the game wins the envido
    """
    hand: Hand = fake_hand
    hands_repository = fake_hands_repository
    hands_repository.save(hand)
    player1 = hand.players[0].id
    player2 = hand.players[1].id

    envido_manager = EnvidoManager(hands_repository)

    envido_manager.chant_envido(hand_id=hand.id, player_id=player1, level=EnvidoLevels.REAL_ENVIDO)
    envido_manager.accept_envido(hand_id=hand.id, player_id=player2)

    envido_manager.play_envido(
            hand_id=hand.id,
            player_id=player1,
            # 29
            cards=[Card(suit='E', rank='5'), Card(suit='E', rank='4')]
    )
    envido_manager.play_envido(
            hand_id=hand.id,
            player_id=player2,
            # 29
            cards=[Card(suit='B', rank='5'), Card(suit='B', rank='4')]
    )

    assert hand.envido.all_played is True
    assert hand.envido.winner == hand.player_hand


def test_envido_cannot_be_chanted_again_if_it_was_already_played_on_the_first_round(
        fake_hands_repository, fake_hand
        ):
    """ Tests that envido cannot be chanted again if it was already played in 
        the hand
    """
    hand: Hand = fake_hand
    hands_repository = fake_hands_repository
    hands_repository.save(hand)
    player1 = hand.players[0].id
    player2 = hand.players[1].id

    envido_manager = EnvidoManager(hands_repository)

    envido_manager.chant_envido(hand_id=hand.id, player_id=player1, level=EnvidoLevels.REAL_ENVIDO)
    envido_manager.accept_envido(hand_id=hand.id, player_id=player2)

    envido_manager.play_envido(
            hand_id=hand.id,
            player_id=player1,
            # 29
            cards=[Card(suit='E', rank='5'), Card(suit='E', rank='4')]
    )
    envido_manager.play_envido(
            hand_id=hand.id,
            player_id=player2,
            # 29
            cards=[Card(suit='B', rank='5'), Card(suit='B', rank='4')]
    )

    with pytest.raises(GameException) as excep:
        envido_manager.chant_envido(hand_id=hand.id, player_id=player1, level=EnvidoLevels.FALTA_ENVIDO)

    assert 'El envido ya ha finalizado' in str(excep)



def test_cannot_chant_envido_when_cards_were_not_yet_dealed(
        fake_hands_repository, fake_hand
        ):
    """ Tests that envido cannot be chanted when no cards dealed
    """
    hand: Hand = fake_hand
    hand.status = HandStatus.NOT_STARTED
    hands_repository = fake_hands_repository
    hands_repository.save(hand)
    player1 = hand.players[0].id
    player2 = hand.players[1].id
    envido_manager = EnvidoManager(hands_repository)
    with pytest.raises(GameException) as excep:
        envido_manager.chant_envido(hand_id=hand.id, player_id=player1, level=EnvidoLevels.ENVIDO)

    assert 'Deben repartirse las cartas primero' in str(excep)


# TODO, Casos de prueba
# No se puede cantar si ya se cantó el truco!
# -> Ojo en realidad si primeron canta uno truco le podes recantar el envido esta primero
#    y luego de jugar el envido tiene que contestar el canto del truco
# Si la partida no ha iniciado no se puede cantar
# No se puede cantar niveles inferiores al actual -> Cuando se responde      ✓
# Se acumula el puntaje de sucesivos niveles del envido                      ✓
# Aceptar/Declinar el envido y setea el puntaje y ganador(si declina)        ✓
# No querido en cualquier nivel es +1 punto                                  ✓
# Falta envido en malas gana directamente (+30)
# Falta envido en buenas se computa lo que le falta al oponente para ganar la partida
#           (30 - puntaje actual del oponente)

# Cantar la puntuación/ganador
# No se puede cantar puntaje que no tenga en mesa/cartas repartidas
# 2 cartas de igual palo suman +20
# Caballo, Zota y Rey valen 0
# Si empatan gana el que es mano
