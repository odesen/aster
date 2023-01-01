from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from aster.models import Base, intpk, text, userid

if TYPE_CHECKING:
    from aster.auth.models import User


class Post(Base):
    __tablename__ = "post"

    id: Mapped[intpk] = mapped_column(init=False)
    content: Mapped[text] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime, insert_default=datetime.now)
    uid: Mapped[userid] = mapped_column()
    user: Mapped["User"] = relationship()
