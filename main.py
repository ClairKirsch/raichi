from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from dependencies.db import create_db_and_tables
from routers.token import router as token_router
from routers.user import router as user_router


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
