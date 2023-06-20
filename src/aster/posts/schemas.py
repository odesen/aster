from datetime import datetime

from aster.auth.schemas import UserView
from aster.schemas import ORJSONModel
from pydantic import Field, RootModel


class PostBase(ORJSONModel):
    content: str = Field(max_length=256)


class PostCreate(PostBase):
    ...


class PostView(PostBase, from_attributes=True):
    id: int
    created_at: datetime
    user: UserView


ListPostView = RootModel[list[PostView]]
