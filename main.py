from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from dependencies.db import create_db_and_tables
from routers.token import router as token_router
from routers.user import router as user_router
from routers.message import router as message_router
from routers.venue import router as venue_router
from routers.events import router as events_router
from routers.tags import router as tags_router
from routers.search import router as search_router
from routers.otp import router as otp_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(
    prefix="",
    router=token_router,
)
app.include_router(router=user_router)
app.include_router(router=message_router)
app.include_router(router=venue_router)
app.include_router(router=events_router)
app.include_router(router=tags_router)
app.include_router(router=search_router)
app.include_router(router=otp_router)
