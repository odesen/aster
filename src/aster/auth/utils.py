from datetime import datetime, timedelta
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from .config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(
        to_encode, get_settings().secret_key, get_settings().algorithm
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    is_verified: bool = pwd_context.verify(plain_password, hashed_password)
    return is_verified


def get_password_hash(password: str) -> str:
    hash: str = pwd_context.hash(password)
    return hash
