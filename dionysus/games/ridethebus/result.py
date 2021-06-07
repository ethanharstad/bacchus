from .player import Player


class Result:
    def __init__(self, player, successful):
        self.player: Player = player
        self.successful: bool = successful
