from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from aster.models import Base, intpk, str64, text, userid


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str64] = mapped_column(unique=True)
    password: Mapped[text] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default_factory=datetime.now, insert_default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default_factory=datetime.now, onupdate=datetime.now
    )


class UserBlock(Base):
    __tablename__ = "user_block"

    id: Mapped[intpk] = mapped_column(init=False)
    uid: Mapped[userid] = mapped_column()
    uid_blocked: Mapped[userid] = mapped_column()
