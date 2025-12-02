from typing import Annotated
from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    # Import model modules so classes register with SQLModel.metadata
    from . import association_tables  # noqa: F401
    from . import users  # noqa: F401
    from . import venue  # noqa: F401
    from . import events  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
