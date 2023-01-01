import secrets
from functools import lru_cache

from pydantic import BaseSettings


class AuthConfig(BaseSettings):
    secret_key: str = secrets.token_urlsafe(32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


@lru_cache()
def get_settings():
    return AuthConfig()
