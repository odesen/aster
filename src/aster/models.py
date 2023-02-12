from typing import Annotated

from sqlalchemy import ForeignKey, MetaData, String, Text
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, mapped_column

POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}
metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)


class BaseModel(MappedAsDataclass, DeclarativeBase):
    metadata = metadata
    """subclasses will be converted to dataclasses"""


intpk = Annotated[int, mapped_column(init=False, primary_key=True)]
str64 = Annotated[str, mapped_column(String(64))]
text = Annotated[str, mapped_column(Text)]
userid = Annotated[int, mapped_column(ForeignKey("user.id"))]
