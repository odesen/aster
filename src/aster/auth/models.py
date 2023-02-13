from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from aster.models import BaseModel, intpk, str64, text, userid


class User(BaseModel):
    __tablename__ = "user"

    id: Mapped[intpk] = mapped_column()
    username: Mapped[str64] = mapped_column(unique=True)
    password: Mapped[text] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default_factory=datetime.now, insert_default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default_factory=datetime.now, onupdate=datetime.now
    )


class UserBlock(BaseModel):
    __tablename__ = "user_block"

    id: Mapped[intpk] = mapped_column()
    uid: Mapped[userid] = mapped_column()
    uid_blocked: Mapped[userid] = mapped_column()
