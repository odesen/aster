import secrets
from functools import lru_cache

from pydantic import BaseSettings

from aster import ASTER_ENV_PREFIX


class AuthConfig(
    BaseSettings,
    env_file=".env",
    env_file_encoding="utf-8",
    env_prefix=ASTER_ENV_PREFIX,
):
    secret_key: str = secrets.token_urlsafe(32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


@lru_cache()
def get_settings() -> AuthConfig:
    return AuthConfig()
