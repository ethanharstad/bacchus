import logging
from typing import List

from pydealer import Card

logger = logging.getLogger(__name__)


class Player:
    def __init__(self, id, name=None):
        self.id: str = id
        self.name: str = name
        self.cards: List[Card] = []
        self.points: int = 0

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, o: object) -> bool:
        return self.__class__ == o.__class__ and self.id == o.id