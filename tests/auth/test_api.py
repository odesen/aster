from typing import Any, Callable, Coroutine

import dirty_equals as de
import pytest
from httpx import Response

from aster.auth.schemas import UserCreate


@pytest.mark.anyio
async def test_register(
    api_register_user: Callable[[UserCreate], Coroutine[Any, Any, Response]],
    api_login: Callable[[dict[str, str]], Coroutine[Any, Any, Response]],
    api_get_authenticated_user: Callable[[], Coroutine[Any, Any, Response]],
) -> None:
    new_user = UserCreate(username="test", password="password")
    res = await api_register_user(new_user)
    assert res.status_code == 201

    res = await api_login(new_user.dict())
    assert res.status_code == 200

    res = await api_get_authenticated_user()
    assert res.status_code == 200
    assert res.json() == de.IsDict(
        id=de.IsPositiveInt(),
        username=new_user.username,
        created_at=de.IsDatetime(iso_string=True),
        updated_at=de.IsDatetime(iso_string=True),
    )
