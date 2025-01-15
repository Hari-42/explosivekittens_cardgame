import random
from typing import List, Optional
from bot import Bot
from card import Card, CardType
from game_handling.game_state import GameState
from enum import Enum

class ProbabilityOfNextExploding(Enum):
    DEFINITELY = 1.0
    PROBABLY = 0.5
    UNSURE = 0.3
    DEFINITELY_NOT = 0.0

class Jarvis(Bot):
    def __init__(self, name: str):
        super().__init__(name)
        self.probability_of_next_exploding = [ProbabilityOfNextExploding.UNSURE]

    def play(self, state: GameState) -> Optional[Card]:
        """
        Decide which card to play based on game state and card priorities.
        """
        # Step 1: Prioritize SEE THE FUTURE cards
        see_the_future_cards = self._get_cards_of_type(CardType.SEE_THE_FUTURE)
        if see_the_future_cards:
            return see_the_future_cards[0]

        # Step 2: Calculate the probability of drawing an Exploding Kitten
        probability_of_exploding_next = self._calculate_exploding_kitten_probability(state)

        # If the probability of drawing an Exploding Kitten is high, use SKIP card if available
        if probability_of_exploding_next > ProbabilityOfNextExploding.UNSURE.value:
            skip_card = self._play_skip_card()
            if skip_card:
                return skip_card

        # Step 3: If no threat, play NORMAL cards
        normal_cards = self._get_cards_of_type(CardType.NORMAL)
        if normal_cards:
            return random.choice(normal_cards)

        # Step 4: If no cards to play, draw a card and hope for the best
        return None

    def handle_exploding_kitten(self, state: GameState) -> int:
        """
        Decide where to place the Exploding Kitten in the deck.
        """
        position = self._calculate_exploding_kitten_position(state)
        print(f"Placing Exploding Kitten back into position {position} of the deck.")
        return position

    def see_the_future(self, state: GameState, top_three: List[Card]) -> Optional[Card]:
        """
        Analyze the top three cards revealed by SEE THE FUTURE and adjust strategy.
        """
        danger_positions = self._find_exploding_kitten_positions(top_three)

        # Handle immediate danger
        if danger_positions:
            if danger_positions[0] == 0:
                return self._handle_imminent_danger()

            self._prepare_for_future_danger()

        # If safe, return None to take no action
        return None

    # ------------------------------------------
    # Helper Methods for Structure Clarity
    # ------------------------------------------

    def _get_cards_of_type(self, card_type: CardType) -> List[Card]:
        """
        Retrieve all cards of a given type from the bot's hand.
        """
        return [card for card in self.hand if card.card_type == card_type]

    def _calculate_exploding_kitten_probability(self, state: GameState) -> float:
        """
        Calculate the probability of drawing an Exploding Kitten based on the current game state.
        """
        exploding_kittens_left = state.alive_bots - 1
        probability_of_exploding_next = exploding_kittens_left / state.cards_left

        if len(self.probability_of_next_exploding) > 0:
            if self.probability_of_next_exploding[0] == ProbabilityOfNextExploding.DEFINITELY:
                probability_of_exploding_next = ProbabilityOfNextExploding.DEFINITELY.value
            elif self.probability_of_next_exploding[0] == ProbabilityOfNextExploding.DEFINITELY_NOT:
                probability_of_exploding_next = ProbabilityOfNextExploding.DEFINITELY_NOT.value

        return probability_of_exploding_next

    def _play_skip_card(self) -> Optional[Card]:
        """
        Play a SKIP card to avoid danger.
        """
        skip_cards = self._get_cards_of_type(CardType.SKIP)
        if skip_cards:
            return random.choice(skip_cards)
        return None

    def _find_exploding_kitten_positions(self, top_three: List[Card]) -> List[int]:
        """
        Identify the positions of any Exploding Kittens in the top three cards.
        """
        return [i for i, card in enumerate(top_three) if card.card_type == CardType.EXPLODING_KITTEN]

    def _handle_imminent_danger(self) -> Optional[Card]:
        """
        Handle the scenario where an Exploding Kitten is imminent and SKIP should be used.
        """
        skip_cards = self._get_cards_of_type(CardType.SKIP)
        if skip_cards:
            print("Using SKIP to avoid imminent Exploding Kitten.")
            return skip_cards[0]
        return None

    def _prepare_for_future_danger(self) -> None:
        """
        Prepare for future danger when Exploding Kittens are detected.
        """
        print("Danger is near, preparing to avoid it in the next turns.")

    def _calculate_exploding_kitten_position(self, state: GameState) -> int:
        """
        Calculate the optimal position for the Exploding Kitten based on the deck and players.
        """
        if state.cards_left > state.alive_bots:
            return state.cards_left // state.alive_bots
        return random.randint(0, state.cards_left - 1)

    def place_exploding_kitten(self, state: GameState) -> int:
        """
        Place the Exploding Kitten in a position that maximizes the chance of other players drawing it and exploding.
        Factors considered:
        - Turn order
        - Number of players left
        - Number of defuse cards remaining
        - Remaining cards in the deck
        """

        # Calculate the ideal position based on several factors
        ideal_position = state.cards_left - 1  # Default to placing it near the end of the deck

        # If it's near the end of the deck and there are multiple players with defuse cards, try to spread the risk
        if state.cards_left > 10 and state.alive_bots > 2:
            # In a larger deck, place it in the middle to maximize spreading the risk across players
            ideal_position = state.cards_left // 2 + random.randint(0, 2)
        elif state.alive_bots == 2:
            # If only two players are left, place it right before the end to ensure one player faces the danger
            ideal_position = state.cards_left - 3

        # If few defuse cards are left, place it earlier to prevent players from defusing it later
        defuses_played = len([card for card in state.history_of_played_cards if card.card_type == CardType.DEFUSE])
        defuses_left = (state.alive_bots * 1) - defuses_played  # Assume each player started with one defuse card
        if defuses_left < 2:
            # Fewer defuses, place the Exploding Kitten earlier to increase its threat
            ideal_position = max(1, state.cards_left // 4)  # Place it earlier in the deck

        # If the deck is small, place it near the end for increased likelihood of exploding
        if state.cards_left <= 5:
            ideal_position = state.cards_left - 1  # Close to the end for a high-risk play

        # Output the chosen position for debugging purposes
        print(f"Placing Exploding Kitten at position {ideal_position} to maximize risk for other players.")

        # Return the ideal position to place the Exploding Kitten
        return ideal_position

    def track_game_history(self, state: GameState):
        """
        Use the game's history to gain insights and adjust gameplay.
        """
        self._track_exploding_kittens(state)
        self._track_skip_cards(state)
        self._warn_about_defuses(state)

    def _track_exploding_kittens(self, state: GameState):
        """
        Track how many Exploding Kittens have been played.
        """
        exploding_kittens_played = [
            card for card in state.history_of_played_cards if card.card_type == CardType.EXPLODING_KITTEN
        ]
        print(f"Exploding Kittens removed from the game: {len(exploding_kittens_played)}")

    def _track_skip_cards(self, state: GameState):
        """
        Track SKIP cards played by opponents.
        """
        skips_played = [
            card for card in state.history_of_played_cards if card.card_type == CardType.SKIP
        ]
        print(f"SKIP cards played so far: {len(skips_played)}")

    def _warn_about_defuses(self, state: GameState):
        """
        Adjust strategy if most DEFUSE cards are gone.
        """
        defuses_played = [
            card for card in state.history_of_played_cards if card.card_type == CardType.DEFUSE
        ]
        if len(defuses_played) >= state.alive_bots:
            print("Most players are out of DEFUSE cards. Play cautiously!")
