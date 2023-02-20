from typing import Sequence

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from aster.auth.utils import get_password_hash

from .models import User, UserBlock
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


async def list_users(session: AsyncSession) -> Sequence[User]:
    result = await session.execute(select(User))
    return result.scalars().all()


async def list_users_blocked_by_user(
    session: AsyncSession, *, username: str
) -> Sequence[User]:
    UserBlocked = aliased(User)
    result = await session.execute(
        select(UserBlocked).where(
            UserBlocked.id.in_(
                select(UserBlock.uid_blocked)
                .join(UserBlock.user)
                .where(User.username == username)
            )
        )
    )
    return result.scalars().all()


async def check_if_user_blocked_by_user(
    session: AsyncSession, *, username: str, username_block: str
) -> bool:
    UserBlocked = aliased(User)
    stmt = select(1).where(
        exists(
            select(User.username, UserBlocked.username)
            .join(User, UserBlock.user)
            .join(UserBlocked, UserBlock.user_blocked)
            .where(User.username == username, UserBlocked.username == username_block)
        )
    )
    res = await session.execute(stmt)
    return True if res.first() is not None else False


async def block_user(
    session: AsyncSession, *, user: User, username_to_block: str
) -> None:
    user_to_block = await get_user_by_username(session, username=username_to_block)
    if not user_to_block:
        raise Exception
    result = await session.execute(
        select(UserBlock).where(
            UserBlock.uid == user.id, UserBlock.uid_blocked == user_to_block.id
        )
    )
    True if result.first() else False  # TODO: 304 or new block
    session.add(UserBlock(uid=user.id, uid_blocked=user_to_block.id))
    await session.flush()


async def unblock_user(
    session: AsyncSession, *, user: User, username_to_unblock: str
) -> None:
    user_to_block = await get_user_by_username(session, username=username_to_unblock)
    if not user_to_block:
        raise Exception
    result = await session.execute(
        select(UserBlock).where(
            UserBlock.uid == user.id, UserBlock.uid_blocked == user_to_block.id
        )
    )
    user_block = result.scalar_one_or_none()
    if not user_block:
        raise Exception
    await session.delete(user_block)
