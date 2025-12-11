from typing import Annotated
from fastapi import APIRouter
from fastapi.params import Depends
from sqlmodel import Session, select
from geopy import distance

from dependencies.db import get_session
from dependencies.events import Event, EventInfo
from dependencies.tags import Tag


router = APIRouter(tags=["search"], prefix="/search")


@router.post(
    "/by-tag",
    summary="Search for events by tag",
    description="Search for events associated with a specific tag.",
    response_model=list[EventInfo],
)
async def search_events_by_tag(
    tag_name: str, session: Annotated[Session, Depends(get_session)]
):
    results = session.exec(
        select(Event).where(Event.tags.any(Tag.name.ilike(f"%{tag_name}%")))
    ).all()
    return results


@router.post(
    "/by-location",
    summary="Search for events by location",
    description="Search for events within a certain radius of a given location.",
    response_model=list[EventInfo],
)
async def search_events_by_location(
    latitude: float,
    longitude: float,
    radius_miles: float,
    session: Annotated[Session, Depends(get_session)],
):
    all_events = session.exec(select(Event)).all()
    center_point = (latitude, longitude)
    nearby_events = []

    for event in all_events:
        event_point = (event.venue.latitude, event.venue.longitude)
        if distance.distance(center_point, event_point).miles <= radius_miles:
            nearby_events.append(event)

    return nearby_events
