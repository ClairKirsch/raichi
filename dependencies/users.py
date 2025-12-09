from typing import TYPE_CHECKING, Any
from typing_extensions import Annotated
from fastapi.params import Depends
from sqlmodel import Field, Relationship, SQLModel, Session, select

from dependencies.events import EventInfo
from dependencies.messages import MessageInfo
from .db import get_session
from .association_tables import UserEventAssoc

if TYPE_CHECKING:
    from .events import Event  # type: ignore
    from .messages import Message  # type: ignore


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str | None = None
    full_name: str | None = None
    hashed_password: str
    bio: str | None = None
    profile_image: str | None = None

    # Relationships
    events: list["Event"] = Relationship(
        back_populates="attendees", link_model=UserEventAssoc
    )
    messages_sent: list["Message"] = Relationship(
        back_populates="sender",
        sa_relationship_kwargs={"foreign_keys": "Message.sender_id"},
    )
    messages_received: list["Message"] = Relationship(
        back_populates="receiver",
        sa_relationship_kwargs={"foreign_keys": "Message.receiver_id"},
    )


class UserInfo(SQLModel):
    id: int
    username: str
    email: str | None = None
    full_name: str | None = None
    bio: str | None = None
    profile_image: str | None = None

    events: list["EventInfo"] = Field(default_factory=list)
    messages_sent: list["MessageInfo"] = Field(default_factory=list)
    messages_received: list["MessageInfo"] = Field(default_factory=list)


class UserCreate(SQLModel):
    username: str
    password: str


class UserProfile(SQLModel):
    full_name: str | None = None
    bio: str | None = None
    profile_image: str | None = None
    events: list["EventInfo"] = Field(default_factory=list)


class UserUpdate(SQLModel):
    full_name: str | None = None
    bio: str | None = None
    profile_image: str | None = None


def get_user_by_username(
    username: str, session: Annotated[Session, Depends(get_session)]
):
    return session.exec(select(User).where(User.username == username)).first()


def get_user_by_id(id: int, session: Annotated[Session, Depends(get_session)]):
    return session.exec(select(User).where(User.id == id)).first()
