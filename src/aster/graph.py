from __future__ import annotations

from datetime import datetime
from typing import Self, Type

import strawberry

from aster.auth import models as auth_models
from aster.auth.services import get_user_by_username
from aster.auth.utils import verify_password
from aster.database import session_factory
from aster.posts import models as post_models
from aster.posts.services import get_post_by_id


@strawberry.type
class LoginSuccess:
    user: User


@strawberry.type
class LoginError:
    message: str


LoginResult: Type[LoginSuccess | LoginError] = strawberry.union(
    "LoginResult", (LoginSuccess, LoginError)
)


@strawberry.type
class Post:
    id: strawberry.ID
    content: str
    created_at: datetime
    user: User

    @classmethod
    def marshal(cls, model: post_models.Post) -> Self:
        return cls(
            id=strawberry.ID(str(model.id)),
            content=model.content,
            created_at=model.created_at,
            user=User.marshal(model.user),
        )


@strawberry.type
class User:
    id: strawberry.ID
    username: str

    @classmethod
    def marshal(cls, model: auth_models.User) -> Self:
        return cls(id=strawberry.ID(str(model.id)), username=model.username)


@strawberry.type
class Query:
    @strawberry.field
    async def post(self, id: strawberry.ID) -> Post:
        async with session_factory.begin() as session:
            post = await get_post_by_id(session, post_id=int(id))
            if not post:
                raise Exception
            return Post.marshal(post)


@strawberry.type
class Mutation:
    @strawberry.field
    async def login(self, username: str, password: str) -> LoginResult:
        async with session_factory.begin() as session:
            user = await get_user_by_username(session, username=username)
            if not user:
                return LoginError(message="")
            if not verify_password(password, user.password):
                return LoginError(message="")
            return LoginSuccess(user=User.marshal(user))


schema = strawberry.Schema(Query, mutation=Mutation)
