from datetime import datetime

from aster.auth.schemas import UserView
from aster.schemas import ORJSONModel
from pydantic import Field


class PostBase(ORJSONModel):
    content: str = Field(max_length=256)


class PostCreate(PostBase):
    ...


class PostView(PostBase):
    id: int
    created_at: datetime
    user: UserView

    class Config:
        orm_mode = True


class ListPostView(ORJSONModel):
    __root__: list[PostView]

    class Config:
        orm_mode = True
