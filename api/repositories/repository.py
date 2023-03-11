import abc
from typing import List, Optional
from models.models import Game, Hand, Score, Player


class AbstractPlayerRepository(abc.ABC):
    @abc.abstractmethod
    def get_by_id(self, id: int) -> Optional[Player]:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, player: Player) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, player: Player) -> None:
        raise NotImplementedError


class InMemoryPlayersRepository(AbstractPlayerRepository):
    _players: List[Player]

    def __init__(self):
        self._players = []

    def get_by_id(self, id) -> Optional[Player]:
        for player in self._players:
            if player.id == id:
                return player
        return None

    def save(self, player: Player) -> None:
        self._players.append(player)

    def update(self, player: Player) -> None:
        # Obtengo el index del jugador en el array
        # lo reeemplazo
        pass


players_repository: InMemoryPlayersRepository = InMemoryPlayersRepository()


def dep_players_repository() -> AbstractPlayerRepository:
    return players_repository


class AbstractHandRepository(abc.ABC):
    @abc.abstractmethod
    def get_by_id(self, id: str) -> Optional[Hand]:
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


class InMemoryHandRepository(AbstractHandRepository):
    _hands: List[Hand]

    def __init__(self):
        self._hands = []

    def get_by_id(self, id: str) -> Optional[Hand]:
        for hand in self._hands:
            if hand.id == id:
                return hand

        return None

    def get_availables(self) -> List[Hand]:
        avaliable_games = []
        for game in self._hands:
            if len(game.players) < 2:
                avaliable_games.append(game)
        return avaliable_games

    def save(self, hand: Hand) -> None:
        self._hands.append(hand)

    def update(self, hand: Hand) -> None:
        hand_index = self._hands.index(self.get_by_id(id=hand.id))
        self._hands[hand_index] = hand


hand_repository: AbstractHandRepository = InMemoryHandRepository()


# Singlenton for DI in services/managers
def dep_hand_repository() -> AbstractHandRepository:
    return hand_repository


class AbstractScoreRepository(abc.ABC):
    @abc.abstractmethod
    def get_by_id(self, id: int) -> Hand:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, hand: Hand) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, hand: Hand) -> None:
        raise NotImplementedError


class InMemoryScoreRepository(AbstractScoreRepository):
    _scores: List[Score]

    def __init__(self):
        self._scores = []

    def get_by_id(self, id: int) -> Optional[Score]:
        for score in self._scores:
            if score.id == id:
                return score

        return None

    def save(self, score: Score) -> None:
        self._scores.append(score)

    def update(self, score: Score) -> None:
        score_index = self._scores.index(self.get_by_id(id=score.id))
        self._scores[score_index] = score


scores_repository: AbstractScoreRepository = InMemoryScoreRepository()


def dep_scores_repository() -> AbstractScoreRepository:
    return scores_repository


class AbstractGameRepository(abc.ABC):
    @abc.abstractmethod
    def get_by_id(self, id: str) -> Optional[Game]:
        raise NotImplementedError

    @abc.abstractmethod
    def avaliable_games(self) -> List[Game]:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, game: Game) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, game: Game) -> None:
        raise NotImplementedError


class InMemoryGameRepository(AbstractGameRepository):
    _games: List[Game]

    def __init__(self):
        self._games = []

    def get_by_id(self, id: int) -> Optional[Game]:
        for game in self._games:
            if game.id == id:
                return game

        return None

    def avaliable_games(self) -> List[Game]:
        availables = []
        for game in self._games:
            if len(game.players) < game.rules:
                availables.append(game)
        return availables

    def save(self, game: Game) -> None:
        self._games.append(game)

    def update(self, game: Game) -> None:
        game_index = self._scores.index(self.get_by_id(id=game.id))
        self._games[game_index] = game


game_repository: InMemoryGameRepository = InMemoryGameRepository()


def dep_game_repository() -> AbstractGameRepository:
    return game_repository
