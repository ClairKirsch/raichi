from typing import Annotated
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlmodel import Session, select
from dependencies.db import get_session
from dependencies.venue import Venue, VenueCreate

router = APIRouter(tags=["venue information"], prefix="/venues")


@router.get(
    "/{venue_id}",
    response_model=Venue,
    summary="Get venue info by ID",
    description="Retrieve information about a venue by its unique ID.",
)
async def read_venue_by_id(
    venue_id: str,
    session: Annotated[Session, Depends(get_session)],
):
    venue_data = session.exec(select(Venue).where(Venue.id == venue_id)).first()
    if not venue_data:
        raise HTTPException(status_code=404, detail="Venue not found")
    return venue_data


@router.post(
    "/",
    response_model=Venue,
    summary="Create a new venue",
    description="Create a new venue with the provided information.",
)
async def create_venue(
    venue: VenueCreate,
    session: Annotated[Session, Depends(get_session)],
):
    new_venue = VenueCreate.model_validate(venue)
    session.add(new_venue)
    session.commit()
    session.refresh(new_venue)
    return new_venue
