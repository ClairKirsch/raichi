from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .users import User


class Messages(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    sender_id: int | None = Field(default=None, foreign_key="user.id")
    receiver_id: int | None = Field(default=None, foreign_key="user.id")

    content: str

    sender: Optional["User"] = Relationship(
        back_populates="messages_sent",
        sa_relationship_kwargs={"foreign_keys": "Messages.sender_id"},
    )

    receiver: Optional["User"] = Relationship(
        back_populates="messages_received",
        sa_relationship_kwargs={"foreign_keys": "Messages.receiver_id"},
    )
