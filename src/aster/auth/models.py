from datetime import datetime

from aster.models import BaseModel, intpk, str64, text, userid
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(BaseModel):
    __tablename__ = "user_"

    # Columns
    id: Mapped[intpk] = mapped_column(init=False)
    username: Mapped[str64] = mapped_column(unique=True)
    password: Mapped[text] = mapped_column()
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


class UserBlock(BaseModel):
    __tablename__ = "user_block"

    # Columns
    id: Mapped[intpk] = mapped_column(init=False)
    uid: Mapped[userid] = mapped_column()
    uid_blocked: Mapped[userid] = mapped_column()

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
