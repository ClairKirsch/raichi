from typing import Annotated
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlmodel import Session, select
from dependencies.association_tables import EventTagAssoc
from dependencies.db import get_session
from dependencies.events import Event
from dependencies.tags import Tag, TagCreate, TagInfo

router = APIRouter(tags=["tag information"], prefix="/tags")


@router.get(
    "/{tag_id}",
    response_model=TagInfo,
    summary="Get tag info by ID",
    description="Retrieve information about a tag by its unique ID.",
)
async def read_tag_by_id(
    tag_id: str,
    session: Annotated[Session, Depends(get_session)],
):
    venue_data = session.exec(select(Tag).where(Tag.id == tag_id)).first()
    if not venue_data:
        raise HTTPException(status_code=404, detail="Venue not found")
    return venue_data


@router.post(
    "/",
    response_model=TagInfo,
    summary="Create a new venue",
    description="Create a new venue with the provided information.",
)
async def create_tag(
    tag: TagCreate,
    session: Annotated[Session, Depends(get_session)],
):
    new_tag = Tag.model_validate(tag)
    session.add(new_tag)
    session.commit()
    session.refresh(new_tag)
    return new_tag

@router.post(
    "/{event_id}/associate/{tag_id}",
    summary="Associate a tag with an event",
    description="Associate the specified tag with the specified event.",
)
async def associate_tag_with_event(event_id: int, tag_id: int, session: Session = Depends(get_session)):
    # Check if the event exists
    event = session.exec(select(Event).where(Event.id == event_id)).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check if the tag exists
    tag = session.exec(select(Tag).where(Tag.id == tag_id)).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Create association
    association = EventTagAssoc(event_id=event_id, tag_id=tag_id)
    session.add(association)
    session.commit()
    session.refresh(association)  # Refresh to load the new data
    if not association:
        raise HTTPException(status_code=500, detail="Failed to associate tag with event")
    return {"detail": "Tag associated with event successfully"}
