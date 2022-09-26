import logging
import csv
import os

from scalecodec import ss58_decode
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from app import settings
from app.models.explorer import TaggedAccount

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Tagged account import started...")
    try:

        # Create database connection
        engine = create_engine(
            f"mysql+pymysql://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset=utf8mb4",
            pool_pre_ping=True
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        session = SessionLocal()

        # open CSV file
        with open(os.path.join(os.path.dirname(__file__), '../assets/tagged_accounts.csv'), 'r') as read_obj:

            csv_reader = csv.reader(read_obj)
            records = list(map(tuple, csv_reader))
            # Insert TaggedAccount
            for record in records[1:]:

                if record[2] == 'Scam':
                    risk_level = 4
                    risk_level_verbose = 'High'
                elif record[2] == 'Sanctions':
                    risk_level = 5
                    risk_level_verbose = 'Critical'
                else:
                    risk_level = None
                    risk_level_verbose = None

                tagged_account = TaggedAccount(
                    account_id=f'0x{ss58_decode(record[1])}',
                    tag_name=record[0],
                    tag_type=record[2],
                    tag_sub_type=record[3],
                    risk_level=risk_level,
                    risk_level_verbose=risk_level_verbose
                )
                try:
                    session.add(tagged_account)
                    session.flush()
                    session.commit()
                except IntegrityError:
                    session.rollback()

    except Exception as e:
        logger.error(e)
        raise e

    logger.info("Tagged account import finished")


if __name__ == "__main__":
    main()
