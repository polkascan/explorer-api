from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event

from app.settings import settings


engine = create_engine(settings.API_SQLA_URI, pool_pre_ping=True, pool_size=40)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@event.listens_for(SessionLocal, 'after_begin')
def set_query_timeout(session, transaction, connection):
    session.execute('SET SESSION MAX_EXECUTION_TIME=1000;')

