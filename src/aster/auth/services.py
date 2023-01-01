from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aster.auth.utils import get_password_hash

from .models import User
from .schemas import UserCreate


async def create_user(session: AsyncSession, *, data_in: UserCreate) -> User:
    user = User(
        **data_in.dict(exclude={"password"}),
        password=get_password_hash(data_in.password.get_secret_value()),
    )
    session.add(user)
    await session.flush()
    return user


async def get_user_by_username(session: AsyncSession, *, username: str) -> User | None:
    result = await session.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()
