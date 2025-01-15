import random
from typing import List, Optional

from bot import Bot
from card import Card, CardType
from game_handling.game_state import GameState


class Jarvis(Bot):
    def play(self, state: GameState) -> Optional[Card]:
        defuse_cards = [card for card in self.hand if card.card_type == CardType.DEFUSE]
        if defuse_cards:
            playable_cards = [card for card in self.hand if card.card_type != CardType.DEFUSE]
            if playable_cards:
                return random.choice(playable_cards)
            return None

        see_the_future_cards = [card for card in self.hand if card.card_type == CardType.SEE_THE_FUTURE]
        if see_the_future_cards:
            return random.choice(see_the_future_cards)

        skip_cards = [card for card in self.hand if card.card_type == CardType.SKIP]
        if skip_cards:
            return random.choice(skip_cards)

        normal_cards = [card for card in self.hand if card.card_type == CardType.NORMAL]
        if normal_cards:
            return random.choice(normal_cards)

        return None

    def handle_exploding_kitten(self, state: GameState) -> int:
        defuse_cards = [card for card in self.hand if card.card_type == CardType.DEFUSE]
        if defuse_cards:
            return random.randint(0, len(state.deck) - 1)
        else:
            return -1

    def see_the_future(self, state: GameState, top_three: List[Card]):
        for card in top_three:
            if card.card_type == CardType.EXPLODING_KITTEN:
                skip_cards = [card for card in self.hand if card.card_type == CardType.SKIP]
                if skip_cards:
                    return random.choice(skip_cards)

        return None
