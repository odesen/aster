import os
from typing import Any, Callable, Iterable

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from aster.api import create_app
from aster.auth.schemas import UserCreate
from aster.database import drop_database, engine, init_database
from aster.posts.schemas import PostCreate

pytestmark = pytest.mark.anyio

os.environ["ASTER_DATABASE_NAME"] = "aster-test"


@pytest.fixture(scope="session")
async def database() -> Any:
    await init_database(engine)
    yield
    drop_database(str(engine.url), "aster-test")


@pytest.fixture(scope="session")
def client() -> Iterable[TestClient]:
    yield TestClient(create_app())


# Auth API


@pytest.fixture
def api_login(client: TestClient) -> Callable[[Any], Response]:
    def _r(data_in: Any) -> Response:
        return client.post(f"{client.base_url}/login", data=data_in)

    return _r


@pytest.fixture
def api_register_user(client: TestClient) -> Callable[[UserCreate], Response]:
    def _r(data_in: UserCreate) -> Response:
        return client.post(f"{client.base_url}/users", content=data_in.json())

    return _r


@pytest.fixture
def api_list_users(client: TestClient) -> Callable[[], Response]:
    def _r() -> Response:
        return client.get(f"{client.base_url}/users")

    return _r


@pytest.fixture
def api_get_user(client: TestClient) -> Callable[[str], Response]:
    def _r(username: str) -> Response:
        return client.get(f"/users/{username}")

    return _r


@pytest.fixture
def api_get_authenticated(client: TestClient) -> Callable[[], Response]:
    def _r() -> Response:
        return client.get(f"{client.base_url}/user")

    return _r


@pytest.fixture
def api_update_authenticated_user(client: TestClient) -> Callable[[], Response]:
    def _r() -> Response:
        return client.patch(f"{client.base_url}/user")

    return _r


@pytest.fixture
def api_update_password_authenticated_user(
    client: TestClient,
) -> Callable[[], Response]:
    def _r() -> Response:
        return client.put(f"{client.base_url}/user/password")

    return _r


@pytest.fixture
def api_list_users_blocked_by_authenticated_user(
    client: TestClient,
) -> Callable[[], Response]:
    def _r() -> Response:
        return client.get(f"{client.base_url}/user/blocks")

    return _r


@pytest.fixture
def api_check_user_blocked_by_authenticated_user(
    client: TestClient,
) -> Callable[[str], Response]:
    def _r(username: str) -> Response:
        return client.get(f"{client.base_url}/user/blocks/{username}")

    return _r


@pytest.fixture
def api_block_user(client: TestClient) -> Callable[[str], Response]:
    def _r(username: str) -> Response:
        return client.put(f"{client.base_url}/user/blocks/{username}")

    return _r


@pytest.fixture
def api_unblock_user(client: TestClient) -> Callable[[str], Response]:
    def _r(username: str) -> Response:
        return client.delete(f"{client.base_url}/user/blocks/{username}")

    return _r


# Post API


@pytest.fixture
def api_create_post(client: TestClient) -> Callable[[PostCreate], Response]:
    def _r(data_in: PostCreate) -> Response:
        return client.post(f"{client.base_url}/posts", content=data_in.json())

    return _r


@pytest.fixture
def api_list_posts(client: TestClient) -> Callable[[str], Response]:
    def _r(username: str) -> Response:
        return client.get(f"{client.base_url}/posts", params={"username": username})

    return _r


@pytest.fixture
def api_get_post(client: TestClient) -> Callable[[int], Response]:
    def _r(post_id: int) -> Response:
        return client.get(f"{client.base_url}/posts/{post_id}")

    return _r


@pytest.fixture
def api_delete_post(client: TestClient) -> Callable[[int], Response]:
    def _r(post_id: int) -> Response:
        return client.delete(f"{client.base_url}/posts/{post_id}")

    return _r
