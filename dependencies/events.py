from typing import List
from sqlmodel import Field, Relationship, SQLModel

from .association_tables import UserEvent
from typing import TYPE_CHECKING
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .users import User  # type: ignore
    from .venue import Venue  # type: ignore


class Events(SQLModel, table=True):
    id: str | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = None
    date: str
    venue_id: str | None = Field(default=None, foreign_key="venue.id")
    venue: Optional["Venue"] = Relationship(back_populates="events")
    attendees: List["User"] = Relationship(back_populates="events", link_model=UserEvent)