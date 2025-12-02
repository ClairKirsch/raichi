from fastapi import FastAPI

from dependencies.db import create_db_and_tables
from routers.token import router as token_router
from routers.user import router as user_router

app = FastAPI()

app.include_router(
    prefix="",
    router=token_router,
)
app.include_router(
    router=user_router
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()