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
        self.has_acted = False  # NEW: Track if player has acted this round

    def reset_for_round(self):
        self.hand = []
        self.current_bet = 0.0
        self.is_folded = False
        self.is_all_in = False
        self.has_acted = False

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
        self.winners: List[str] = []

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
        self.winners = []

        # Shift dealer
        self.dealer_index = (self.dealer_index + 1) % len(self.players)
        
        # Reset players and deal
        for p in self.players:
            p.reset_for_round()
            p.hand = self.deck.deal(2)
            
        # Blinds (Simplified: Dealer is SB, next is BB for 2 players)
        # Assuming SB=10, BB=20
        sb_index = (self.dealer_index + 1) % len(self.players)
        bb_index = (self.dealer_index + 2) % len(self.players) if len(self.players) > 2 else (self.dealer_index) % len(self.players)
        
        self._post_bet(self.players[sb_index], 10)
        self._post_bet(self.players[bb_index], 20)
        self.current_bet = 20
        
        # Action starts after BB (blinds are forced bets, not voluntary actions)
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
            player.has_acted = True
        elif action == "call":
            to_call = self.current_bet - player.current_bet
            self._post_bet(player, to_call)
            player.has_acted = True
        elif action == "check":
            if player.current_bet < self.current_bet:
                return {"error": "Cannot check, must call"}
            player.has_acted = True
        elif action == "raise":
            if amount <= self.current_bet:
                return {"error": "Raise must be greater than current bet"}
            to_raise = amount - player.current_bet
            self._post_bet(player, to_raise)
            self.current_bet = amount
            player.has_acted = True
            # Reset has_acted for other players since there's a new bet
            for p in self.players:
                if p.username != username:
                    p.has_acted = False
            
        # Move turn
        self._next_turn()
        return {"status": "ok", "game_state": self.get_state()}

    def _next_turn(self):
        # Check if betting round is complete
        active_players = [p for p in self.players if not p.is_folded and not p.is_all_in]
        
        # If only one player left, they win
        if len(active_players) <= 1:
            self._resolve_winner()
            return
        
        # Find next active player first
        count = 0
        while count < len(self.players):
            self.turn_index = (self.turn_index + 1) % len(self.players)
            p = self.players[self.turn_index]
            if not p.is_folded and not p.is_all_in:
                # Found next player - now check if betting round should end
                # Round ends when we circle back to a player who has already acted
                # AND all active players have matched the current bet
                all_matched = all(p.current_bet == self.current_bet for p in active_players)
                
                if p.has_acted and all_matched:
                    # This player already acted and everyone matched - round is complete
                    self._advance_stage()
                    return
                else:
                    # This player needs to act
                    return
            count += 1

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
            return
        
        # Reset betting for new stage
        self.current_bet = 0
        for p in self.players:
            p.current_bet = 0
            p.has_acted = False
            
        # Turn starts left of dealer
        self.turn_index = (self.dealer_index + 1) % len(self.players)

    def _resolve_winner(self):
        # Use HandEvaluator
        best_rank = (-1, [])
        winners = []
        
        active_players = [p for p in self.players if not p.is_folded]
        
        # If only one player left, they win
        if len(active_players) == 1:
            winners = active_players
        else:
            # Evaluate hands
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
            
        self.winners = [w.username for w in winners]
        self.is_active = False

    def get_state(self):
        return {
            "room_id": self.room_id,
            "pot": self.pot,
            "stage": self.game_stage,
            "community_cards": [c.to_dict() for c in self.community_cards],
            "current_bet": self.current_bet,
            "is_active": self.is_active,
            "players": [{
                "username": p.username,
                "chips": p.chips,
                "bet": p.current_bet,
                "folded": p.is_folded,
                "is_turn": self.players[self.turn_index].username == p.username if self.is_active else False,
                "hand": [c.to_dict() for c in p.hand]
            } for p in self.players],
            "winners": self.winners
        }
