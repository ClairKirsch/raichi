from typing import Annotated
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlmodel import Session
import pyotp


from dependencies.auth import get_current_active_user
from dependencies.db import get_session

from dependencies.users import User
from dependencies.otp_secrets import (
    TOTPSecretCreate,
    TOTPSecretInfo,
    TOTPSecrets,
    TOTPVerifyRequest,
)

router = APIRouter(tags=["one time passwords"], prefix="/otp")


@router.post(
    "/new/",
    summary="Create a new OTP secret",
    description="Create a new OTP secret. Secrets are not activated until verified.",
    response_model=TOTPSecretInfo,
)
async def generate_new_otp_secret(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    current_user = session.merge(current_user)  # FIX: attach user to current session

    new_secret = TOTPSecrets(
        secret=pyotp.random_base32(), enabled=False, user_id=current_user.id
    )
    TOTPSecrets.model_validate(new_secret)
    current_user.totp_secrets.append(new_secret)
    session.add(new_secret)
    session.commit()
    session.refresh(new_secret)
    uri = pyotp.TOTP(new_secret.secret).provisioning_uri(
        name=current_user.username,
        issuer_name="Shinozawa",
    )

    return TOTPSecretInfo(secret=uri)


@router.post(
    "/verify/",
    summary="Verify a new OTP secret",
)
async def verify_new_otp(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    otp: TOTPVerifyRequest,
):
    otp = otp.otp
    new_secret_verified = False
    for secret in current_user.totp_secrets:
        totp = pyotp.TOTP(secret.secret)
        if totp.verify(otp) == True:
            new_secret_verified = True
            secret.enabled = True
            session.add(secret)
            session.commit()
            session.refresh(secret)
            return {"detail": "OTP verified successfully."}

    if new_secret_verified == False:
        raise HTTPException(
            status_code=400,
            detail="TOTP verification failure.",
        )
