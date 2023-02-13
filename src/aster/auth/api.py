from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from aster.database import get_session
from aster.responses import AsterResponse

from . import dependencies, models, schemas, services

users_router = APIRouter(prefix="/users")


@users_router.post(
    "", response_model=schemas.UserView, status_code=status.HTTP_201_CREATED
)
async def create_user(
    data_in: schemas.UserCreate, session: AsyncSession = Depends(get_session)
) -> AsterResponse:
    user = await services.create_user(session, data_in=data_in)
    await session.commit()
    return AsterResponse(
        schemas.UserView.from_orm(user).json(), status.HTTP_201_CREATED
    )


@users_router.get("")
async def list_users(session: AsyncSession = Depends(get_session)) -> Any:
    users = await services.list_users(session)
    return AsterResponse(schemas.ListUserView.from_orm(users))


@users_router.get("/{username}", response_model=schemas.UserView)
async def get_user(
    user: models.User = Depends(dependencies.get_valid_user_by_username),
) -> AsterResponse:
    return AsterResponse(schemas.UserView.from_orm(user).json())


user_router = APIRouter(
    prefix="/user", dependencies=[Depends(dependencies.get_current_active_user)]
)


@user_router.get("", response_model=schemas.UserView)
async def get_authentificated_user(
    user: models.User = Depends(dependencies.get_current_active_user),
) -> AsterResponse:
    return AsterResponse(schemas.UserView.from_orm(user).json())


# @user_router.patch("")
# async def update_authentificated_user() -> Any:
#     ...


user_block_router = APIRouter(prefix="/blocks")
user_router.include_router(user_block_router)


@user_block_router.get("/")
async def list_user_blocks() -> AsterResponse:
    return AsterResponse()


@user_block_router.get("/{username}")
async def check_user_blocked_by_authentificated_user(username: str) -> AsterResponse:
    return AsterResponse()


# @user_block_router.put("/{username}")
# async def block_user(username: str) -> Any:
#     ...


# @user_block_router.delete("/{username}")
# async def unblock_user(username: str) -> Any:
#     ...
