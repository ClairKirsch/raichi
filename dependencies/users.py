from typing import List, Optional, TYPE_CHECKING, Any
import uuid
from typing_extensions import Annotated
from fastapi.params import Depends
from sqlmodel import Field, Relationship, SQLModel, Session, select
from .db import get_session
from .association_tables import UserEvent

if TYPE_CHECKING:
    from .events import Events  # type: ignore


class User(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    username: str = Field(index=True, unique=True)
    email: Optional[str] = None
    full_name: Optional[str] = None
    hashed_password: str = Field(index=True)
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    events: List["Events"] = Relationship(back_populates="attendees", link_model=UserEvent)


class UserInfo(SQLModel):
    id: str
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    events: List[Any] = Field(default_factory=list)

class UserCreate(SQLModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: str
    bio: Optional[str] = None
    profile_image: Optional[str] = None

def get_user(username: str, session: Annotated[Session, Depends(get_session)]):
    user_data = session.exec(select(User).where(User.username == username)).first()
    return user_data

def create_user(user_create: UserCreate, session: Annotated[Session, Depends(get_session)]):
    user = User(
        username=user_create.username,
        email=user_create.email,
        full_name=user_create.full_name,
        hashed_password=user_create.password,  # In a real app, hash the password!
        bio=user_create.bio,
        profile_image=user_create.profile_image,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user