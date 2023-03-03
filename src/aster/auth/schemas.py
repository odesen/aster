from datetime import datetime, timezone

from aster.schemas import ORJSONModel
from pydantic import BaseModel, Field, SecretStr


def _normalize_datetime(value: datetime) -> datetime:
    """Converts the given value into UTC and strips microseconds"""
    if value.tzinfo is not None:
        value.astimezone(timezone.utc)
    return value.replace(microsecond=0)


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
    exp: datetime
    """Expiration - Time after which the JWT expires"""
    iat: datetime = Field(
        default_factory=lambda: _normalize_datetime(datetime.now(timezone.utc))
    )
    """Issued at - Time at which the JWT was issued; can be used to determine age of the JWT"""
    sub: str = Field(min_length=1)
    """Subject of the JWT (the user)"""
    iss: str | None = None
    """Issuer - Issuer of the JWT"""
    aud: str | None = None
    """Audience - Recipient for which the JWT is intended"""
    nbf: datetime | None = None
    """Not before - Time before which the JWT must not be accepted for processing"""
