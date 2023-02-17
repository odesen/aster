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


class ListUserView(ORJSONModel):
    __root__: list[UserView]

    class Config:
        orm_mode = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class JWTToken(BaseModel):
    iss: str | None = None
    """Issuer of the JWT"""
    sub: str | None = None
    """Subject of the JWT (the user)"""
    aud: str | None = None
    """Recipient for which the JWT is intended"""
    exp: datetime | None = None
    """Time ater which the JWT expires"""
    nbf: datetime | None = None
    """Time before which the JWT must not be accepted for processing"""
    iat: datetime | None = None
    """Time at which the JWT was issued; can be used to determine age of the JWT"""
