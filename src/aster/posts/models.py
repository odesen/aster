from datetime import datetime
from typing import TYPE_CHECKING

from aster.models import BaseModel
from sqlalchemy import DateTime, ForeignKey, Identity, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from aster.auth.models import User


class Post(BaseModel, kw_only=True):
    __tablename__ = "post"

    # Columns
    id: Mapped[int] = mapped_column(Integer, Identity(), init=False, primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default_factory=datetime.now, insert_default=datetime.now
    )
    uid: Mapped[int] = mapped_column(ForeignKey("user_.id"), init=False)

    # Relationships
    user: Mapped["User"] = relationship()
