from typing import Annotated

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, mapped_column

from aster.database import metadata


class Base(MappedAsDataclass, DeclarativeBase):
    metadata = metadata
    """subclasses will be converted to dataclasses"""


intpk = Annotated[int, mapped_column(init=False, primary_key=True)]
str64 = Annotated[str, mapped_column(String(64))]
text = Annotated[str, mapped_column(Text)]
userid = Annotated[int, mapped_column(ForeignKey("user.id"))]
