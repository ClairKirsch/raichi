from datetime import datetime, timedelta
from sqlmodel import Session, select
import yagmail
import os
import dotenv

from dependencies.events import Event


async def send_mail(session: Session) -> int:
    dotenv.load_dotenv()
    tomorrow = (datetime.now() + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    events_tomorrow = session.exec(select(Event).where(Event.date == tomorrow)).all()
    sent_letters = 0
    for event in events_tomorrow:
        for attendant in event.attendees:
            yag = yagmail.SMTP(
                user=os.environ["EMAIL_LOGIN"], password=os.environ["EMAIL_PASSWORD"]
            )
            body = f"""
            Hello, {attendant.full_name}. 
            Shinozawa would like to remind you that tomorrow, {event.date.strftime("%A, %B %d, %Y")}, you have {event.title} scheduled.

            Thank you for your patronage.
            """
            if attendant.email is not None:
                yag.send(
                    to=attendant.email,
                    subject="This is a reminder from Shinozawa!",
                    contents=body,
                )
                sent_letters += 1
    return sent_letters
