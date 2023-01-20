import pytest

from models.models import Player, Hand
from services.services import HandManager, GameException
from services.connection_manager import ConnectionManager
from unittest import mock

pytest_plugins = ('pytest_asyncio',)


# TODO, mocks de los objectos de la db!!!
@pytest.mark.asyncio
async def test_a_player_can_create_a_new_hand():
    """ Tests that a user can create a new hand in the server """
    connection_manager = mock.AsyncMock(ConnectionManager)
    hand_manager = HandManager(connection_manager)

    player = Player().save()

    hand = await hand_manager.new_hand(player_id=player.id)

    assert hand == len(Hand.get_all())


@pytest.mark.asyncio
async def test_a_player_cannot_create_a_hand_if_he_is_already_playing():
    """ Test that a user can join a hand """
    with pytest.raises(Exception) as excep:
        connection_manager = mock.AsyncMock(ConnectionManager)
        hand_manager = HandManager(connection_manager)
        player = Player().save()

        await hand_manager.new_hand(player_id=player.id)
        # This raises the exception
        await hand_manager.new_hand(player_id=player.id)

    assert excep.type == GameException
    assert "Ya estás en una partida" == str(excep.value)


@pytest.mark.asyncio
async def test_a_user_can_join_a_hand_with_free_slots():
    """ Test that a user can join a hand when there are free slots available """
    connection_manager = mock.AsyncMock(ConnectionManager)

    hand_manager = HandManager(connection_manager)
    player = Player().save()
    player_two = Player().save()

    hand_id = await hand_manager.new_hand(player_id=player.id)

    await hand_manager.join_hand(hand_id=hand_id, player_id=player_two.id)

    assert Player.get_by_id(player_two.id).playing_hand is not None


@pytest.mark.asyncio
async def test_a_user_cannot_join_a_if_he_is_already_playing_in_other():
    """ Test that a user cannot join a hand if he is already playing one """
    with pytest.raises(Exception) as excep:
        connection_manager = mock.AsyncMock(ConnectionManager)

        hand_manager = HandManager(connection_manager)
        player = Player().save()

        hand_id = await hand_manager.new_hand(player_id=player.id)

        # The same player tries to join his own hand -> raises exception
        await hand_manager.join_hand(hand_id=hand_id, player_id=player.id)

    assert excep.type == GameException
    assert "Ya estás en una partida" == str(excep.value)


@pytest.mark.asyncio
async def test_a_user_cannot_join_a_hand_if_no_more_slots_left():
    """ Test that a user cannot join a hand if it's full of players """
    with pytest.raises(Exception) as excep:
        connection_manager = mock.AsyncMock(ConnectionManager)

        hand_manager = HandManager(connection_manager)
        player = Player().save()
        player_two = Player().save()
        player_three = Player().save()

        hand_id = await hand_manager.new_hand(player_id=player.id)

        await hand_manager.join_hand(hand_id=hand_id, player_id=player_two.id)
        await hand_manager.join_hand(hand_id=hand_id, player_id=player_three.id)

    assert excep.type == GameException
    assert "Partida completa" == str(excep.value)


@pytest.mark.asyncio
async def test_a_user_can_deal_a_hand():
    """ Test that a user can deal cards in a new hand """
    connection_manager = mock.AsyncMock(ConnectionManager)

    hand_manager = HandManager(connection_manager)
    player = Player().save()
    player_two = Player().save()

    hand_id = await hand_manager.new_hand(player_id=player.id)
    hand = Hand.get_by_id(hand_id=hand_id)
    await hand_manager.join_hand(hand_id=hand_id, player_id=player_two.id)

    await hand_manager.deal_cards(hand_id=hand_id, player_id=player.id)

    cards_dealed_player_one = hand.get_cards_dealed(player_id=player.id)
    cards_dealed_player_two = hand.get_cards_dealed(player_id=player_two.id)

    assert len(cards_dealed_player_one) == 3
    assert len(cards_dealed_player_two) == 3


@pytest.mark.asyncio
async def test_a_user_cannot_deal_a_hand():
    """ Test that a user cannot deal cards if is not hand """
    with pytest.raises(Exception) as excep:
        connection_manager = mock.AsyncMock(ConnectionManager)

        hand_manager = HandManager(connection_manager)
        player = Player().save()
        player_two = Player().save()

        hand_id = await hand_manager.new_hand(player_id=player.id)
        await hand_manager.join_hand(hand_id=hand_id, player_id=player_two.id)

        await hand_manager.deal_cards(hand_id=hand_id, player_id=player_two.id)

    assert excep.type == GameException
    assert "Acción inválida" == str(excep.value)


@pytest.mark.asyncio
async def test_a_user_cannot_deal_a_hand_two():
    """ Test that a user cannot deal cards if there not enought players joined """
    with pytest.raises(Exception) as excep:
        connection_manager = mock.AsyncMock(ConnectionManager)

        hand_manager = HandManager(connection_manager)
        player = Player().save()
        hand_id = await hand_manager.new_hand(player_id=player.id)

        await hand_manager.deal_cards(hand_id=hand_id, player_id=player.id)

    assert excep.type == GameException
    assert "No hay suficientes jugadores" == str(excep.value)


@pytest.mark.asyncio
async def test_a_user_can_play_a_card():
    """ Test that a user can play a card in a hand he is playing """
    connection_manager = mock.AsyncMock(ConnectionManager)

    hand_manager = HandManager(connection_manager)
    player = Player().save()
    player_two = Player().save()

    hand_id = await hand_manager.new_hand(player_id=player.id)
    hand = Hand.get_by_id(hand_id=hand_id)
    await hand_manager.join_hand(hand_id=hand_id, player_id=player_two.id)
    await hand_manager.deal_cards(hand_id=hand_id, player_id=player.id)

    cards_dealed_player_one = hand.get_cards_dealed(player_id=player.id)

    await hand_manager.play_card(hand_id=hand_id, player_id=player.id, card_id=cards_dealed_player_one[0].id)

    card_inserted_in_round = cards_dealed_player_one[0]
    card_dealed_to_player = hand.get_card_played(player_id=player.id, round_number=0)

    assert card_inserted_in_round.suit == card_dealed_to_player.suit
    assert card_inserted_in_round.rank == card_dealed_to_player.rank
    assert card_inserted_in_round.value == card_dealed_to_player.value


@pytest.mark.asyncio
async def test_a_user_cannot_play_a_card_if_already_played_in_the_round():
    """ Test that a user cant play twice in the same round """
    with pytest.raises(Exception) as excep:
        connection_manager = mock.AsyncMock(ConnectionManager)

        hand_manager = HandManager(connection_manager)
        player = Player().save()
        player_two = Player().save()

        hand_id = await hand_manager.new_hand(player_id=player.id)
        hand = Hand.get_by_id(hand_id=hand_id)
        await hand_manager.join_hand(hand_id=hand_id, player_id=player_two.id)
        await hand_manager.deal_cards(hand_id=hand_id, player_id=player.id)

        cards_dealed_player_one = hand.get_cards_dealed(player_id=player.id)

        await hand_manager.play_card(hand_id=hand_id, player_id=player.id, card_id=cards_dealed_player_one[0].id)
        await hand_manager.play_card(hand_id=hand_id, player_id=player.id, card_id=cards_dealed_player_one[2].id)

    assert excep.type == GameException
    assert "Ya has jugado una carta" == str(excep.value)


# TODO, cannot play if insert error
