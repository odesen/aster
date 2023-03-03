import os
from typing import Any, AsyncIterable, Callable, Coroutine

import pytest
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

os.environ["ASTER_DATABASE_NAME"] = "aster-test"

# ruff: noqa: E402

from aster.api import create_app
from aster.database import drop_database, engine, init_database, session_factory
from aster.posts.schemas import PostCreate


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
async def database(anyio_backend: str) -> Any:
    await init_database(engine)
    yield
    drop_database(str(engine.url), "aster-test")


@pytest.fixture(scope="session")
async def client(anyio_backend: str) -> AsyncIterable[AsyncClient]:
    async with AsyncClient(app=create_app(), base_url="http://testserver") as ac:
        yield ac


@pytest.fixture(scope="function", autouse=True)
async def session() -> AsyncIterable[AsyncSession]:
    async with (engine.connect() as conn, conn.begin() as transaction):
        session_factory.configure(bind=conn, join_transaction_mode="create_savepoint")
        yield session_factory()
        await transaction.rollback()


# Auth API


@pytest.fixture
async def api_login(
    client: AsyncClient,
) -> Callable[[dict[str, str], bool], Coroutine[Any, Any, Response]]:
    async def _r(data_in: dict[str, str], update_token: bool = True) -> Response:
        res = await client.post(f"{client.base_url}/login", data=data_in)
        if update_token:
            client.headers[
                "Authorization"
            ] = f"""Bearer {res.json().get("access_token", "")}"""
        return res

    return _r


@pytest.fixture
def api_register_user(
    client: AsyncClient,
) -> Callable[[dict[str, str]], Coroutine[Any, Any, Response]]:
    async def _r(data_in: dict[str, str]) -> Response:
        return await client.post(
            f"{client.base_url}/users/register",
            json=data_in,
        )

    return _r


@pytest.fixture
def api_list_users(client: AsyncClient) -> Callable[[], Coroutine[Any, Any, Response]]:
    async def _r() -> Response:
        return await client.get(f"{client.base_url}/users")

    return _r


@pytest.fixture
def api_get_user(client: AsyncClient) -> Callable[[str], Coroutine[Any, Any, Response]]:
    async def _r(username: str) -> Response:
        return await client.get(f"/users/{username}")

    return _r


@pytest.fixture
def api_get_authenticated_user(
    client: AsyncClient,
) -> Callable[[], Coroutine[Any, Any, Response]]:
    async def _r() -> Response:
        return await client.get(f"{client.base_url}/user")

    return _r


@pytest.fixture
def api_update_authenticated_user(
    client: AsyncClient,
) -> Callable[[], Coroutine[Any, Any, Response]]:
    async def _r() -> Response:
        return await client.patch(f"{client.base_url}/user")

    return _r


@pytest.fixture
def api_update_password_authenticated_user(
    client: AsyncClient,
) -> Callable[[], Coroutine[Any, Any, Response]]:
    async def _r() -> Response:
        return await client.put(f"{client.base_url}/user/password")

    return _r


@pytest.fixture
def api_list_users_blocked_by_authenticated_user(
    client: AsyncClient,
) -> Callable[[], Coroutine[Any, Any, Response]]:
    async def _r() -> Response:
        return await client.get(f"{client.base_url}/user/blocks")

    return _r


@pytest.fixture
def api_check_user_blocked_by_authenticated_user(
    client: AsyncClient,
) -> Callable[[str], Coroutine[Any, Any, Response]]:
    async def _r(username: str) -> Response:
        return await client.get(f"{client.base_url}/user/blocks/{username}")

    return _r


@pytest.fixture
def api_block_user(
    client: AsyncClient,
) -> Callable[[str], Coroutine[Any, Any, Response]]:
    async def _r(username: str) -> Response:
        return await client.put(f"{client.base_url}/user/blocks/{username}")

    return _r


@pytest.fixture
def api_unblock_user(
    client: AsyncClient,
) -> Callable[[str], Coroutine[Any, Any, Response]]:
    async def _r(username: str) -> Response:
        return await client.delete(f"{client.base_url}/user/blocks/{username}")

    return _r


# Post API


@pytest.fixture
def api_create_post(
    client: AsyncClient,
) -> Callable[[PostCreate], Coroutine[Any, Any, Response]]:
    async def _r(data_in: PostCreate) -> Response:
        return await client.post(f"{client.base_url}/posts", content=data_in.json())

    return _r


@pytest.fixture
def api_list_posts(
    client: AsyncClient,
) -> Callable[[str], Coroutine[Any, Any, Response]]:
    async def _r(username: str) -> Response:
        return await client.get(
            f"{client.base_url}/posts", params={"username": username}
        )

    return _r


@pytest.fixture
def api_get_post(client: AsyncClient) -> Callable[[int], Coroutine[Any, Any, Response]]:
    async def _r(post_id: int) -> Response:
        return await client.get(f"{client.base_url}/posts/{post_id}")

    return _r


@pytest.fixture
def api_delete_post(
    client: AsyncClient,
) -> Callable[[int], Coroutine[Any, Any, Response]]:
    async def _r(post_id: int) -> Response:
        return await client.delete(f"{client.base_url}/posts/{post_id}")

    return _r
