from enum import Enum

import pydealer

from .cdn import CDN_HOST

class FrontStyle(Enum):
    STANDARD = 'standard'

class BackStyle(Enum):
    BLUE = 'blue'
    BLUE_ALT = 'blue2'
    RED = 'red'
    RED_ALT = 'red2'

def get_card_image_url(card: pydealer.Card, style:FrontStyle = FrontStyle.STANDARD) -> str:
    return f"{CDN_HOST}/images/playing-cards/{style.value}/{card.suit.lower()}_{card.value.lower()}.png"
    
def get_card_back_image_url(style:BackStyle = BackStyle.RED) -> str:
    return f"{CDN_HOST}/images/playing-cards/backs/{style.value}.png"