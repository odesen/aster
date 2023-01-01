from datetime import datetime

from pydantic import Field

from aster.auth.schemas import UserView
from aster.schemas import ORJSONModel


class PostBase(ORJSONModel):
    content: str = Field(max_length=256)


class PostCreate(PostBase):
    ...


class PostView(PostBase):
    created_at: datetime
    user: UserView

    class Config:
        orm_mode = True


class ListPostView(ORJSONModel):
    posts: list[PostView]

    class Config:
        orm_mode = True
