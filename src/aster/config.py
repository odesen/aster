from functools import lru_cache
from typing import Any

from pydantic import BaseSettings, PostgresDsn, SecretStr, validator

from aster import ASTER_ENV_PREFIX


class AppSettings(
    BaseSettings,
    env_file=".env",
    env_file_encoding="utf-8",
    env_prefix=ASTER_ENV_PREFIX,
):
    database_scheme: str = "postgresql+psycopg"
    database_hostname: str
    database_credential_user: SecretStr
    database_credential_password: SecretStr
    database_name: str = "aster"
    database_port: int = 5432
    database_engine_pool_size: int = 20
    database_engine_max_overflow: int = 0
    database_url: PostgresDsn = None  # type: ignore

    @validator("database_url", pre=True)
    def assemble_db_connection(cls, v: str | None, values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        user: SecretStr | None = values.get("database_credential_user")
        pw: SecretStr | None = values.get("database_credential_password")
        return PostgresDsn.build(
            scheme=values.get("database_scheme") or "",
            user=user.get_secret_value() if user else None,
            password=pw.get_secret_value() if pw else None,
            host=values.get("database_hostname") or "",
            port=str(values.get("database_port")),
            path=f"""/{values.get("database_name", "")}""",
        )


@lru_cache()
def get_settings() -> AppSettings:
    return AppSettings()
