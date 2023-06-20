from datetime import datetime, timedelta
from typing import Annotated

from aster.config import InjectSettings
from aster.database import InjectSession
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

from .models import User
from .schemas import JWTToken, TokenResponse
from .services import get_user_by_username
from .utils import verify_password

InjectToken = Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="/login"))]
InjectFormOAuth2 = Annotated[OAuth2PasswordRequestForm, Depends()]


async def authenticate_user(
    session: InjectSession,
    form: InjectFormOAuth2,
    config: InjectSettings,
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
        claims=token_data.model_dump(exclude_none=True),
        key=config.secret_key,
        algorithm=config.algorithm,
    )
    return TokenResponse(access_token=encoded_token, token_type="bearer")


InjectGeneratedToken = Annotated[TokenResponse, Depends(authenticate_user)]


async def get_valid_user_by_username(username: str, session: InjectSession) -> User:
    user = await get_user_by_username(session, username=username)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return user


InjectUser = Annotated[User, Depends(get_valid_user_by_username)]


async def get_current_user(
    token: InjectToken,
    session: InjectSession,
    config: InjectSettings,
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


InjectAuthenticatedUser = Annotated[User, Depends(get_current_user)]


async def get_current_active_user(
    current_user: InjectAuthenticatedUser,
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
