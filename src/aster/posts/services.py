from typing import Sequence

from aster.models import Post, User
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload

from .schemas import PostCreate


async def create_post(
    session: AsyncSession, *, data_in: PostCreate, user: User
) -> Post:
    post = Post(**data_in.model_dump(), user=user)
    session.add(post)
    await session.flush()
    return post


async def get_post_by_id(session: AsyncSession, *, post_id: int) -> Post | None:
    res = await session.execute(
        select(Post).options(joinedload(Post.user)).where(Post.id == post_id)
    )
    return res.scalar_one_or_none()


async def list_posts(
    session: AsyncSession, *, username: str, limit: int = 10, offset: int = 0
) -> Sequence[Post]:
    res = await session.execute(
        select(Post)
        .join(Post.user)
        .options(contains_eager(Post.user))
        .where(User.username == username)
        .limit(limit)
        .offset(offset)
        .order_by(desc(Post.created_at))
    )
    return res.scalars().all()


async def delete_post(session: AsyncSession, *, post: Post) -> None:
    await session.delete(post)
    await session.flush()
