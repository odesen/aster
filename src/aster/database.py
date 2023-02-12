from typing import AsyncIterable

import psycopg
from psycopg import sql
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from aster.config import get_settings
from aster.models import BaseModel

engine = create_async_engine(get_settings().database_url, echo=True)
session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterable[AsyncSession]:
    async with session_factory.begin() as session:
        yield session


# @event.listens_for(Engine, "before_cursor_execute")
# def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
#     conn.info.set_default("query_start_time", []).append(time.time())
#     logger.debug("Start query: %s", statement)

# @event.listens_for(Engine, "after_cursor_execute")
# def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
#     total = time.time() - conn.info["query_start_time"].pop(-1)
#     logger.debug("Query complete!")
#     logger.debug("Total time: %f", total)


def create_database(url: str, database: str) -> None:
    with (
        psycopg.connect(url, autocommit=True) as conn,
        conn.cursor() as cur,
    ):
        cur.execute(sql.SQL("CREATE DATABASE {0};").format(sql.Identifier(database)))


def check_database_exists(url: str, database: str) -> bool:
    with (psycopg.connect(url) as conn, conn.cursor() as cur):
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (database,))
        res = cur.fetchone()
    return True if res is not None else False


async def init_database(engine: AsyncEngine) -> None:
    config = get_settings()
    url_psycopg = f"postgresql://{config.database_credential_user.get_secret_value()}:{config.database_credential_password.get_secret_value()}@{config.database_hostname}:{config.database_port}"
    if not check_database_exists(url_psycopg, config.database_name):
        create_database(url_psycopg, config.database_name)
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


def init_schema() -> None:
    ...


def drop_database(url: str, database: str) -> None:
    with (psycopg.connect(url, autocommit=True) as conn, conn.cursor() as cur):
        cur.execute(
            sql.SQL("DROP DATABASE IF EXISTS {0};").format(sql.Identifier(database))
        )
