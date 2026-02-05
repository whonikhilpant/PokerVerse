from fastapi import FastAPI
from deck import Deck

app = FastAPI()
deck = Deck()

@app.get("/")
def home():
    return {"message": "PokerVerse backend running"}

@app.get("/deal")
def deal():
    cards = deck.deal(5)
    return [card.to_dict() for card in cards]