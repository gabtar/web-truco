import pytest
from models.models import Round, Card, Hand, Player


@pytest.fixture()
def fake_hand():
    hand = Hand(id=-1)
    player1 = Player()
    player1.id = 'player1'
    player2 = Player()
    player2.id = 'player2'
    hand.players = [player1, player2]

    hand.player_hand = 'player2'

    hand.rounds = [
            Round(cards_played={'player1': None, 'player2': None}),
            Round(cards_played={'player1': None, 'player2': None}),
            Round(cards_played={'player1': None, 'player2': None}),
            ]

    return hand


# -----------------------------------------------------------------------------
# Round tests
# -----------------------------------------------------------------------------
def test_player_one_wins():
    """ When player 1 places a higher card, he wins the round """
    as_espadas = Card(suit='E', rank='1')
    as_basto = Card(suit='B', rank='1')

    round = Round(cards_played={'1': as_espadas, '2': as_basto})

    assert round.winner == '1'


def test_player_two_wins():
    """ When player 1 places a higher card, he wins the round """
    cuatro_copa = Card(suit='C', rank='4')
    tres_oro = Card(suit='O', rank='3')

    round = Round(cards_played={'1': cuatro_copa, '2': tres_oro})

    assert round.winner == '2'


def test_no_winner_when_equal_value_cards():
    """ Test that there is no winner when to 2 cards of equal value are played """
    cuatro_copa = Card(suit='C', rank='4')
    cuatro_espada = Card(suit='E', rank='4')

    round = Round(cards_played={'1': cuatro_copa, '2': cuatro_espada})

    assert round.winner is None


def test_no_winner_when_only_one_card_played():
    """ Test there is no winner if only 1 card was played """
    round = Round(cards_played={'1': Card(suit='C', rank='4'), '2': None})

    assert round.winner is None


# -----------------------------------------------------------------------------
# Hand tests
# -----------------------------------------------------------------------------

# TODO, Casos de prueba
# Si no jugaron cartas no hay ganador                                        ✓
# Primer round empate -> Gana el que gana el segundo round                   ✓
# Primer round y segundo empate -> Gana el que gana el tercer round          ✓
# 3 empates -> Gana el que es mano                                           ✓
# Gana primer round y empata segundo -> Gana el que ganó el primer round     ✓
# Gana primer round, pierde segundo y empata tercero
#       -> Gana el que ganó el primer round                                  ✓
# Al mejor de 3 rounds
#       -> Gana los primeros 2                                               ✓
#       -> Gana el primero y el tercero
#       -> Gana el segundo y el tercero
def test_no_player_wins_when_no_rounds_played(fake_empty_hand):
    """ Test that there is no winner when nobody has placed a card """
    assert fake_empty_hand.winner is None


def test_player_one_wins_on_tie_first_round_and_winned_second_round(fake_hand):
    """ Test that when first card is tied(same value), and second round is
        winned by player 1, player 1 wins the hand.
    """
    hand = fake_hand
    cards_p1 = [Card(suit='E', rank='4'), Card(suit='E', rank='1')]
    cards_p2 = [Card(suit='O', rank='4'), Card(suit='B', rank='1')]

    hand.rounds[0].cards_played['player1'] = cards_p1[0]
    hand.rounds[0].cards_played['player2'] = cards_p2[0]
    hand.rounds[1].cards_played['player1'] = cards_p1[1]
    hand.rounds[1].cards_played['player2'] = cards_p2[1]

    assert hand.winner == 'player1'


def test_two_consecutive_rounds_define_in_third_round(fake_hand):
    """ Test that when first card is tied, second round is tied
        and third round is winned by player 1, he wins the hand
    """
    hand = fake_hand
    cards_p1 = [Card(suit='E', rank='4'), Card(suit='E', rank='5'), Card(suit='O', rank='3')]
    cards_p2 = [Card(suit='O', rank='4'), Card(suit='O', rank='5'), Card(suit='B', rank='6')]

    hand.rounds[0].cards_played['player1'] = cards_p1[0]
    hand.rounds[0].cards_played['player2'] = cards_p2[0]
    hand.rounds[1].cards_played['player1'] = cards_p1[1]
    hand.rounds[1].cards_played['player2'] = cards_p2[1]
    hand.rounds[2].cards_played['player1'] = cards_p1[2]
    hand.rounds[2].cards_played['player2'] = cards_p2[2]

    assert hand.winner == 'player1'


