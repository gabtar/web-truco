import json
from datetime import datetime
from typing import List
from models.models import Hand, Player
from services.connection_manager import dep_connection_manager
from services.services import HandManager, ScoreManager, PlayerManager


socketController = {}


# Required services for interacting with the events
# Later try to pass by injection in events functions
hand_manager: HandManager = HandManager()
player_manager: PlayerManager = PlayerManager()
score_manager: ScoreManager = ScoreManager()


def event(name):
    """ Socket decorator to route events received from clients """
    def dec(func):
        def inner_func(*args, **kwargs):
            return func(*args, **kwargs)
        socketController[name] = inner_func
        return inner_func
    return dec


# ----------------------------------------------------------------------------
# Server to client events
# ----------------------------------------------------------------------------
@event("gamesUpdate")
async def games_update(playerId: str = None):
    """ Sends an update of the current games avaliables in the server.

    If an optional player_id argument is passed it only sends the message
    to socket of that user

    Args:
        playerId (str): the id of the player to send the update status of games.
    """
    games_list = [game.dict(include={'id', 'name', 'players'}) for game in hand_manager.avaliable_games()]
    for game in games_list:
        game['currentPlayers'] = len(game['players'])
        del game['players']

    message = json.dumps({
            'event': 'gamesUpdate',
            'payload': {'gamesList': games_list}
    })

    if playerId is not None:
        await dep_connection_manager().send(json_string=message, player_id=playerId)
    else:
        await dep_connection_manager().broadcast(json_string=message)


@event("newPlayerJoined")
async def new_player_joined(handId: int, playerId: str):
    """ Notifies the players in a hand that a new user has joined

    Args:
        playerId (str): the id of the player who joined the hand.
        handId: (int): the id of the hand to notify the rest of the players.
    """
    hand = hand_manager.hand_repository.get_by_id(id=handId)
    player = player_manager.find_player(player_id=playerId)
    for player_id in hand.players:
        # Don't send the message to the player who joined
        # Because he already receives the updated game
        if player_id == playerId:
            continue

        message = json.dumps({
            "event": "newPlayerJoined",
            "payload": {"player": {"id": player.id, "name": player.name}}}
        )
        await dep_connection_manager().send(json_string=message, player_id=player_id)


# ----------------------------------------------------------------------------
# Client to server events with server to client responses
# ----------------------------------------------------------------------------
@event("message")
async def send_message(playerId: str, message: str):
    """ Receives a message from a player and re sends it to all users connected

    Args:
        playerId (str): the id of the player who sent the message.
        message (str): the text of the message sent by the player.
    """
    player: Player = player_manager.find_player(player_id=playerId)

    data = json.dumps({
        "event": "message",
        "payload": {"message": {
            "text": message,
            "player": player.name,
            "time": str(datetime.now().strftime("%H:%M:%S"))
            }
        }
    })
    await dep_connection_manager().broadcast(data)


@event("joinGame")
async def join_hand(handId: int, playerId: str):
    """ Joins a player to a hand

    Args:
        playerId (str): the id of the player to add to the hand.
        handId (int): the id of the hand to add a new player.
    """
    hand_manager.join_hand(hand_id=handId, player_id=playerId)
    # TODO cambiar por método directamente en el servicio
    hand: Hand = hand_manager.hand_repository.get_by_id(id=handId)

    game_players = [player_manager.find_player(player_id=player_id).dict() for player_id in hand.players]

    # TODO change to send json schema of the full game status
    data = json.dumps({
            'event': 'joinedHand',
            'payload': {'handId': handId,
                        'name': hand.name,
                        'currentPlayers': game_players}
    })
    await dep_connection_manager().send(json_string=data, player_id=playerId)
    await new_player_joined(handId=handId, playerId=playerId)

    # Updates the new game to all players
    await games_update()


@event("createNewGame")
async def create_new_game(playerId: str):
    """ Creates a new game

    Args:
        playerId (str): id of the player who creates the hand.
    """
    hand_id = hand_manager.new_hand(player_id=playerId)
    # Joins the user to the recently created hand
    await join_hand(playerId=playerId, handId=hand_id)


@event("dealCards")
async def deal_cards(playerId: str, handId: int):
    """ Deals cards in a hand

    Args:
        playerId (str): id of the player who wants to deal cards.
        handId (int): id of the hand to deal cards.
    """
    # TODO cambiar por método directamente en el servicio
    hand = hand_manager.hand_repository.get_by_id(id=handId)
    cards_dealed = hand_manager.deal_cards(hand_id=handId, player_id=playerId)
    score_manager.initialize_score(hand=hand)

    for player, cards in cards_dealed.items():
        data = json.dumps({
                'event': 'receiveDealedCards',
                'payload': {'cards': [card.dict(include={'suit', 'rank'}) for card in cards]}
        })
        await dep_connection_manager().send(json_string=data, player_id=player)


@event("playCard")
async def play_card(playerId: str, handId: int, rank: str, suit: str):
    """ Plays a card in a hand
    If the card played finish the hand, also notifies the result to all players

    Args:
        playerId (str): id of the player who is playing the card.
        handId (int): id of the hand to play the card.
        suit (str): the suit of the card to be played.
        rank (str): the rank of the card to be played.
    """
    hand = hand_manager.hand_repository.get_by_id(id=handId)

    cards_played = hand_manager.play_card(hand_id=handId,
                                          player_id=playerId,
                                          rank=rank,
                                          suit=suit
                                          )

    cards = {}
    for player in cards_played.keys():
        cards[player] = [card.dict(include={'suit', 'rank'}) for card in cards_played[player]]

    data = json.dumps({
        "event": "cardPlayed",
        "payload": {
            "cardsPlayed": cards
            # "card": {"suit": suit, "rank": rank},
            # "player": playerId,
            # "round": current_round
        }
    })

    for player in hand.players:
        await dep_connection_manager().send(json_string=data, player_id=player)

    if score_manager.hand_winner(hand=hand) is not None:

        score_manager.assign_score(hand=hand)

        data = json.dumps({
            "event": "handWinner",
            "player": score_manager.hand_winner(hand),
        })

        for player in hand.players:
            await dep_connection_manager().send(json_string=data, player_id=player)
