import random
import logging
import json

import discord
import petname

logging.basicConfig(level=logging.DEBUG)

GAME_DATA_PATHS = [
    "data/games/cah/cah-cards-compact.json",
]

QUESTIONS = []
ANSWERS = []


class AnswerCard:
    id: int
    text: str

    def __init__(self, id, text):
        self.id = id
        self.text = text

    def __eq__(self, other):
        if (isinstance(other, AnswerCard)):
            return self.id == other.id
        return False
    
    def __hash__(self):
        return self.id

    def __str__(self):
        return self.text

    def __repr__(self):
        return 'AnswerCard({0.id}, "{0.text}")'.format(self)


class QuestionCard:
    id: int
    text: str
    pick: int

    def __init__(self, id, text, pick):
        self.id = id
        self.text = text
        self.pick = pick
    
    def __eq__(self, other):
        if (isinstance(other, QuestionCard)):
            return self.id == other.id
        return False
    
    def __hash__(self):
        return self.id

    def __str__(self):
        s = self.text
        if self.pick > 1:
            s += " (Pick {})".format(self.pick)
        return s

    def __repr__(self):
        return 'QuestionCard({0.id}, "{0.text}"[{0.pick}])'.format(self)


class Player:
    id: int
    name: str
    score: int
    hand: set

    def __init__(self, id, name="Anonymous"):
        self.id = id
        self.name = name
        self.score = 0
        self.hand = set()
    
    def __eq__(self, other):
        if (isinstance(other, Player)):
            return self.id == other.id
        return False
    
    def __hash__(self):
        return self.id
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return "Player({0.id}, {0.name})".format(self)


for path in GAME_DATA_PATHS:
    with open(path, "r") as f:
        data = json.load(f)
        for i, d in enumerate(data["white"]):
            a = AnswerCard(i, d)
            ANSWERS.append(a)
            logging.info("Loaded: {}".format(a))
        for i, d in enumerate(data["black"]):
            q = QuestionCard(i, d["text"], d["pick"])
            QUESTIONS.append(q)
            logging.info("Loaded: {}".format(q))


class CardsAgainstHumanity:
    key: str
    questions: set
    answers: set
    players: dict

    def __init__(self):
        self.key = petname.Generate(2, "-")
        self.questions = set()
        self.answers = set()
        self.players = dict()

    def add_player(self, player: Player):
        if player.id in self.players:
            return False
        self.players[player.id] = player
        logging.info("Players: {}". format(self.players))
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
            while len(player.hand) < 5:
                player.hand.add(self.draw_answer())
        return question
