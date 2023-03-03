from aster.database import get_session
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Post
from .services import get_post_by_id


async def get_valid_post_by_id(
    post_id: int, session: AsyncSession = Depends(get_session)
) -> Post:
    post = await get_post_by_id(session, post_id=post_id)
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return post
