import sys
import os

# Add current dir to path to find poker_engine
sys.path.append(os.getcwd())

from poker_engine.game import Game

def test_betting_round():
    print("Initializing Game...")
    g = Game("test_room")
    g.add_player("Alice", 1000)
    g.add_player("Bob", 1000)
    
    print("Starting Round...")
    g.start_round()
    
    # Identify SB and BB based on bets
    p1 = g.players[0]
    p2 = g.players[1]
    
    sb_player = None
    bb_player = None
    
    if p1.current_bet == 10 and p2.current_bet == 20:
        sb_player = p1
        bb_player = p2
    elif p2.current_bet == 10 and p1.current_bet == 20:
        sb_player = p2
        bb_player = p1
    else:
        print(f"FAIL: Blinds incorrect. P1:{p1.current_bet}, P2:{p2.current_bet}")
        return

    print(f"SB: {sb_player.username}, BB: {bb_player.username}")

    # Check "Have Acted" - should be False after my fix
    if sb_player.has_acted or bb_player.has_acted:
        print(f"FAIL: Blinds marked as acted prematurely. SB:{sb_player.has_acted}, BB:{bb_player.has_acted}")
        return
    else:
        print("SUCCESS: Blinds start as has_acted=False")
        
    # Check Turn - Should be SB player in Heads Up (Dealer acts first)
    current_player = g.players[g.turn_index]
    print(f"Current Turn: {current_player.username} (Expected SB: {sb_player.username})")
    
    if current_player.username != sb_player.username:
        print("FAIL: Wrong player start")
        # Continue anyway to see flow
        
    # First Player Calls (Matches 20)
    print(f"{current_player.username} Calls...")
    res = g.player_action(current_player.username, "call")
    if res.get("error"):
        print(f"FAIL: Call error: {res}")
        return
        
    print(f"Game Stage: {g.game_stage} (Expected PREFLOP)")
    
    if g.game_stage != "PREFLOP":
        print("FAIL: Game advanced to FLOP prematurely! BB didn't get to act!")
        return

    # Now Second Player (BB) turn
    current_player = g.players[g.turn_index]
    print(f"Current Turn: {current_player.username} (Expected BB: {bb_player.username})")
    
    # BB Checks
    print(f"{current_player.username} Checks...")
    res = g.player_action(current_player.username, "check")
    if res.get("error"):
        print(f"FAIL: Check error: {res}")
        return
        
    print(f"Game Stage: {g.game_stage} (Expected FLOP)")
    print(f"Community Cards: {len(g.community_cards)} (Expected 3)")
    
    if g.game_stage == "FLOP" and len(g.community_cards) == 3:
        print("SUCCESS: Game flow is correct. Advanced to FLOP after checking.")
    else:
        print(f"FAIL: Game did not advance to FLOP properly. Stage: {g.game_stage}")

if __name__ == "__main__":
    test_betting_round()
