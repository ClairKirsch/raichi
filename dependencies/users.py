from typing_extensions import Annotated
from fastapi.params import Depends
from sqlmodel import Field, SQLModel, Session, select
from dependencies.db import get_session



class User(SQLModel, table=True):
    id: str | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str | None = None
    full_name: str | None = None
    hashed_password: str = Field(index=True)

class UserInfo(SQLModel):
    id: str
    username: str
    email: str | None = None
    full_name: str | None = None

def get_user(username: str, session: Annotated[Session, Depends(get_session)]):
    user_data = session.exec(select(User).where(User.username == username)).first()
    return user_data
