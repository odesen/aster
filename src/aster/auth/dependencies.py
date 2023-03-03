from datetime import datetime, timedelta

from aster.database import get_session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from .config import AuthConfig, get_settings
from .models import User
from .schemas import JWTToken, TokenResponse
from .services import get_user_by_username
from .utils import verify_password


async def authenticate_user(
    session: AsyncSession = Depends(get_session),
    form: OAuth2PasswordRequestForm = Depends(),
    config: AuthConfig = Depends(get_settings),
) -> TokenResponse:
    user = await get_user_by_username(session, username=form.username)
    if not user:
        raise Exception
    if not verify_password(form.password, user.password):
        raise Exception
    token_data = JWTToken(
        sub=user.username,
        exp=datetime.utcnow() + timedelta(minutes=config.access_token_expire_minutes),
    )
    encoded_token = jwt.encode(
        claims=token_data.dict(exclude_none=True),
        key=config.secret_key,
        algorithm=config.algorithm,
    )
    return TokenResponse(access_token=encoded_token, token_type="bearer")


async def get_valid_user_by_username(
    username: str, session: AsyncSession = Depends(get_session)
) -> User:
    user = await get_user_by_username(session, username=username)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return user


async def get_current_user(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")),
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
        decoded_token = JWTToken(**payload)
        if decoded_token.sub is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user: User | None = await get_user_by_username(
        session=session, username=decoded_token.sub
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
