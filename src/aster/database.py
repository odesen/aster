import time
from typing import Annotated, Any, AsyncIterable

import alembic.command
import alembic.config
import psycopg
from fastapi import Depends
from psycopg import sql
from sqlalchemy import Engine, event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from structlog.contextvars import bind_contextvars, get_contextvars

from aster.config import get_settings

engine = create_async_engine(str(get_settings().sqlalchemy_database_url))
session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterable[AsyncSession]:
    async with session_factory.begin() as session:
        yield session


InjectSession = Annotated[AsyncSession, Depends(get_session)]


@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(
    conn: Any,
    cursor: Any,
    statement: Any,
    parameters: Any,
    context: Any,
    executemany: Any,
) -> None:
    conn.info["query_start_time"] = time.time()


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(
    conn: Any,
    cursor: Any,
    statement: Any,
    parameters: Any,
    context: Any,
    executemany: Any,
) -> None:
    end_time = time.time()
    bind_contextvars(
        sql_queries_count=get_contextvars().get("sql_queries_count", 0) + 1,
        sql_queries_time_spent=get_contextvars().get("sql_queries_time_spent", 0.0)
        + end_time
        - conn.info.pop("query_start_time", end_time),
    )


def create_database() -> None:
    with (
        psycopg.connect(
            get_settings().get_sqlalchemy_url(False).render_as_string(False),
            autocommit=True,
        ) as conn,
        conn.cursor() as cur,
    ):
        cur.execute(
            sql.SQL("CREATE DATABASE {0};").format(
                sql.Identifier(get_settings().database_name)
            )
        )


def check_database_exists() -> bool:
    with psycopg.connect(
        get_settings().get_sqlalchemy_url(False).render_as_string(False)
    ) as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s;",
            (get_settings().database_name,),
        )
        res = cur.fetchone()
    return True if res is not None else False


def init_database() -> None:
    if not check_database_exists():
        create_database()
    upgrade_database()


def upgrade_database(revision: str = "head", sql: bool = False) -> None:
    alembic_cfg = alembic.config.Config(
        str(get_settings().alembic_ini_path),
    )
    alembic.command.upgrade(alembic_cfg, revision, sql=sql)


def downgrade_database(revision: str = "head") -> None:
    alembic_cfg = alembic.config.Config(
        str(get_settings().alembic_ini_path),
    )
    alembic.command.downgrade(alembic_cfg, revision)


def drop_database() -> None:
    with psycopg.connect(
        get_settings().get_sqlalchemy_url(False).render_as_string(False),
        autocommit=True,
    ) as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = %s AND pid <> pg_backend_pid();
            """,
            (get_settings().database_name,),
        )
        cur.execute(
            sql.SQL("DROP DATABASE IF EXISTS {0};").format(
                sql.Identifier(get_settings().database_name)
            )
        )
