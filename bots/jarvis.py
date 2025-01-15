import random
from typing import List, Optional

from bot import Bot
from card import Card, CardType
from game_handling.game_state import GameState

class Jarvis(Bot):
    def play(self, state: GameState) -> Optional[Card]:
        pass

    def handle_exploding_kitten(self, state: GameState) -> int:
        pass

    def see_the_future(self, state: GameState, top_three: List[Card]):
        pass
