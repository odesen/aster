from datetime import datetime

from pydantic import BaseModel, Field, SecretStr

from aster.schemas import ORJSONModel


class UserBase(ORJSONModel):
    username: str = Field(max_length=64)


class UserCreate(UserBase):
    password: SecretStr = Field(max_length=256)


class UserView(UserBase, orm_mode=True):
    id: int
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
