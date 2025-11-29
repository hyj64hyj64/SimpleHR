# create_initial_user.py

from app.database import SessionLocal
from app.models import User
from app.utils import get_password_hash  # adjust path if needed

def create_user():
    db = SessionLocal()

    # CHANGE THESE:
    username = "admin"
    password = "Admin123"
    email = "admin@example.com"

    # Check if user exists
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        print("User already exists.")
        return

    user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    print("User created:", user.username)

if __name__ == "__main__":
    create_user()
