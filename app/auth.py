import itsdangerous
from fastapi import Request, Response
from passlib.context import CryptContext
from sqlmodel import Session, select

from .core.config import settings
from .db import engine
from .models import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
serializer = itsdangerous.URLSafeSerializer(settings.secret_key, salt="session")


def hash_password(raw: str) -> str:
    return pwd_context.hash(raw)


def verify_password(raw: str, hashed: str) -> bool:
    return pwd_context.verify(raw, hashed)


def create_session_cookie(response: Response, user_id: int):
    token = serializer.dumps({"user_id": user_id})
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax"
    )


def clear_session_cookie(response: Response):
    response.delete_cookie("session")


def get_current_user(request: Request):
    token = request.cookies.get("session")
    if not token:
        return None
    try:
        data = serializer.loads(token)
        user_id = data["user_id"]
    except Exception:
        return None

    with Session(engine) as session:
        return session.get(User, user_id)
