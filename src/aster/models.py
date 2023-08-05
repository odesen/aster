from datetime import datetime
from typing import Annotated

from sqlalchemy import DateTime, ForeignKey, Identity, Integer, MetaData, String, Text
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)

POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}
metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)


class BaseORMModel(MappedAsDataclass, DeclarativeBase):
    metadata = metadata
    """subclasses will be converted to dataclasses"""


intpk = Annotated[int, mapped_column(Integer, Identity(), primary_key=True)]
str64 = Annotated[str, mapped_column(String(64))]
text = Annotated[str, mapped_column(Text)]
userid = Annotated[int, mapped_column(ForeignKey("user_.id"))]


class Post(BaseORMModel, kw_only=True):
    __tablename__ = "post"

    # Columns
    id: Mapped[int] = mapped_column(Integer, Identity(), init=False, primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default_factory=datetime.now, insert_default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default_factory=datetime.now, onupdate=datetime.now
    )
    uid: Mapped[int] = mapped_column(ForeignKey("user_.id"), init=False)

    # Relationships
    user: Mapped["User"] = relationship()


class User(BaseORMModel):
    __tablename__ = "user_"

    # Columns
    id: Mapped[int] = mapped_column(Integer, Identity(), init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default_factory=datetime.now, insert_default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default_factory=datetime.now, onupdate=datetime.now
    )

    # Relationships
    users_blocked: Mapped[list["UserBlock"]] = relationship(
        "UserBlock",
        default_factory=list,
        foreign_keys="UserBlock.uid",
        back_populates="user",
    )
    users_blocked_by: Mapped[list["UserBlock"]] = relationship(
        "UserBlock",
        default_factory=list,
        foreign_keys="UserBlock.uid_blocked",
        back_populates="user_blocked",
    )


class UserBlock(BaseORMModel):
    __tablename__ = "user_block"

    # Columns
    id: Mapped[int] = mapped_column(Integer, Identity(), init=False, primary_key=True)
    uid: Mapped[int] = mapped_column(ForeignKey("user_.id"))
    uid_blocked: Mapped[int] = mapped_column(ForeignKey("user_.id"))

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys="UserBlock.uid",
        back_populates="users_blocked",
        init=False,
    )
    user_blocked: Mapped["User"] = relationship(
        "User",
        foreign_keys="UserBlock.uid_blocked",
        back_populates="users_blocked_by",
        init=False,
    )
