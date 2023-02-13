from datetime import datetime

from pydantic import BaseModel, Field, SecretStr

from aster.schemas import ORJSONModel


class UserBase(ORJSONModel):
    username: str = Field(max_length=64)


class UserCreate(UserBase):
    password: SecretStr = Field(max_length=256)


class UserView(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ListUserView(UserBase):
    __root__: list[UserView]

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
