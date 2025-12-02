from typing import Annotated
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlmodel import Session, select

from dependencies.auth import get_current_active_user

from dependencies.db import get_session
from dependencies.users import User, UserInfo

router = APIRouter(tags=["user information"], prefix="/users")

@router.get("/me/", response_model=UserInfo, summary = "Get current user info", description = "Retrieve information about the currently authenticated user.")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user

@router.get("/{user_id}", response_model=UserInfo, summary = "Get user info by ID", description = "Retrieve information about a user by their unique ID.")
async def read_user_by_id(
    user_id: str,
    session: Annotated[Session, Depends(get_session)],
):
    user_data = session.exec(select(User).where(User.id == user_id)).first()
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    return user_data
