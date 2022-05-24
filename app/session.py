from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.settings import settings

engine = create_engine(settings.API_SQLA_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, pool_size=40)
