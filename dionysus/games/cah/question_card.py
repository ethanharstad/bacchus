import logging
from typing import List
from .answer_card import AnswerCard

logger = logging.getLogger(__name__)


class QuestionCard:
    id: int
    text: str
    pick: int

    def __init__(self, id, text, pick):
        self.id = id
        self.text = text
        self.pick = pick

    def __eq__(self, other):
        if isinstance(other, QuestionCard):
            return self.id == other.id
        return False

    def __hash__(self):
        return self.id

    def __str__(self):
        return self.render()

    def __repr__(self):
        return 'QuestionCard({0.id}, "{0.text}"[{0.pick}])'.format(self)

    def render(self, answers: List[AnswerCard] = None):
        has_answers = answers != None
        if not has_answers:
            answers = [r"\_\_\_\_\_" for i in range(self.pick)]
        else:
            if len(answers) != self.pick:
                raise ValueError(
                    "Question requires {pick} answers and {answers} were provided.".format(
                        pick=self.pick, answers=len(answers)
                    )
                )
            answers = [answer.render() for answer in answers]
        if "{}" in self.text:
            s = self.text.format(*answers)
        else:
            s = self.text
            if has_answers:
                s += "\n> " + "\n> ".join(answers)
        if has_answers == False and self.pick > 1:
            s += " (Pick {})".format(self.pick)
        return s

    def fill_in(self, answers: List[AnswerCard]):
        return self.render(answers)