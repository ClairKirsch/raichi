from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from dependencies.auth import ACCESS_TOKEN_EXPIRE_MINUTES, Token, authenticate_user, create_access_token
from dependencies.db import get_session


router = APIRouter(tags=["authentication"])

@router.post("/token")
async def login_for_access_token(
    session: Annotated[Session, Depends(get_session)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
