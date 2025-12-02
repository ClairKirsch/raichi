from sqlmodel import Field, SQLModel


class UserEvent(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id")
    event_id: int | None = Field(default=None, foreign_key="events.id")
