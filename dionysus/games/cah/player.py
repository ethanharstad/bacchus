import logging

logger = logging.getLogger(__name__)


class Player:
    id: int
    name: str
    score: int
    hand: list

    def __init__(self, id, name="Anonymous"):
        self.id = id
        self.name = name
        self.score = 0
        self.hand = []

    def __eq__(self, other):
        if isinstance(other, Player):
            return self.id == other.id
        return False

    def __hash__(self):
        return self.id

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Player({0.id}, {0.name})".format(self)
