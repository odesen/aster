import time
from typing import Annotated, Any, AsyncIterable

import psycopg
from fastapi import Depends
from psycopg import sql
from sqlalchemy import Engine, event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from structlog.contextvars import bind_contextvars, get_contextvars

from aster.config import get_settings
from aster.models import BaseModel

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


def create_database(url: str, database: str) -> None:
    with (
        psycopg.connect(url, autocommit=True) as conn,
        conn.cursor() as cur,
    ):
        cur.execute(sql.SQL("CREATE DATABASE {0};").format(sql.Identifier(database)))


def check_database_exists(url: str, database: str) -> bool:
    with psycopg.connect(url) as conn, conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (database,))
        res = cur.fetchone()
    return True if res is not None else False


async def init_database(engine: AsyncEngine) -> None:
    config = get_settings()
    if not check_database_exists(
        str(config.psycopg_database_url), config.database_name
    ):
        create_database(str(config.psycopg_database_url), config.database_name)
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


def init_schema() -> None:
    ...


def drop_database(url: str | None, database: str) -> None:
    if url is None:
        url = str(get_settings().psycopg_database_url)
    with psycopg.connect(url, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = %s AND pid <> pg_backend_pid();
            """,
            (database,),
        )
        cur.execute(
            sql.SQL("DROP DATABASE IF EXISTS {0};").format(sql.Identifier(database))
        )
