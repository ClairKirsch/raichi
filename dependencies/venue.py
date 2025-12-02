from typing import List, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .events import Events  # type: ignore


class Venue(SQLModel, table=True):
    id: str | None = Field(default=None, primary_key=True)
    name: str
    address: str | None = None
    capacity: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    events: List["Events"] = Relationship(back_populates="venue")