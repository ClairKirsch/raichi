from typing import Annotated
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlmodel import Session, select

from dependencies.auth import get_current_active_user

from dependencies.db import get_session
from dependencies.users import User, UserCreate, UserInfo
from pwdlib import PasswordHash
import re

argon2i_mcf_regex = re.compile(
    r"^\$argon2id\$v=\d+\$m=\d+,t=\d+,p=\d+\$[A-Za-z0-9+/]+\$[A-Za-z0-9+/]+={0,2}$"
)


def is_argon2i_mcf(hash_str: str) -> bool:
    return bool(argon2i_mcf_regex.match(hash_str))


router = APIRouter(tags=["user information"], prefix="/users")


@router.get(
    "/me/",
    response_model=UserInfo,
    summary="Get current user info",
    description="Retrieve information about the currently authenticated user.",
)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.get(
    "/{user_id}",
    response_model=UserInfo,
    summary="Get user info by ID",
    description="Retrieve information about a user by their unique ID.",
)
async def read_user_by_id(
    user_id: str,
    session: Annotated[Session, Depends(get_session)],
):
    user_data = session.exec(select(User).where(User.id == user_id)).first()
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    return user_data


@router.post(
    "/",
    response_model=UserInfo,
    summary="Create a new user",
    description="Create a new user with the provided information.",
)
async def create_user(
    user: UserCreate,
    session: Annotated[Session, Depends(get_session)],
):
    if is_argon2i_mcf(user.password):
        pass
    else:
        user.password = PasswordHash.recommended().hash(user.password)

    existing_user = session.exec(
        select(User).where(User.username == user.username)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = User(
        username=user.username,
        hashed_password=user.password,  # In a real app, hash the password!
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user
