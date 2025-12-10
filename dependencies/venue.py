from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .events import Event  # type: ignore


class Venue(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    name: str
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    capacity: int | None = None

    events: list["Event"] = Relationship(back_populates="venue")


class VenueCreate(SQLModel):
    name: str
    address: str | None = None
    capacity: int | None = None
    latitude: float | None = None
    longitude: float | None = None


class VenueInfo(SQLModel):
    id: int
    name: str
    address: str | None = None
    capacity: int | None = None
    latitude: float | None = None
    longitude: float | None = None
