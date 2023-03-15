from datetime import datetime
from typing import TYPE_CHECKING

from aster.models import BaseModel
from sqlalchemy import DateTime, ForeignKey, Identity, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from aster.auth.models import User


class Post(BaseModel):
    __tablename__ = "post"

    # Columns
    id: Mapped[int] = mapped_column(Integer, Identity(), init=False, primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, insert_default=datetime.now)
    uid: Mapped[int] = mapped_column(ForeignKey("user_.id"))

    # Relationships
    user: Mapped["User"] = relationship()
