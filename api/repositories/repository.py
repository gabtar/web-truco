import abc
from typing import List
from models.models import Hand


class AbstractHandRepository(abc.ABC):
    @abc.abstractmethod
    def get_by_id(self, id: int) -> Hand:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, hand: Hand) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, hand: Hand) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_availables(self):
        raise NotImplementedError


class InMemoryGamesRepository(AbstractHandRepository):
    _hands: List[Hand]

    def __init__(self):
        self._hands = []

    def get_by_id(self, id: int) -> Hand:
        return self._hands[id]

    def get_availables(self) -> List[Hand]:
        avaliable_games = []
        for game in self._hands:
            if len(game.players) < 2:
                avaliable_games.append(game)
        return avaliable_games

    def save(self, hand: Hand) -> None:
        hand.id = len(self._hands)
        self._hands.append(hand)

    def update(self, hand: Hand) -> None:
        self._hands[hand.id] = hand


games_repository = InMemoryGamesRepository()


# Singlenton for DI in services/managers
def dep_games_repository():
    return games_repository
