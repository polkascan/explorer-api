from typing import Any, Generator

from sqlalchemy.orm import scoped_session
from sqlalchemy.ext.declarative import as_declarative, declared_attr

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


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
