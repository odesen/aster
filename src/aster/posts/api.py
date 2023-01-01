from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from aster.database import get_session
from aster.posts.dependencies import get_valid_post_by_id
from aster.responses import ORJSONModelJSONResponse

from . import models, schemas, services

posts_router = APIRouter(prefix="/posts")


@posts_router.post("/", response_model=schemas.PostView)
async def create_post(
    data_in: schemas.PostCreate, session: AsyncSession = Depends(get_session)
) -> Any:
    post = await services.create_post(session, data_in=data_in)
    return ORJSONModelJSONResponse(schemas.PostView.from_orm(post))


@posts_router.get("/", response_model=schemas.ListPostView)
async def list_posts(uid: int, session: AsyncSession = Depends(get_session)) -> Any:
    posts = await services.list_posts(session, uid=uid)
    return ORJSONModelJSONResponse(schemas.ListPostView.from_orm(posts))


@posts_router.get("/{id}", response_model=schemas.PostView)
async def get_post(post: models.Post = Depends(get_valid_post_by_id)) -> Any:
    return ORJSONModelJSONResponse(schemas.PostView.from_orm(post))


@posts_router.delete("/{id}")
async def delete_post(
    post: models.Post = Depends(get_valid_post_by_id),
    session: AsyncSession = Depends(get_session),
) -> Any:
    await services.delete_post(session, post=post)
