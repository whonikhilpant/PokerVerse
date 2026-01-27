from fastapi import WebSocket
from typing import List, Dict
from .game import Game
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {} # room_id -> [websockets]
        self.games: Dict[str, Game] = {} # room_id -> Game

    async def connect(self, websocket: WebSocket, room_id: str, username: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
            self.games[room_id] = Game(room_id)
        
        self.active_connections[room_id].append(websocket)
        
        # Add player to game logic
        # For simplicity, we assume they bring 1000 chips. Real app would deduct from DB.
        game = self.games[room_id]
        if username not in [p.username for p in game.players]:
            game.add_player(username, chips=1000.0)
        
        await self.broadcast(room_id, {"type": "player_joined", "username": username, "state": game.get_state()})

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            if websocket in self.active_connections[room_id]:
                self.active_connections[room_id].remove(websocket)

    async def broadcast(self, room_id: str, message: dict):
        if room_id in self.active_connections:
            # Iterate over a copy to avoid modification during iteration issues
            for connection in self.active_connections[room_id].copy():
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    # Handle disconnected clients
                    self.disconnect(connection, room_id)

    async def handle_command(self, room_id: str, username: str, command: dict):
        game = self.games.get(room_id)
        if not game:
            return
        
        action = command.get("action")
        amount = command.get("amount", 0)
        
        if action == "start_game":
            game.start_round()
            await self.broadcast(room_id, {"type": "game_update", "state": game.get_state(), "message": "Game Started"})
        elif action in ["call", "raise", "fold", "check"]:
            result = game.player_action(username, action, amount)
            await self.broadcast(room_id, {"type": "game_update", "state": game.get_state(), "result": result})

manager = ConnectionManager()
