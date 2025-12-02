from typing import Optional
from sqlmodel import SQLModel, Field

class UserEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[str] = Field(default=None, foreign_key="user.id")
    event_id: Optional[str] = Field(default=None, foreign_key="events.id")