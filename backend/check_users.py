import sys
import os

# Add current dir to path to find imports
sys.path.append(os.getcwd())

from database import SessionLocal
from models import User
from auth import verify_password, get_password_hash

def check_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"Total Users: {len(users)}")
        for u in users:
            print(f"User: {u.username}, Chips: {u.chips}, Hash: {u.hashed_password[:10]}...")
            
        # Test a specific login if needed
        # print(verify_password("password", users[0].hashed_password))
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
