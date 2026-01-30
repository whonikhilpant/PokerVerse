from collections import Counter
import itertools
from .card import Card, Rank, Suit, RANK_VALUES

class HandRank(int):
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10
    
    @classmethod
    def to_string(cls, rank):
        return {
            1: "High Card",
            2: "Pair",
            3: "Two Pair",
            4: "Three of a Kind",
            5: "Straight",
            6: "Flush",
            7: "Full House",
            8: "Four of a Kind",
            9: "Straight Flush",
            10: "Royal Flush"
        }.get(rank, "Unknown")

class HandEvaluator:
    @staticmethod
    def evaluate(cards: list[Card]):
        """
        Evaluates the best 5-card hand from a list of 5-7 cards.
        Returns a tuple: (HandRank, kickers_list) which can be compared directly.
        """
        if not cards or len(cards) < 5:
            # Not enough cards to make a hand
            return (0, [])
        
        return HandEvaluator._get_best_hand(cards)

    @staticmethod
    def _get_best_hand(cards: list[Card]):
        best_score = (-1, [])
        
        # Generate all 5-card combinations from the available cards
        combinations = itertools.combinations(cards, 5)
        for hand in combinations:
            score = HandEvaluator._score_five_cards(list(hand))
            # Tuple comparison logic works naturally in Python: (RANK, [kicker1, kicker2...])
            if score > best_score:
                best_score = score
        
        return best_score

    @staticmethod
    def _score_five_cards(cards: list[Card]):
        # Sort ranks high to low
        ranks = sorted([RANK_VALUES[c.rank] for c in cards], reverse=True)
        suits = [c.suit for c in cards]
        rank_counts = Counter(ranks)
        
        is_flush = len(set(suits)) == 1
        is_straight = (max(ranks) - min(ranks) == 4) and (len(set(ranks)) == 5)
        
        # Ace low straight check (A, 5, 4, 3, 2) -> Ranks: [14, 5, 4, 3, 2]
        if set(ranks) == {14, 5, 4, 3, 2}:
            is_straight = True
            ranks = [5, 4, 3, 2, 1] # Treat Ace as 1 for comparison
            
        if is_straight and is_flush:
            if max(ranks) == 14: return (HandRank.ROYAL_FLUSH, ranks)
            return (HandRank.STRAIGHT_FLUSH, ranks)
            
        if 4 in rank_counts.values():
            quads = [r for r, c in rank_counts.items() if c == 4]
            kickers = [r for r in ranks if r not in quads]
            return (HandRank.FOUR_OF_A_KIND, quads + kickers)
            
        if 3 in rank_counts.values() and 2 in rank_counts.values():
            trips = [r for r, c in rank_counts.items() if c == 3]
            pair = [r for r, c in rank_counts.items() if c == 2]
            return (HandRank.FULL_HOUSE, trips + pair)
            
        if is_flush:
            return (HandRank.FLUSH, ranks)
            
        if is_straight:
            return (HandRank.STRAIGHT, ranks)
            
        if 3 in rank_counts.values():
            trips = [r for r, c in rank_counts.items() if c == 3]
            kickers = [r for r in ranks if r not in trips]
            return (HandRank.THREE_OF_A_KIND, trips + kickers)
            
        if list(rank_counts.values()).count(2) == 2:
            pairs = sorted([r for r, c in rank_counts.items() if c == 2], reverse=True)
            kickers = [r for r in ranks if r not in pairs]
            return (HandRank.TWO_PAIR, pairs + kickers)
            
        if 2 in rank_counts.values():
            pair = [r for r, c in rank_counts.items() if c == 2]
            kickers = [r for r in ranks if r not in pair]
            return (HandRank.PAIR, pair + kickers)
            
        return (HandRank.HIGH_CARD, ranks)
