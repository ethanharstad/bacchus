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