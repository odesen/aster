from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from aster.database import get_session

from .config import AuthConfig, get_settings
from .models import User
from .schemas import TokenData
from .services import get_user_by_username


async def get_valid_user_by_username(
    username: str, session: AsyncSession = Depends(get_session)
) -> User:
    user = await get_user_by_username(session, username=username)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return user


async def get_current_user(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="token")),
    session: AsyncSession = Depends(get_session),
    config: AuthConfig = Depends(get_settings),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.secret_key, algorithms=[config.algorithm])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user: User | None = await get_user_by_username(
        session=session, username=token_data.username
    )
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
