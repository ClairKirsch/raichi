from typing import Annotated
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlmodel import Session, select
from dependencies.auth import get_current_active_user
from dependencies.db import get_session
from dependencies.users import User
from dependencies.messages import Message

router = APIRouter(tags=["messaging"], prefix="/message")


@router.post(
    "/{user_id}/send",
    summary="Send a message to a user",
    description="Send a message to the specified user.",
)
async def send_message(
    recipient_id: str,
    sender_id: Annotated[int, Depends(get_current_active_user)],
    latitude: float,
    longitude: float,
    message: str,
    session: Annotated[Session, Depends(get_session)],
):
    sender_id = sender_id.id
    recipient = session.exec(select(User).where(User.id == recipient_id)).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient user not found")
    message_instance = Message(
        sender_id=sender_id,
        receiver_id=recipient_id,
        content=message,
    )
    session.add(message_instance)
    session.commit()
    session.refresh(message_instance)
    return {"detail": "Message sent successfully", "message_id": message_instance.id}


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
        select(Message).where(Message.receiver_id == current_user.id)
    ).all()
    return messages
