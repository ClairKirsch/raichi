from typing import TYPE_CHECKING, Any
from typing_extensions import Annotated
from fastapi.params import Depends
from sqlmodel import Field, Relationship, SQLModel, Session, select
from .db import get_session
from .association_tables import UserEvent

if TYPE_CHECKING:
    from .events import Events  # type: ignore
    from .messages import Messages  # type: ignore


class User(SQLModel, table=True):
    id: int | None = Field(primary_key=True)

    username: str = Field(index=True, unique=True)
    email: str | None = None
    full_name: str | None = None
    hashed_password: str = Field(index=True)
    bio: str | None = None
    profile_image: str | None = None

    events: list["Events"] = Relationship(
        back_populates="attendees", link_model=UserEvent
    )

    messages_sent: list["Messages"] = Relationship(
        back_populates="sender",
        sa_relationship_kwargs={"foreign_keys": "Messages.sender_id"},
    )

    messages_received: list["Messages"] = Relationship(
        back_populates="receiver",
        sa_relationship_kwargs={"foreign_keys": "Messages.receiver_id"},
    )


class UserInfo(SQLModel):
    id: int
    username: str
    email: str | None = None
    full_name: str | None = None
    bio: str | None = None
    profile_image: str | None = None

    events: list[Any] = Field(default_factory=list)
    messages_sent: list[Any] = Field(default_factory=list)
    messages_received: list[Any] = Field(default_factory=list)


class UserCreate(SQLModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    password: str
    bio: str | None = None
    profile_image: str | None = None


def get_user(username: str, session: Annotated[Session, Depends(get_session)]):
    return session.exec(select(User).where(User.username == username)).first()


def create_user(
    user_create: UserCreate, session: Annotated[Session, Depends(get_session)]
):
    user = User(
        username=user_create.username,
        email=user_create.email,
        full_name=user_create.full_name,
        hashed_password=user_create.password,  # Reminder: hash in real app
        bio=user_create.bio,
        profile_image=user_create.profile_image,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
