from typing import TYPE_CHECKING, Optional
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel
from datetime import datetime

from dependencies.tags import TagInfo
from .association_tables import EventTagAssoc, UserEventAssoc
from .venue import VenueInfo

if TYPE_CHECKING:
    from .users import User  # type: ignore
    from .venue import Venue  # type: ignore
    from .tags import Tag  # type: ignore


class Event(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    date: datetime = Field(sa_column=Column(DateTime))

    venue_id: Optional[int] = Field(default=None, foreign_key="venue.id")
    venue: Optional["Venue"] = Relationship(back_populates="events")

    attendees: list["User"] = Relationship(
        back_populates="events", link_model=UserEventAssoc
    )
    estimated_attendance: int | None = None
    tags: list["Tag"] = Relationship(back_populates="events", link_model=EventTagAssoc)


class EventCreate(SQLModel):
    title: str
    description: str | None = None
    date: datetime = Field(default_factory=datetime.now)
    venue_id: int | None = None
    estimated_attendance: int | None = None


class EventInfo(SQLModel):
    id: int
    title: str
    description: str | None = None
    date: datetime = Field(default=None)
    estimated_attendance: int | None = None
    venue: VenueInfo = Field(default=None)
    tags: list["TagInfo"] = Field(default_factory=list)
