from enum import IntEnum
import logging
import random
from typing import Dict, List

import petname
import pydealer

from .player import Player

logger = logging.getLogger(__name__)


class GameState(IntEnum):
    INIT = 0
    RED_OR_BLACK = 10
    HIGHER_OR_LOWER = 20
    INSIDE_OR_OUTSIDE = 30
    SUIT = 40


class RideTheBus:
    def __init__(self):
        self.key: str = petname.Generate(2, "-")
        self.players: Dict[str, Player] = {}
        self.play_order: List[str] = []
        self.state: GameState = GameState.INIT
        self._index = 0
        self._deck = pydealer.Deck()
        self._deck.shuffle()

    def add_player(self, id: str, name: str = None):
        # TODO add player update ability
        logger.info(f"Player {id}:{name} is attempting to join game {self.key}")
        self.players[id] = Player(id, name)

    def remove_player(self, id: str):
        pass

    def start(self):
        # set player order
        self.play_order = list(self.players.keys())
        random.shuffle(self.play_order)
        # init game
        self.state = GameState.RED_OR_BLACK

    def guess(self, player_id: str):
        if player_id != self.current_player.id:
            raise ValueError(
                f"Guessing player ({player_id}) is not the current player ({self.current_player.id})"
            )

    @property
    def current_player(self) -> Player:
        if self.state in [
            GameState.RED_OR_BLACK,
            GameState.HIGHER_OR_LOWER,
            GameState.INSIDE_OR_OUTSIDE,
            GameState.SUIT,
        ]:
            return self.players[self.play_order[self._index]]
        return None