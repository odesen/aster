from aster.database import InjectSession
from aster.responses import AsterResponse
from aster.routes import AsterRoute
from fastapi import APIRouter, Depends, status

from . import dependencies, models, schemas, services

login_router = APIRouter(prefix="/login", route_class=AsterRoute)


@login_router.post(
    "", response_model=schemas.TokenResponse, status_code=status.HTTP_200_OK
)
async def login(
    token: schemas.TokenResponse = Depends(dependencies.authenticate_user),
) -> AsterResponse:
    return AsterResponse(token.json())


users_router = APIRouter(prefix="/users", route_class=AsterRoute)


@users_router.post(
    "/register", response_model=schemas.UserView, status_code=status.HTTP_201_CREATED
)
async def register_user(
    data_in: schemas.UserCreate, session: InjectSession
) -> AsterResponse:
    user = await services.create_user(session, data_in=data_in)
    await session.commit()
    return AsterResponse(
        schemas.UserView.from_orm(user).json(), status.HTTP_201_CREATED
    )


@users_router.get("", response_model=schemas.ListUserView)
async def list_users(session: InjectSession) -> AsterResponse:
    users = await services.list_users(session)
    return AsterResponse(schemas.ListUserView.from_orm(users).json())


@users_router.get("/{username}", response_model=schemas.UserView)
async def get_user(
    user: models.User = Depends(dependencies.get_valid_user_by_username),
) -> AsterResponse:
    return AsterResponse(schemas.UserView.from_orm(user).json())


user_router = APIRouter(
    prefix="/user",
    dependencies=[Depends(dependencies.get_current_user)],
    route_class=AsterRoute,
)


@user_router.get("", response_model=schemas.UserView)
async def get_authenticated_user(
    user: models.User = Depends(dependencies.get_current_user),
) -> AsterResponse:
    return AsterResponse(schemas.UserView.from_orm(user).json())


@user_router.patch("")
async def update_authenticated_user() -> AsterResponse:
    return AsterResponse()


@user_router.put("/password")
async def update_password_for_authenticated_user() -> AsterResponse:
    return AsterResponse()


user_block_router = APIRouter(prefix="/blocks", route_class=AsterRoute)


@user_block_router.get("", response_model=schemas.ListUserView)
async def list_users_blocked_by_authenticated_user(
    user: dependencies.InjectUser,
    session: InjectSession,
) -> AsterResponse:
    users = await services.list_users_blocked_by_user(session, username=user.username)
    return AsterResponse(schemas.ListUserView.from_orm(users).json())


@user_block_router.get("/{username}")
async def check_user_blocked_by_authenticated_user(
    username: str,
    user: dependencies.InjectUser,
    session: InjectSession,
) -> AsterResponse:
    is_blocked = await services.check_if_user_blocked_by_user(
        session, username=user.username, username_block=username
    )
    status_code = (
        status.HTTP_204_NO_CONTENT if is_blocked else status.HTTP_404_NOT_FOUND
    )
    return AsterResponse(status_code=status_code)


@user_block_router.put("/{username}", status_code=status.HTTP_204_NO_CONTENT)
async def block_user(
    username: str,
    user: dependencies.InjectUser,
    session: InjectSession,
) -> AsterResponse:
    await services.block_user(session, user=user, username_to_block=username)
    await session.commit()
    return AsterResponse(status_code=status.HTTP_204_NO_CONTENT)


@user_block_router.delete("/{username}")
async def unblock_user(
    username: str,
    user: dependencies.InjectUser,
    session: InjectSession,
) -> AsterResponse:
    await services.unblock_user(session, user=user, username_to_unblock=username)
    await session.commit()
    return AsterResponse(status_code=status.HTTP_204_NO_CONTENT)


user_router.include_router(user_block_router)