def test_all_rounds_tied_player_hand_wins(fake_hand):
    """ Test when all cards played are tied, the player who is hand wins """
    hand = fake_hand
    cards_p1 = [Card(suit='E', rank='4'), Card(suit='E', rank='5'), Card(suit='E', rank='6')]
    cards_p2 = [Card(suit='O', rank='4'), Card(suit='O', rank='5'), Card(suit='O', rank='6')]

    hand.rounds[0].cards_played['player1'] = cards_p1[0]
    hand.rounds[0].cards_played['player2'] = cards_p2[0]
    hand.rounds[1].cards_played['player1'] = cards_p1[1]
    hand.rounds[1].cards_played['player2'] = cards_p2[1]
    hand.rounds[2].cards_played['player1'] = cards_p1[2]
    hand.rounds[2].cards_played['player2'] = cards_p2[2]

    assert hand.winner == hand.player_hand


def test_player1_wins_when_wins_first_round_and_second_round_is_tie(fake_hand):
    """ Test that player 1 wins the hand when he wins the first round and the
        second round is a tie
    """
    hand = fake_hand
    cards_p1 = [Card(suit='E', rank='1'), Card(suit='E', rank='5')]
    cards_p2 = [Card(suit='O', rank='4'), Card(suit='B', rank='5')]

    hand.rounds[0].cards_played['player1'] = cards_p1[0]
    hand.rounds[0].cards_played['player2'] = cards_p2[0]
    hand.rounds[1].cards_played['player1'] = cards_p1[1]
    hand.rounds[1].cards_played['player2'] = cards_p2[1]

    assert hand.winner == 'player1'


def test_player1_first_round_loses_second_and_ties_third(fake_hand):
    """ Test that player 1 wins the hand when he wins the first loses the 2nd
        and the third is a tie
    """
    hand = fake_hand
    cards_p1 = [Card(suit='E', rank='1'), Card(suit='E', rank='4'), Card(suit='C', rank='12')]
    cards_p2 = [Card(suit='O', rank='4'), Card(suit='B', rank='7'), Card(suit='B', rank='12')]

    hand.rounds[0].cards_played['player1'] = cards_p1[0]
    hand.rounds[0].cards_played['player2'] = cards_p2[0]
    hand.rounds[1].cards_played['player1'] = cards_p1[1]
    hand.rounds[1].cards_played['player2'] = cards_p2[1]
    hand.rounds[1].cards_played['player1'] = cards_p1[2]
    hand.rounds[1].cards_played['player2'] = cards_p2[2]

    assert hand.winner == 'player1'


def test_player2_wins_first_and_secound_round(fake_hand):
    """ Test that player 2 wins 1st and 2nd round, he wins the hand """
    hand = fake_hand
    cards_p1 = [Card(suit='E', rank='12'), Card(suit='C', rank='4')]
    cards_p2 = [Card(suit='O', rank='3'), Card(suit='B', rank='7')]

    hand.rounds[0].cards_played['player1'] = cards_p1[0]
    hand.rounds[0].cards_played['player2'] = cards_p2[0]
    hand.rounds[1].cards_played['player1'] = cards_p1[1]
    hand.rounds[1].cards_played['player2'] = cards_p2[1]

    assert hand.winner == 'player2'


def test_player2_wins_first_and_third_round(fake_hand):
    """ Test that player 2 wins 1st, loses 2nd round, and wins 3rd round,
        he wins the hand
    """
    hand = fake_hand
    cards_p1 = [Card(suit='E', rank='12'), Card(suit='C', rank='1'), Card(suit='B', rank='7')]
    cards_p2 = [Card(suit='O', rank='3'), Card(suit='B', rank='10'), Card(suit='C', rank='3')]

    hand.rounds[0].cards_played['player1'] = cards_p1[0]
    hand.rounds[0].cards_played['player2'] = cards_p2[0]
    hand.rounds[1].cards_played['player1'] = cards_p1[1]
    hand.rounds[1].cards_played['player2'] = cards_p2[1]
    hand.rounds[2].cards_played['player1'] = cards_p1[2]
    hand.rounds[2].cards_played['player2'] = cards_p2[2]

    assert hand.winner == 'player2'


def test_player1_loses_first_and_wins_second_and_third_round(fake_hand):
    """ Test that player 1 wins loses 1st, wins 2nd round, and wins 3rd round,
        so he wins the hand
    """
    hand = fake_hand
    cards_p1 = [Card(suit='E', rank='12'), Card(suit='B', rank='1'), Card(suit='E', rank='1')]
    cards_p2 = [Card(suit='O', rank='3'), Card(suit='O', rank='7'), Card(suit='E', rank='7')]

    hand.rounds[0].cards_played['player1'] = cards_p1[0]
    hand.rounds[0].cards_played['player2'] = cards_p2[0]
    hand.rounds[1].cards_played['player1'] = cards_p1[1]
    hand.rounds[1].cards_played['player2'] = cards_p2[1]
    hand.rounds[2].cards_played['player1'] = cards_p1[2]
    hand.rounds[2].cards_played['player2'] = cards_p2[2]

    assert hand.winner == 'player1'
