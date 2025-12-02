from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .events import Events  # type: ignore


class Venue(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    address: str | None = None
    capacity: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    events: list["Events"] = Relationship(back_populates="venue")
