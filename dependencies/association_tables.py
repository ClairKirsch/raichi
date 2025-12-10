from sqlmodel import Field, SQLModel


class UserEventAssoc(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id")
    event_id: int | None = Field(default=None, foreign_key="event.id")


class EventTagAssoc(SQLModel, table=True):
    event_id: int | None = Field(default=None, foreign_key="event.id", primary_key=True)
    tag_id: int | None = Field(default=None, foreign_key="tag.id", primary_key=True)
