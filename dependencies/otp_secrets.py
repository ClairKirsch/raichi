from datetime import datetime
from typing import TYPE_CHECKING
from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .users import User


class TOTPSecrets(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    secret: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    enabled: bool = Field(default=False)
    user: "User" = Relationship(back_populates="totp_secrets")


class TOTPSecretCreate(SQLModel):
    secret: str
    enabled: bool
    user_id: int


class TOTPSecretInfo(SQLModel):
    secret: str

class TOTPVerifyRequest(BaseModel):
    otp: str