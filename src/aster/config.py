import logging
import secrets
from functools import cached_property, lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import Depends
from pydantic import (
    AnyHttpUrl,
    DirectoryPath,
    Field,
    FilePath,
    PostgresDsn,
    RedisDsn,
    SecretStr,
    ValidationError,
    computed_field,
)
from pydantic_settings import BaseSettings
from pydantic_settings.main import SettingsConfigDict

from aster import ASTER_ENV_PREFIX


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=Path(".env"),
        env_file_encoding="utf-8",
        env_nested_delimiter=None,
        env_prefix=ASTER_ENV_PREFIX,
        secrets_dir=None,
    )
    database_scheme: str = "postgresql+psycopg"
    database_hostname: str
    database_credential_user: SecretStr
    database_credential_password: SecretStr
    database_name: str = "aster"
    database_port: int = 5432
    database_engine_pool_size: int = 20
    database_engine_max_overflow: int = 0

    @computed_field(repr=False)  # type: ignore[misc]
    @cached_property
    def sqlalchemy_database_url(self) -> PostgresDsn:
        try:
            url = PostgresDsn(
                f"{self.database_scheme}://{self.database_credential_user.get_secret_value()}:{self.database_credential_password.get_secret_value()}@{self.database_hostname}:{str(self.database_port)}/{self.database_name}"
            )
        except ValidationError:
            ...
        return url

    @computed_field(repr=False)  # type: ignore[misc]
    @cached_property
    def psycopg_database_url(self) -> PostgresDsn:
        try:
            url = PostgresDsn(
                f"postgresql://{self.database_credential_user.get_secret_value()}:{self.database_credential_password.get_secret_value()}@{self.database_hostname}:{str(self.database_port)}"
            )
        except ValidationError:
            ...
        return url

    alembic_ini_path: FilePath = "alembic.ini"  # type: ignore
    alembic_revision_path: DirectoryPath = "alembic"  # type: ignore

    redis_url: RedisDsn | None = None

    logging_level: int = logging.INFO

    cors_origin: list[AnyHttpUrl] = Field(default_factory=list)

    secret_key: str = secrets.token_urlsafe(32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


@lru_cache()
def get_settings() -> AppSettings:
    return AppSettings(**{})


InjectSettings = Annotated[AppSettings, Depends(get_settings)]
