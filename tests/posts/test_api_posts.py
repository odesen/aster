from typing import Any, Callable, Coroutine

import dirty_equals as de
import pytest
from aster.auth.schemas import UserCreate
from aster.posts.schemas import PostCreate
from httpx import Response


@pytest.mark.asyncio
async def test_post(
    api_register_user: Callable[[dict[str, str]], Coroutine[Any, Any, Response]],
    api_login: Callable[[dict[str, str]], Coroutine[Any, Any, Response]],
    api_create_post: Callable[[PostCreate], Coroutine[Any, Any, Response]],
    api_get_post: Callable[[int], Coroutine[Any, Any, Response]],
    api_list_posts: Callable[[str], Coroutine[Any, Any, Response]],
    api_delete_post: Callable[[int], Coroutine[Any, Any, Response]],
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

    def post_equal(post_content: str) -> de.IsDict:
        return de.IsDict(
            id=de.IsPositiveInt(),
            content=post_content,
            created_at=de.IsDatetime(iso_string=True),
            user=de.IsDict(
                id=de.IsPositiveInt(),
                username=new_user.username,
                created_at=de.IsDatetime(iso_string=True),
                updated_at=de.IsDatetime(iso_string=True),
            ),
        )

    post1 = PostCreate(content="Post 1")
    res = await api_create_post(post1)
    assert res.status_code == 201

    res = await api_list_posts(new_user.username)
    assert res.status_code == 200
    post1_equal = post_equal(post1.content)
    assert res.json() == de.IsList(post1_equal)

    res = await api_get_post(res.json()[0]["id"])
    assert res.status_code == 200
    assert res.json() == post1_equal

    post2 = PostCreate(content="Post 2")
    res = await api_create_post(post2)
    assert res.status_code == 201

    res = await api_list_posts(new_user.username)
    assert res.status_code == 200
    assert res.json() == de.IsList(
        post_equal(post2.content), post1_equal
    )  # order by created_at desc

    res = await api_delete_post(res.json()[0]["id"])
    assert res.status_code == 204
