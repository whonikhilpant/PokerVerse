import random
from enum import Enum
from typing import List

class Suit(str, Enum):
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"
    CLUBS = "Clubs"
    SPADES = "Spades"

class Rank(str, Enum):
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"

# Mapping for comparison
RANK_VALUES = {
    Rank.TWO: 2, Rank.THREE: 3, Rank.FOUR: 4, Rank.FIVE: 5,
    Rank.SIX: 6, Rank.SEVEN: 7, Rank.EIGHT: 8, Rank.NINE: 9,
    Rank.TEN: 10, Rank.JACK: 11, Rank.QUEEN: 12, Rank.KING: 13, Rank.ACE: 14
}

class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f"{self.rank.value} of {self.suit.value}"

    def __lt__(self, other):
        if RANK_VALUES[self.rank] != RANK_VALUES[other.rank]:
            return RANK_VALUES[self.rank] < RANK_VALUES[other.rank]
        return self.suit.value < other.suit.value # Suit order arbitrary

    def to_dict(self):
        return {"rank": self.rank.value, "suit": self.suit.value, "string": str(self)}

class Deck:
    def __init__(self):
        self.cards: List[Card] = []
        self.reset()

    def reset(self):
        self.cards = [Card(rank, suit) for suit in Suit for rank in Rank]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, count: int = 1) -> List[Card]:
        if len(self.cards) < count:
            raise ValueError("Not enough cards in deck")
        return [self.cards.pop() for _ in range(count)]
