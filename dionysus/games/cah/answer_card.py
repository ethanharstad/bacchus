import logging

logger = logging.getLogger(__name__)

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
    
    def render(self):
        return f"**{self.text.rstrip('.')}**"