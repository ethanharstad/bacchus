from enum import Enum

import pydealer

from .cdn import CDN_HOST

class Deck(Enum):
    STANDARD = 'standard'

def get_card_image_url(card: pydealer.Card, deck:Deck = Deck.STANDARD):
    return f"{CDN_HOST}/images/playing-cards/{deck.value}/{card.suit.lower()}_{card.value.lower()}.png"