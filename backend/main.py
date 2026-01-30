from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import models, schemas, database, auth
from .poker_engine.manager import manager
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables (Sync engine used in sync context? No, create_all is sync)
    # But usually we allow sync blocking calls in startup? 
    # Or strict updated version:
    models.Base.metadata.create_all(bind=database.engine)
    yield

app = FastAPI(title="PokerVerse API", lifespan=lifespan)

# CORS (Allow frontend)
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to PokerVerse API"}

@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # Check if user exists
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        chips=1000.0 # Initial bonus
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    # Authenticate user
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.post("/deposit", response_model=schemas.TransactionResponse)
def deposit_chips(amount: float, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    # Create transaction
    transaction = models.Transaction(
        user_id=current_user.id,
        amount=amount,
        transaction_type="DEPOSIT"
    )
    # Update balance
    current_user.chips += amount
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

    
@app.get("/transactions", response_model=list[schemas.TransactionResponse])
def get_transactions(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    """Get all transactions for the current user"""
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id
    ).order_by(models.Transaction.timestamp.desc()).all()
    return transactions

@app.get("/leaderboard")
def get_leaderboard(db: Session = Depends(database.get_db)):
    """Get top 10 players by chip count"""
    top_players = db.query(models.User).order_by(
        models.User.chips.desc()
    ).limit(10).all()
    
    return [{
        "rank": i + 1,
        "username": player.username,
        "chips": player.chips
    } for i, player in enumerate(top_players)]

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, token: str = None):
    # Accept connection first
    await websocket.accept()
    
    # Then authenticate via query param token
    try:
        if token is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
             await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
             return
    except auth.JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Add player to game (connection already accepted in manager.connect, so skip that)
    game = manager.games.get(room_id)
    if game is None:
        from .poker_engine.game import Game
        manager.games[room_id] = Game(room_id)
        manager.active_connections[room_id] = []
        game = manager.games[room_id]
    
    if room_id not in manager.active_connections:
        manager.active_connections[room_id] = []
    
    manager.active_connections[room_id].append(websocket)
    
    if username not in [p.username for p in game.players]:
        game.add_player(username, chips=1000.0)
    
    await manager.broadcast(room_id, {"type": "player_joined", "username": username, "state": game.get_state()})
    
    try:
        while True:
            data = await websocket.receive_json()
            await manager.handle_command(room_id, username, data)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        await manager.broadcast(room_id, {"type": "player_left", "username": username})

