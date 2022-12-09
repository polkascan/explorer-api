import logging

from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import settings


logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init() -> None:
    try:
        engine = create_engine(
            f"mysql+pymysql://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/?charset=utf8mb4",
            pool_pre_ping=True
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        db = SessionLocal()

        # Try if DB exists
        db.execute(f"CREATE DATABASE IF NOT EXISTS {settings.DB_NAME}")
        db.commit()

    except Exception as e:
        logger.error(e)
        raise e


def main() -> None:
    logger.info("Initializing service")
    init()
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
