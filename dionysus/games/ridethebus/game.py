from enum import IntEnum
import logging
import random
from typing import Dict, List

import petname
import pydealer

from .player import Player
from .result import Result

logger = logging.getLogger(__name__)


class GameState(IntEnum):
    INIT = 0
    RED_OR_BLACK = 10
    HIGHER_OR_LOWER = 20
    INSIDE_OR_OUTSIDE = 30
    SUIT = 40
    PYRAMID = 50
    RIDE_THE_BUS = 90
    COMPLETE = 100


class RideTheBus:
    def __init__(self):
        # The "name" of this instance of the game
        self.key: str = petname.Generate(2, "-")
        # The players of this game by their id
        self.players: Dict[str, Player] = {}
        # The order that the players are in
        self.play_order: List[str] = []
        # The stage of the game
        self.state: GameState = GameState.INIT
        # The level of the pyramid
        self.level: int = 0
        # The cards in the pyramid
        self.pyramid: List[List[pydealer.Card]] = []
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

    def guess(self, player_id: str, guess: str):
        if player_id != self.current_player.id:
            raise ValueError(
                f"Guessing player ({player_id}) is not the current player ({self.current_player.id})"
            )
        player = self.current_player
        # Do things....
        # Draw card
        while True:
            card = self._deck.deal(1)[0]
            if self._validate_draw(player, card):
                break
            self._deck.add(card)
            self._deck.shuffle()
        self.current_player.cards.append(card)
        result = self._score_round(player, guess)

        # Move on
        self._index += 1
        if self._index >= len(self.players):
            self._next_round()

        return Result(player, result)

    def _validate_draw(self, player: Player, card: pydealer.Card):
        if self.state is GameState.HIGHER_OR_LOWER:
            return card.value != player.cards[-1].value
        elif self.state is GameState.INSIDE_OR_OUTSIDE:
            return card.value not in [player.cards[-1].value, player.cards[-1].value]
        return True

    def _score_round(self, player: Player, guess: str) -> bool:
        logger.info(f"{player.id} guessed {guess} for {player.cards}")
        dealt = player.cards[-1]
        if self.state is GameState.RED_OR_BLACK:
            if dealt.suit in ["Clubs", "Spades"]:
                color = "black"
            else:
                color = "red"
            return guess == color
        elif self.state is GameState.HIGHER_OR_LOWER:
            prev = player.cards[-2]
            higher = dealt > prev
            guess = guess == "higher"
            return (higher and guess) or (not higher and not guess)
        elif self.state is GameState.INSIDE_OR_OUTSIDE:
            bounds = player.cards[:-1]
            if bounds[1] < bounds[0]:
                bounds.reverse()
            logger.info(f"Checking {bounds[0]} < {dealt} < {bounds[1]}")
            inside = bounds[0] < dealt < bounds[1]
            guess = guess == "inside"
            return (inside and guess) or (not inside and not guess)
        elif self.state is GameState.SUIT:
            return dealt.suit.lower() == guess
        return None

    def _next_round(self):
        self._index = 0
        if self.state == GameState.RED_OR_BLACK:
            self.state = GameState.HIGHER_OR_LOWER
            return
        if self.state == GameState.HIGHER_OR_LOWER:
            self.state = GameState.INSIDE_OR_OUTSIDE
            return
        if self.state == GameState.INSIDE_OR_OUTSIDE:
            self.state = GameState.SUIT
            return
        if self.state == GameState.SUIT:
            self.state = GameState.PYRAMID
            return
        if self.state == GameState.PYRAMID:
            self.state = GameState.RIDE_THE_BUS
            return
        if self.state == GameState.RIDE_THE_BUS:
            self.state = GameState.COMPLETE
            return

    @property
    def player_list(self) -> List[Player]:
        return [self.players[id] for id in self.play_order]

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
