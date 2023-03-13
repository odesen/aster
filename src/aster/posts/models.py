from datetime import datetime
from typing import TYPE_CHECKING

from aster.models import BaseModel, intpk, text, userid
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from aster.auth.models import User


class Post(BaseModel):
    __tablename__ = "post"

    id: Mapped[intpk]
    content: Mapped[text]
    created_at: Mapped[datetime] = mapped_column(DateTime, insert_default=datetime.now)
    uid: Mapped[userid]
    user: Mapped["User"] = relationship()
