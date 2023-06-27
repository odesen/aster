import logging
import secrets
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends
from pydantic import (
    AnyHttpUrl,
    DirectoryPath,
    Field,
    FieldValidationInfo,
    FilePath,
    PostgresDsn,
    RedisDsn,
    SecretStr,
    field_validator,
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
    database_url: PostgresDsn = None  # type: ignore
    database_engine_pool_size: int = 20
    database_engine_max_overflow: int = 0

    @field_validator("database_url", mode="before")
    def assemble_db_connection(cls, v: str | None, info: FieldValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        user: SecretStr | None = info.data.get("database_credential_user")
        pw: SecretStr | None = info.data.get("database_credential_password")
        return PostgresDsn(
            f"{info.data.get('database_scheme') or ''}://{user.get_secret_value() if user else None}:{pw.get_secret_value() if pw else None}@{info.data.get('database_hostname') or ''}:{str(info.data.get('database_port'))}/{info.data.get('database_name', '')}"
        )

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
