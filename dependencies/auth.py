from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from pydantic import BaseModel
from sqlmodel import Session
import pyotp

from dependencies.db import get_session
from dependencies.users import User, get_user_by_id, get_user_by_username

SECRET_KEY = "05e36815ef8fb0f9495fa0450168319aa5afeaec20b64836a9914dff89a49d63"  # this should be in env vars or something but lol
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5 * (
    24 * 60
)  # lol dude this is a school project im not implementing refresh tokens


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    id: int | None = None


password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password, salt=password_hash.gensalt())


def authenticate_user(
    session: Annotated[Session, Depends(get_session)],
    username: str,
    password: str,
    otp: Optional[int],
):
    user = get_user_by_username(session=session, username=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    if user.totp_secrets and (otp is None or not verify_otp(user, otp)):
        return False
    return user


def verify_otp(
    user: User,
    otp: str,
) -> bool:
    for secret in user.totp_secrets:
        totp = pyotp.TOTP(secret.secret)
        if totp.verify(otp, valid_window=1) and secret.enabled:
            return True
    return False


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    session: Annotated[Session, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        id = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(id=id, username=username)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The access token expired",
            headers={"WWW-Authenticate": "Bearer error='invalid_token'"},
        )
    except InvalidTokenError:
        raise credentials_exception
    user = get_user_by_id(session=session, id=token_data.id)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user
