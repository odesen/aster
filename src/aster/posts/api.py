from aster.database import get_session
from aster.posts.dependencies import get_valid_post_by_id
from aster.responses import AsterResponse
from aster.routes import AsterRoute
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from . import models, schemas, services

posts_router = APIRouter(prefix="/posts", route_class=AsterRoute)


@posts_router.post(
    "/", response_model=schemas.PostView, status_code=status.HTTP_201_CREATED
)
async def create_post(
    data_in: schemas.PostCreate, session: AsyncSession = Depends(get_session)
) -> AsterResponse:
    post = await services.create_post(session, data_in=data_in)
    return AsterResponse(
        schemas.PostView.from_orm(post).json(), status.HTTP_201_CREATED
    )


@posts_router.get("/", response_model=schemas.ListPostView)
async def list_posts(
    username: str, session: AsyncSession = Depends(get_session)
) -> AsterResponse:
    posts = await services.list_posts(session, username=username)
    return AsterResponse(schemas.ListPostView.from_orm(posts).json())


@posts_router.get("/{id}", response_model=schemas.PostView)
async def get_post(post: models.Post = Depends(get_valid_post_by_id)) -> AsterResponse:
    return AsterResponse(schemas.PostView.from_orm(post).json())


@posts_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post: models.Post = Depends(get_valid_post_by_id),
    session: AsyncSession = Depends(get_session),
) -> AsterResponse:
    await services.delete_post(session, post=post)
    return AsterResponse(status_code=status.HTTP_204_NO_CONTENT)
