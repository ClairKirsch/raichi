from sqlmodel import Field, Relationship, SQLModel
from typing import TYPE_CHECKING
from dependencies.association_tables import EventTagAssoc

if TYPE_CHECKING:
    from .events import Event  # type: ignore


class Tag(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    events: list["Event"] = Relationship(
        back_populates="tags", link_model=EventTagAssoc
    )


class TagCreate(SQLModel):
    name: str


class TagInfo(SQLModel):
    id: int
    name: str
