from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .users import User


class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    sender_id: Optional[int] = Field(default=None, foreign_key="user.id")
    receiver_id: Optional[int] = Field(default=None, foreign_key="user.id")
    date: datetime = Field(sa_column=Column(DateTime))
    subject: str | None = Field(default=None, max_length=100)
    content: str | None = Field(default=None, max_length=1000)

    sender: Optional["User"] = Relationship(
        back_populates="messages_sent",
        sa_relationship_kwargs={"foreign_keys": "Message.sender_id"},
    )
    receiver: Optional["User"] = Relationship(
        back_populates="messages_received",
        sa_relationship_kwargs={"foreign_keys": "Message.receiver_id"},
    )


class MessageCreate(SQLModel):
    sender_id: int
    receiver_id: int
    subject: str
    content: str
    date: datetime = Field(default_factory=datetime.now)


class MessageInfo(SQLModel):
    id: int
    sender_id: int
    receiver_id: int
    date: datetime = Field(default=None)
    subject: str
    content: str
