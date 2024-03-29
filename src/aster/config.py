import logging
import secrets
from functools import cached_property, lru_cache
from pathlib import Path
from typing import Annotated

import sqlalchemy as sa
import structlog
from fastapi import Depends
from pydantic import (
    AnyHttpUrl,
    Field,
    FilePath,
    PostgresDsn,
    RedisDsn,
    SecretStr,
    ValidationError,
    computed_field,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from aster import ASTER_ENV_PREFIX

logger = structlog.get_logger()


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(".env"),
        env_file_encoding="utf-8",
        env_prefix=ASTER_ENV_PREFIX,
    )
    database_scheme: str = "postgresql+psycopg"
    database_hostname: str
    database_credential_user: SecretStr
    database_credential_password: SecretStr
    database_name: str = "aster"
    database_port: int = 5432
    database_engine_pool_size: int = 20
    database_engine_max_overflow: int = 0

    def get_sqlalchemy_url(self, with_name: bool = True) -> sa.URL:
        try:
            url = PostgresDsn(
                f"{self.database_scheme}://{self.database_credential_user.get_secret_value()}:{self.database_credential_password.get_secret_value()}@{self.database_hostname}:{str(self.database_port)}/{self.database_name}"
            )
        except ValidationError:
            logger.exception("Invalid sqlalchemy url")
        sqlalchemy_url = sa.make_url(str(url))
        if not with_name:
            sqlalchemy_url = sqlalchemy_url._replace(
                drivername="postgresql", database=None
            )
        return sqlalchemy_url

    @computed_field(repr=False)  # type: ignore[misc]
    @cached_property
    def sqlalchemy_database_url(self) -> PostgresDsn:
        try:
            url = PostgresDsn(
                f"{self.database_scheme}://{self.database_credential_user.get_secret_value()}:{self.database_credential_password.get_secret_value()}@{self.database_hostname}:{str(self.database_port)}/{self.database_name}"
            )
        except ValidationError:
            logger.aexception("Invalid config")
        return url

    @computed_field(repr=False)  # type: ignore[misc]
    @cached_property
    def psycopg_database_url(self) -> PostgresDsn:
        try:
            url = PostgresDsn(
                f"postgresql://{self.database_credential_user.get_secret_value()}:{self.database_credential_password.get_secret_value()}@{self.database_hostname}:{str(self.database_port)}"
            )
        except ValidationError:
            logger.aexception("Invalid config")
        return url

    alembic_ini_path: FilePath = "alembic.ini"  # type: ignore
    # alembic_revision_path: DirectoryPath = "alembic"  # type: ignore

    redis_url: RedisDsn | None = None

    logging_level: int = logging.INFO

    cors_origin: list[AnyHttpUrl] = Field(default_factory=list)

    secret_key: str = secrets.token_urlsafe(32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()


InjectSettings = Annotated[AppSettings, Depends(get_settings)]
