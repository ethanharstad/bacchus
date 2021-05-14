import random
import re
import logging
import json

import discord
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


# TODO speed mode
# TODO Rando Cardrissian
class CardsAgainstHumanity:
    key: str
    cards_per_hand: int
    questions: set
    answers: set
    players: dict

    def __init__(self, cards_per_hand=8):
        self.key = petname.Generate(2, "-")
        self.cards_per_hand = cards_per_hand
        self.questions = set()
        self.answers = set()
        self.players = dict()

    def add_player(self, player: Player):
        if player.id in self.players:
            return False
        self.players[player.id] = player
        logging.info("Players: {}".format(self.players))
        return True

    def remove_player(self, player: Player):
        return self.players.pop(player.id)

    def draw_answer(self):
        while True:
            a = random.choice(ANSWERS)
            if a not in self.answers:
                break
        self.answers.add(a)
        logging.info("Drew: {}".format(a))
        return a

    def draw_question(self):
        while True:
            q = random.choice(QUESTIONS)
            if q not in self.questions:
                break
        self.questions.add(q)
        logging.info("Drew: {}".format(q))
        return q

    def start_round(self):
        question = self.draw_question()
        for player in self.players.values():
            while len(player.hand) < self.cards_per_hand:
                player.hand.add(self.draw_answer())
        return question
