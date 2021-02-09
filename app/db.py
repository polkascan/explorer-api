from typing import Any, Generator

from sqlalchemy.orm import scoped_session
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Session

from fastapi import BackgroundTasks

from app.session import SessionLocal


db_session = scoped_session(SessionLocal)


@as_declarative()
class BaseModel:
    id: Any
    query = db_session.query_property()
    __name__: str

    def save(self, session):
        session.add(self)
        session.flush()


class SessionManager(object):

    def __init__(self):
        self.session: Session = db_session()

    def __enter__(self):
        return self.session

    def __exit__(self, exception_type, exception_value, traceback):
        self.session.close()


def close_session(session: Session):
    session.close()


def get_db(
    background_tasks: BackgroundTasks
):
    with SessionManager() as session:
        background_tasks.add_task(close_session, session)
        yield session
