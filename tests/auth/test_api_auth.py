from typing import Any, Callable, Coroutine

import dirty_equals as de
import pytest
from aster.auth.schemas import UserCreate
from aster.auth.services import create_user
from httpx import Response
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_register(
    api_register_user: Callable[[dict[str, str]], Coroutine[Any, Any, Response]],
    api_login: Callable[[dict[str, str]], Coroutine[Any, Any, Response]],
    api_get_authenticated_user: Callable[[], Coroutine[Any, Any, Response]],
) -> None:
    new_user = UserCreate(username="test", password="password")
    res = await api_register_user(
        {
            "username": new_user.username,
            "password": new_user.password.get_secret_value(),
        }
    )
    assert res.status_code == 201

    res = await api_login(
        {
            "username": new_user.username,
            "password": new_user.password.get_secret_value(),
        }
    )
    assert res.status_code == 200

    res = await api_get_authenticated_user()
    assert res.status_code == 200
    assert res.json() == de.IsDict(
        id=de.IsPositiveInt(),
        username=new_user.username,
        created_at=de.IsDatetime(iso_string=True),
        updated_at=de.IsDatetime(iso_string=True),
    )


@pytest.mark.asyncio
async def test_block_unblock_user(
    session: AsyncSession,
    api_login: Callable[[dict[str, str]], Coroutine[Any, Any, Response]],
    api_block_user: Callable[[str], Coroutine[Any, Any, Response]],
    api_unblock_user: Callable[[str], Coroutine[Any, Any, Response]],
    api_check_user_blocked_by_authenticated_user: Callable[
        [str], Coroutine[Any, Any, Response]
    ],
    api_list_users_blocked_by_authenticated_user: Callable[
        [], Coroutine[Any, Any, Response]
    ],
) -> None:
    user1 = UserCreate(username="user1", password="password")
    user2 = UserCreate(username="user2", password="password")
    user3 = UserCreate(username="user3", password="password")
    await create_user(session, data_in=user1)
    await create_user(session, data_in=user2)
    await create_user(session, data_in=user3)
    await session.commit()
    await api_login(
        {"username": user1.username, "password": user1.password.get_secret_value()}
    )
    res = await api_block_user(user2.username)
    assert res.status_code == 204
    res = await api_block_user(user3.username)
    assert res.status_code == 204
    res = await api_check_user_blocked_by_authenticated_user(user2.username)
    assert res.status_code == 204
    res = await api_check_user_blocked_by_authenticated_user("unknown_user")
    assert res.status_code == 404
    res = await api_list_users_blocked_by_authenticated_user()
    assert res.json() == de.IsList(
        de.IsDict(
            id=de.IsPositiveInt(),
            username=user2.username,
            created_at=de.IsDatetime(iso_string=True),
            updated_at=de.IsDatetime(iso_string=True),
        ),
        de.IsDict(
            id=de.IsPositiveInt(),
            username=user3.username,
            created_at=de.IsDatetime(iso_string=True),
            updated_at=de.IsDatetime(iso_string=True),
        ),
        check_order=False,
    )
    res = await api_unblock_user(user2.username)
    assert res.status_code == 204
    res = await api_check_user_blocked_by_authenticated_user(user2.username)
    assert res.status_code == 404
