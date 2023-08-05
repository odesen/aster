from typing import Annotated

from aster.database import InjectSession
from aster.models import Post
from fastapi import Depends, HTTPException, status

from .services import get_post_by_id


async def get_valid_post_by_id(post_id: int, session: InjectSession) -> Post:
    post = await get_post_by_id(session, post_id=post_id)
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return post


InjectValidPost = Annotated[Post, Depends(get_valid_post_by_id)]
