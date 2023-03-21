from aster.auth.dependencies import InjectAuthenticatedUser
from aster.database import InjectSession
from aster.posts.dependencies import InjectValidPost
from aster.responses import AsterResponse
from aster.routes import AsterRoute
from fastapi import APIRouter, status

from . import schemas, services

posts_router = APIRouter(prefix="/posts", route_class=AsterRoute)


@posts_router.post(
    "", response_model=schemas.PostView, status_code=status.HTTP_201_CREATED
)
async def create_post(
    data_in: schemas.PostCreate, session: InjectSession, user: InjectAuthenticatedUser
) -> AsterResponse:
    post = await services.create_post(session, data_in=data_in, user=user)
    await session.commit()
    return AsterResponse(
        schemas.PostView.from_orm(post).json(), status.HTTP_201_CREATED
    )


@posts_router.get("", response_model=schemas.ListPostView)
async def list_posts(username: str, session: InjectSession) -> AsterResponse:
    posts = await services.list_posts(session, username=username)
    return AsterResponse(schemas.ListPostView.from_orm(posts).json())


@posts_router.get("/{post_id}", response_model=schemas.PostView)
async def get_post(post: InjectValidPost) -> AsterResponse:
    return AsterResponse(schemas.PostView.from_orm(post).json())


@posts_router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post: InjectValidPost,
    session: InjectSession,
) -> AsterResponse:
    await services.delete_post(session, post=post)
    await session.commit()
    return AsterResponse(status_code=status.HTTP_204_NO_CONTENT)
