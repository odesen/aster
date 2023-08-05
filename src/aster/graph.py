from __future__ import annotations

from datetime import datetime
from typing import Annotated, Self, Union

import strawberry

from aster.auth.services import get_user_by_username
from aster.auth.utils import verify_password
from aster.database import session_factory
from aster.models import Post, User
from aster.posts.services import get_post_by_id


@strawberry.type
class LoginSuccess:
    user: UserSchema


@strawberry.type
class LoginError:
    message: str


LoginResult = Annotated[
    Union[LoginSuccess, LoginError], strawberry.union("LoginResult")
]


@strawberry.type
class PostSchema:
    id: strawberry.ID
    content: str
    created_at: datetime
    user: UserSchema

    @classmethod
    def marshal(cls, model: Post) -> Self:
        return cls(
            id=strawberry.ID(str(model.id)),
            content=model.content,
            created_at=model.created_at,
            user=UserSchema.marshal(model.user),
        )


@strawberry.type
class UserSchema:
    id: strawberry.ID
    username: str

    @classmethod
    def marshal(cls, model: User) -> Self:
        return cls(id=strawberry.ID(str(model.id)), username=model.username)


@strawberry.type
class Query:
    @strawberry.field
    async def post(self, id: strawberry.ID) -> PostSchema:
        async with session_factory.begin() as session:
            post = await get_post_by_id(session, post_id=int(id))
            if not post:
                raise Exception
            return PostSchema.marshal(post)


@strawberry.type
class Mutation:
    @strawberry.field
    async def login(self, username: str, password: str) -> LoginResult:
        async with session_factory.begin() as session:
            user = await get_user_by_username(session, username=username)
            if not user:
                return LoginError(message="Something went wrong")
            if not verify_password(password, user.password):
                return LoginError(message="Something went wrong")
            return LoginSuccess(user=UserSchema.marshal(user))


schema = strawberry.Schema(Query, mutation=Mutation)
