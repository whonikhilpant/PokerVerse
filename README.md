# PokerVerse

A multiplayer Texas Hold'em Poker platform built with FastAPI and React.

## 🚀 Quick Start

### 1. Start Backend
The backend runs on Python 3.14 (with SQLite).
```bash
# In one terminal
cd backend
venv\Scripts\python.exe -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
*Wait for "Application startup complete"*

### 2. Start Frontend
The frontend runs on Vite + React.
```bash
# In another terminal
cd frontend
npm run dev
```
Access at: http://localhost:5173

## ⚠️ Troubleshooting

**"Registration unable to fetch"**
- Ensure Backend is running on port 8000.
- Ensure you are visiting http://localhost:5173 (not 5174 or others).
- Restart the backend with `--host 0.0.0.0` as shown above.

**"500 Internal Server Error" on CSS**
- This was fixed by using `postcss.config.cjs`.
- Restart `npm run dev` if you see this.

**"ImportError: email-validator"**
- Run `pip install email-validator` in the backend venv.

## Features
- **Register/Login**: Secure JWT auth.
- **Lobby**: Create or join private rooms.
- **Poker Table**: Real-time websocket updates.
- **Betting**: Check, Call, Raise, Fold actions.
