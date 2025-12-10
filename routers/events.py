from typing import Annotated
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlmodel import Session, select
from dependencies.auth import get_current_active_user
from dependencies.db import get_session
from dependencies.events import EventCreate, Event, EventInfo
from dependencies.users import User

router = APIRouter(tags=["event information"], prefix="/events")


@router.get(
    "/{event_id}",
    response_model=EventInfo,
    summary="Get event info by ID",
    description="Retrieve information about a event by its unique ID.",
)
async def read_event_by_id(
    event_id: str,
    session: Annotated[Session, Depends(get_session)],
):
    venue_data = session.exec(select(Event).where(Event.id == event_id)).first()
    if not venue_data:
        raise HTTPException(status_code=404, detail="Venue not found")
    return venue_data


@router.post(
    "/",
    response_model=Event,
    summary="Create a new event",
    description="Create a new event with the provided information.",
)
async def create_event(
    event: EventCreate,
    session: Annotated[Session, Depends(get_session)],
):
    new_event = Event.model_validate(event)
    session.add(new_event)
    session.commit()
    session.refresh(new_event)
    return new_event


@router.post(
    "/{event_id}/attend",
    summary="Attend an event",
    description="Mark the current user as attending the specified event.",
)
async def attend_event(
    event_id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[int, Depends(get_current_active_user)],
):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    user = session.get(User, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user in event.attendees:
        raise HTTPException(status_code=400, detail="User already attending the event")

    event.attendees.append(user)
    session.add(event)
    session.commit()
    return {"message": "User is now attending the event"}


@router.post(
    "/{event_id}/unattend",
    summary="Unattend an event",
    description="Remove the current user from the attendees of the specified event.",
)
async def unattend_event(
    event_id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[int, Depends(get_current_active_user)],
):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    user = session.get(User, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user not in event.attendees:
        raise HTTPException(status_code=400, detail="User is not attending the event")

    event.attendees.remove(user)
    session.add(event)
    session.commit()
    return {"message": "User has unattended the event"}
