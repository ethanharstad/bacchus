import random
import re
import logging
import json
from enum import IntEnum
from typing import Iterable

from discord.activity import Game

import petname

from .answer_card import AnswerCard
from .question_card import QuestionCard
from .player import Player

logging.basicConfig(level=logging.DEBUG)

GAME_DATA_PATHS = [
    "data/games/cah/cah-cards-compact.json",
]

QUESTIONS = []
ANSWERS = []


p = re.compile(r"\b_\b")
for path in GAME_DATA_PATHS:
    logging.info("Processing game data file: {}".format(path))
    with open(path, "r") as f:
        data = json.load(f)
        for i, d in enumerate(data["white"]):
            a = AnswerCard(i, d)
            ANSWERS.append(a)
            logging.info("Loaded: {}".format(a))
        for i, d in enumerate(data["black"]):
            text = p.sub(r"\_\_\_\_\_", d["text"])
            q = QuestionCard(i, text, d["pick"])
            QUESTIONS.append(q)
            logging.info("Loaded: {}".format(q))


class GameState(IntEnum):
    INIT = 0
    WAITING_FOR_ANSWERS = 1
    WAITING_FOR_JUDGE = 2
    ROUND_COMPLETE = 3
    GAME_OVER = 4

# TODO speed mode
# TODO Rando Cardrissian
class CardsAgainstHumanity:

    def __init__(self, cards_per_hand=8):
        self.key: str = petname.Generate(2, "-")
        self.cards_per_hand: int = cards_per_hand
        self.questions: set = set()
        self.answers: set = set()
        self.players: dict = dict()
        self.play_order: list = []
        self.round: int = 0
        self.judge_index: int = -1
        self.question: QuestionCard = None
        self.state: GameState = GameState.INIT
        self.submissions: dict = {}

    def add_player(self, player: Player):
        # Don't add players that already exist
        if player.id in self.players:
            return False
        # Add the player to the list of players
        self.players[player.id] = player
        # Add the player to the play order
        if self.round == 0:
            # If the game hasn't started yet, play order is randomized
            self.play_order.insert(
                random.randrange(len(self.play_order) + 1),
                player.id
            )
        else:
            # If the game has already started, add to the end
            self.play_order.append(player.id)
        
        logging.info("Players: {}".format(self.players))
        logging.info("Play Order: {}".format(self.play_order))
        return True

    def remove_player(self, player: Player):
        # Can't remove a player that doesn't exist
        if player.id not in self.player:
            return False
        # Remove the player from the play order
        self.play_order.remove(player.id)
        # Remove the player from the list of players
        self.players.pop(player.id)
        return True

    @staticmethod
    def _draw(pool: Iterable, values: Iterable):
        while True:
            x = random.choice(pool)
            if x not in values:
                return x

    def draw_answer(self):
        a = CardsAgainstHumanity._draw(ANSWERS, self.answers)
        self.answers.add(a)
        logging.info("Drew Answer: {}".format(a))
        return a

    def draw_question(self):
        q = CardsAgainstHumanity._draw(QUESTIONS, self.questions)
        self.questions.add(q)
        logging.info("Drew Question: {}".format(q))
        return q

    def start_round(self):
        self.round += 1
        self.question = self.draw_question()
        self.submissions = {}
        for player in self.players.values():
            while len(player.hand) < self.cards_per_hand:
                player.hand.append(self.draw_answer())
        
        self.state = GameState.WAITING_FOR_ANSWERS
        return self.question
    
    def submit_answer(self, player: Player, answer: list):
        # Can't submit if you aren't a player
        if player.id not in self.players:
            return False
        # Can't submit if you're the judge
        if player.id == self.play_order[self.judge_index]:
            return False
        # Must submit the correct number of answers
        if len(answer) != self.question.pick:
            return False
        # Add the submission, keyed by player id
        self.submissions[player.id] = answer
        # See if submissions are complete
        if len(self.submissions) >= (len(self.players) - 1):
            self.state = GameState.WAITING_FOR_JUDGE
        
        logging.info('Submissions: {}'.format(self.submissions))
        logging.info('State: {}'.format(self.state))
        return True

    def choose_winner(self, answer: AnswerCard):
        pass
