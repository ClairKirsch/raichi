from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from dependencies.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    Token,
    authenticate_user,
    create_access_token,
)
from dependencies.db import get_session

from typing import Annotated, Union

from fastapi import Form
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.oauth2 import OAuth2
from fastapi.openapi.docs import Doc


class OAuth2PasswordRequestFormWithOTP:
    """
    OAuth2 password flow form with an additional OTP field.
    """

    def __init__(
        self,
        *,
        grant_type: Annotated[
            Union[str, None],
            Form(pattern="^password$"),
            Doc(
                """
                The OAuth2 spec says it is required and MUST be the fixed string
                "password". This dependency is permissive and allows omitting it.
                """
            ),
        ] = None,
        username: Annotated[
            str,
            Form(),
            Doc("`username` string. The OAuth2 spec requires this exact field name."),
        ],
        password: Annotated[
            str,
            Form(json_schema_extra={"format": "password"}),
            Doc("`password` string. The OAuth2 spec requires this exact field name."),
        ],
        otp: Annotated[
            Union[None, str],
            Form(),
            Doc("Optional one-time password (OTP) for second-factor authentication."),
        ] = None,
        scope: Annotated[
            str,
            Form(),
            Doc(
                """
                A single string with several scopes separated by spaces.
                """
            ),
        ] = "",
        client_id: Annotated[
            Union[str, None],
            Form(),
            Doc("Optional OAuth2 client identifier."),
        ] = None,
        client_secret: Annotated[
            Union[str, None],
            Form(json_schema_extra={"format": "password"}),
            Doc("Optional OAuth2 client secret."),
        ] = None,
    ):
        self.grant_type = grant_type
        self.username = username
        self.password = password
        self.otp = otp
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret


router = APIRouter(tags=["authentication"])

# @router.post("/token")
# async def login_for_access_token(
#    session: Annotated[Session, Depends(get_session)],
#    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
# ) -> Token:
#    user = authenticate_user(session, form_data.username, form_data.password, None)
#    if not user:
#        raise HTTPException(
#            status_code=status.HTTP_401_UNAUTHORIZED,
#            detail="Incorrect username or password",
#            headers={"WWW-Authenticate": "Bearer"},
#        )
#    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#    access_token = create_access_token(
#        data={"sub": str(user.id), "username": user.username},
#        expires_delta=access_token_expires,
#    )
#    return Token(access_token=access_token, token_type="bearer")


@router.post("/token")
async def login_for_access_token_with_otp(
    session: Annotated[Session, Depends(get_session)],
    form_data: Annotated[OAuth2PasswordRequestFormWithOTP, Depends()],
) -> Token:
    user = authenticate_user(
        session,
        form_data.username,
        form_data.password,
        form_data.otp,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username, password, or OTP",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "username": user.username,
        },
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token, token_type="bearer")
