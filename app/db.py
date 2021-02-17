from typing import Any, Generator

from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Session

from app.session import SessionLocal


@as_declarative()
class BaseModel:
    id: Any
    __name__: str

    def save(self, session):
        session.add(self)
        session.flush()


class SessionManager(object):

    def __init__(self, session_cls=SessionLocal):
        self.session: Session = session_cls()

    def __enter__(self):
        return self.session

    def __exit__(self, exception_type, exception_value, traceback):
        self.session.close()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
