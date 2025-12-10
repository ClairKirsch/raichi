from time import time
from typing import Annotated
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlmodel import Session, select
from dependencies.association_tables import UserEventAssoc
from dependencies.auth import get_current_active_user
from dependencies.db import get_session
from dependencies.events import Event
from dependencies.users import User
from dependencies.messages import Message, MessageCreate

router = APIRouter(tags=["messaging"], prefix="/message")


@router.post(
    "/{user_id}/send",
    summary="Send a message to a user",
    description="Send a message to the specified user.",
)
async def send_message(
    user_id: str,
    subject: str,
    message: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    sender_id = current_user.id
    recipient = session.exec(select(User).where(User.id == user_id)).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient user not found")
    shared_event = session.exec(
        select(Event)
        .where(Event.attendees.any(UserEventAssoc.user_id == current_user.id))
        .where(Event.attendees.any(UserEventAssoc.user_id == recipient.id))
    ).first()
    if not shared_event:
        raise HTTPException(
            status_code=400,
            detail="You can only message users who share an event with you",
        )
    message = MessageCreate(
        sender_id=sender_id,
        receiver_id=recipient.id,
        subject=subject,
        content=message,
        datetime=int(time()),
    )
    new_message = Message.model_validate(message)
    session.add(new_message)
    session.commit()
    session.refresh(new_message)
    return {"detail": "Message sent successfully", "message_id": new_message.id}


@router.get(
    "/inbox/",
    summary="Get messages for the current user",
    description="Retrieve all messages received by the currently authenticated user.",
)
async def get_messages(
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    messages = session.exec(
        select(Message)
        .where(Message.receiver_id == current_user.id)
        .order_by(Message.datetime)
    ).all()
    return messages
