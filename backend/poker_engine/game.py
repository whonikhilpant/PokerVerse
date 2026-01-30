from typing import List, Dict, Optional
from .card import Deck, Card
from .hand_evaluator import HandEvaluator

class Player:
    def __init__(self, username: str, chips: float):
        self.username = username
        self.chips = chips # Chips available to bet
        self.hand: List[Card] = []
        self.current_bet = 0.0 # Amount bet in this round
        self.is_folded = False
        self.is_all_in = False

    def reset_for_round(self):
        self.hand = []
        self.current_bet = 0.0
        self.is_folded = False
        self.is_all_in = False

class Game:
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.players: List[Player] = []
        self.deck = Deck()
        self.community_cards: List[Card] = []
        self.pot = 0.0
        self.current_bet = 0.0 # High bet to call
        self.turn_index = 0
        self.dealer_index = 0
        self.game_stage = "PREFLOP" # PREFLOP, FLOP, TURN, RIVER, SHOWDOWN
        self.is_active = False

    def add_player(self, username: str, chips: float):
        if any(p.username == username for p in self.players):
            return
        self.players.append(Player(username, chips))

    def start_round(self):
        if len(self.players) < 2:
            return # Need 2 players
        
        self.is_active = True
        self.deck.reset()
        self.community_cards = []
        self.pot = 0.0
        self.current_bet = 0.0
        self.game_stage = "PREFLOP"

        # Shift dealer
        self.dealer_index = (self.dealer_index + 1) % len(self.players)
        
        # Reset players and deal
        for p in self.players:
            p.reset_for_round()
            p.hand = self.deck.deal(2)
            
        # Blinds (Simplified: Dealer is SB, next is BB for 2 players, or Dealer+1 SB, Dealer+2 BB)
        # Assuming SB=10, BB=20
        sb_index = (self.dealer_index + 1) % len(self.players)
        bb_index = (self.dealer_index + 2) % len(self.players)
        
        self._post_bet(self.players[sb_index], 10)
        self._post_bet(self.players[bb_index], 20)
        self.current_bet = 20
        
        # Action starts after BB
        self.turn_index = (bb_index + 1) % len(self.players)

    def _post_bet(self, player: Player, amount: float):
        if player.chips < amount:
            amount = player.chips # All-in
            player.is_all_in = True
        
        player.chips -= amount
        player.current_bet += amount
        self.pot += amount

    def player_action(self, username: str, action: str, amount: float = 0):
        # action: "call", "raise", "fold", "check"
        player = self.players[self.turn_index]
        if player.username != username:
            return {"error": "Not your turn"}
        
        if action == "fold":
            player.is_folded = True
        elif action == "call":
            to_call = self.current_bet - player.current_bet
            self._post_bet(player, to_call)
        elif action == "check":
            if player.current_bet < self.current_bet:
                return {"error": "Cannot check, must call"}
        elif action == "raise":
            if amount < self.current_bet:
                return {"error": "Raise must be greater than current bet"}
            self._post_bet(player, amount - player.current_bet) # post the difference
            self.current_bet = amount # Update high bet
            
        # Move turn
        self._next_turn()
        return {"status": "ok", "game_state": self.get_state()}

    def _next_turn(self):
        # Find next active player
        count = 0
        while count < len(self.players):
            self.turn_index = (self.turn_index + 1) % len(self.players)
            p = self.players[self.turn_index]
            if not p.is_folded and not p.is_all_in:
                return # Found valuable player
            count += 1
            
        # If we loop through everyone, round might be over
        self._advance_stage()

    def _advance_stage(self):
        # Simplified stage advancement
        if self.game_stage == "PREFLOP":
            self.game_stage = "FLOP"
            self.community_cards = self.deck.deal(3)
        elif self.game_stage == "FLOP":
            self.game_stage = "TURN"
            self.community_cards.append(self.deck.deal(1)[0])
        elif self.game_stage == "TURN":
            self.game_stage = "RIVER"
            self.community_cards.append(self.deck.deal(1)[0])
        elif self.game_stage == "RIVER":
            self.game_stage = "SHOWDOWN"
            self._resolve_winner()
        
        # Reset betting for new stage
        self.current_bet = 0
        for p in self.players:
            p.current_bet = 0
            
        # Turn starts left of dealer
        self.turn_index = (self.dealer_index + 1) % len(self.players)

    def _resolve_winner(self):
        # Use HandEvaluator
        best_rank = (-1, [])
        winners = []
        
        active_players = [p for p in self.players if not p.is_folded]
        for p in active_players:
            rank = HandEvaluator.evaluate(p.hand + self.community_cards)
            if rank > best_rank:
                best_rank = rank
                winners = [p]
            elif rank == best_rank:
                winners.append(p)
                
        # Split pot
        share = self.pot / len(winners)
        for w in winners:
            w.chips += share
            
        self.is_active = False

    def get_state(self):
        return {
            "room_id": self.room_id,
            "pot": self.pot,
            "stage": self.game_stage,
            "community_cards": [c.to_dict() for c in self.community_cards],
            "players": [{
                "username": p.username,
                "chips": p.chips,
                "bet": p.current_bet,
                "folded": p.is_folded,
                "is_turn": self.players[self.turn_index].username == p.username,
                "hand": [c.to_dict() for c in p.hand]  # ADD THIS LINE - send hole cards
            } for p in self.players]
        }
