import random
import re
import logging
import json
from enum import IntEnum
from typing import Iterable, Dict, Set, List

from discord.activity import Game

import petname

from .answer_card import AnswerCard
from .question_card import QuestionCard
from .player import Player

logger = logging.getLogger(__name__)

NUM_JUDGES = 0
GAME_DATA_PATHS = [
    "data/games/cah/cah-cards-compact.json",
]

QUESTIONS = []
ANSWERS = []


p = re.compile(r"\b_\b")
for path in GAME_DATA_PATHS:
    logger.info("Processing game data file: {}".format(path))
    with open(path, "r") as f:
        data = json.load(f)
        for i, d in enumerate(data["white"]):
            a = AnswerCard(i, d)
            ANSWERS.append(a)
            logger.debug("Loaded Answer: {}".format(a))
        logger.info(f"Loaded {i+1} answers")
        for i, d in enumerate(data["black"]):
            text = p.sub("{}", d["text"])
            q = QuestionCard(i, text, d["pick"])
            QUESTIONS.append(q)
            logger.debug("Loaded Question: {}".format(q))
        logger.info(f"Loaded {i+1} questions")
    logger.info("Done processing game data files")


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
        self.questions: Set[QuestionCard] = set()
        self.answers: Set[AnswerCard] = set()
        self.players: Dict[int, Player] = dict()
        self.play_order: List[int] = []
        self.round: int = 0
        self.judge_index: int = -1
        self.question: QuestionCard = None
        self.state: GameState = GameState.INIT
        self.submissions: Dict[int, List[AnswerCard]] = {}
        self.submission_mapping: List[int] = []
        self.winner: Player = None

    def add_player(self, player: Player):
        logger.info(
            f"Player {player.id}:{player.name} is attempting to join game {self.key}"
        )
        # Don't add players that already exist
        if player.id in self.players:
            return
        # Add the player to the list of players
        self.players[player.id] = player
        # Add the player to the play order
        if self.round == 0:
            # If the game hasn't started yet, play order is randomized
            self.play_order.insert(
                random.randrange(len(self.play_order) + 1), player.id
            )
        else:
            # If the game has already started, add to the end
            self.play_order.append(player.id)

        logger.info(f"Player {player.id}:{player.name} joined game {self.key}")
        logger.info("Players: {}".format(self.players))
        logger.info("Play Order: {}".format(self.play_order))
        return True

    def remove_player(self, player: Player):
        logger.info(f"Attempting to remove player {player.id}:{player.name}")
        # Can't remove a player that doesn't exist
        if player.id not in self.player:
            logger.warning(f"Player {player.id}:{player.name} does not exist")
            return False
        # Remove the player from the play order
        self.play_order.remove(player.id)
        # Remove the player from the list of players
        self.players.pop(player.id)
        logger.info(f"Removed player {player.id}:{player.name}")
        logger.info("Players: {}".format(self.players))
        logger.info("Play Order: {}".format(self.play_order))
        return True

    @staticmethod
    def _draw(pool: Iterable, values: Iterable):
        while True:
            x = random.choice(pool)
            if x not in values:
                return x

    def get_judge_id(self):
        return self.play_order[self.judge_index]

    def get_winner_id(self):
        return self.winner.id

    def draw_answer(self):
        a = CardsAgainstHumanity._draw(ANSWERS, self.answers)
        self.answers.add(a)
        logger.info("Drew Answer: {}".format(a))
        return a

    def draw_question(self):
        q = CardsAgainstHumanity._draw(QUESTIONS, self.questions)
        self.questions.add(q)
        logger.info("Drew Question: {}".format(q))
        return q

    def start_round(self):
        self.round += 1
        logger.info(f"Starting round {self.round}")
        logger.info(f"Player {self.get_judge_id} is judge")
        # Draw the question
        self.question = self.draw_question()
        # Reset submissions
        self.submissions = {}
        self.winner = None
        # Fill player hands
        self._fill_hands()

        self.state = GameState.WAITING_FOR_ANSWERS
        return self.question

    def _fill_hands(self):
        for player in self.players.values():
            logger.info(f"Filling player {player.id}:{player.name} hand")
            while len(player.hand) < self.cards_per_hand:
                player.hand.append(self.draw_answer())

    def submit_answer(self, player: Player, answers: list):
        logger.info(f"Player {player.id}:{player.name} attempting to submit {answers}")
        # Can't submit if you aren't a player
        if player.id not in self.players:
            raise ValueError("Player is not a member of the game.")
        # Can't submit if not in submission stage
        if self.state != GameState.WAITING_FOR_ANSWERS:
            raise ValueError("You cannot submit answers right now.")
        # Can't submit if you're the judge
        # if player.id == self.play_order[self.judge_index]:
        #     raise ValueError("The judge cannot submit answers.")
        # Must submit the correct number of answers
        if len(answers) != self.question.pick:
            raise ValueError(
                f"Player submitted {len(answers)} answers and the question requires {self.question.pick}."
            )
        # Add the submission, keyed by player id
        self.submissions[player.id] = answers
        logger.info("Submitted.")
        logger.info("submissions: {}".format(self.submissions))
        logger.info("State: {}".format(GameState(self.state)))

        # See if submissions are complete
        if self._check_answers():
            # Close out submissions
            self.finalize_answers()

        return True

    def _check_answers(self):
        remaining_players = (len(self.players) - NUM_JUDGES) - len(self.submissions)
        logger.info(f"Still waiting on {remaining_players} players.")
        return remaining_players <= 0

    def finalize_answers(self):
        # Remove submitted cards from players' hands
        for player_id, answer in self.submissions.items():
            # Player might not be real if random submission enabled
            if player_id in self.players:
                for card in answer:
                    self.players[player_id].hand.remove(card)
        self.submission_mapping = list(self.submissions.keys())
        random.shuffle(self.submission_mapping)
        self.state = GameState.WAITING_FOR_JUDGE
        logger.info(f"Answers finalized for round {self.round}.")

    def choose_winner(self, submission_id: int):
        if self.state != GameState.WAITING_FOR_JUDGE:
            raise ValueError("The game is not ready for judging.")

        winner_id = self.submission_mapping[submission_id]
        self.winner = self.players[winner_id]
        self.winner.score += 1

        self._finalize_round()
        return winner_id

    def _finalize_round(self):
        if self.state != GameState.WAITING_FOR_JUDGE:
            raise ValueError("The game is not ready for finalizing.")

        self.submission_mapping = []
        self.judge_index = (self.judge_index + 1) % len(self.play_order)
        self.state = GameState.ROUND_COMPLETE
