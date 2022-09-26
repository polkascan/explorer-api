import logging
import os, sys
import asyncio
import sentry_sdk

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from contextlib import contextmanager

from app.session import engine
from app.models.harvester import HarvesterStatus


Session = sessionmaker(engine)

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

env_file = ".env"
if os.path.exists(".local.env"):
    env_file = ".local.env"
load_dotenv(os.path.join(BASE_DIR, env_file))
sys.path.append(BASE_DIR)

sentry_enabled = os.environ['SENTRY_DSN'] and len(os.environ['SENTRY_DSN']) > 1

if sentry_enabled:
    sentry_sdk.init(dsn=os.environ['SENTRY_DSN'], traces_sample_rate=1.0, attach_stacktrace=True, request_bodies='always')
    import gitcommit
    sentry_sdk.set_tag("api-project-name", os.environ['SENTRY_PROJECT_NAME'])
    sentry_sdk.set_tag("api-server-name", os.environ['SENTRY_SERVER_NAME'])
    sentry_sdk.set_tag("api-chain-id", os.environ['CHAIN_ID'])
    sentry_sdk.set_tag("api-git-dt", gitcommit.date)
    sentry_sdk.set_tag("api-git-branch", gitcommit.branch or "main")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("explorer-harvester")


async def harvest_loop(loop):
    while True:
        try:
            with session_scope() as db:
                #t = db.query(HarvesterStatus).get('PROCESS_DECODER_MAX_BLOCKNUMBER')
                start_record = db.query(HarvesterStatus).get('PROCESS_ETL')
                end_record = db.query(HarvesterStatus).get('PROCESS_DECODER_MAX_BLOCKNUMBER')

                if not start_record:
                    start_blocknumber = 0
                else:
                    start_blocknumber = (start_record.value or -1) + 1

                end_blocknumber = max(end_record and (end_record.value + 999) or 999, start_blocknumber + 999)

                if end_blocknumber >= start_blocknumber:
                    logger.info(f'Start ETL process from #{start_blocknumber} to #{end_blocknumber}')
                    db.execute('CALL etl_range({}, {}, 1)'.format(
                        start_blocknumber, end_blocknumber
                    ))
                    db.commit()

                    record = db.query(HarvesterStatus).get('PROCESS_ETL')
                    logger.info('Finished ETL process at #{}'.format(record.value or 0))

        except Exception as e:
            # Alternatively the argument can be omitted
            if sentry_enabled: sentry_sdk.capture_exception(e)
            raise e

        await asyncio.sleep(6)


loop = asyncio.get_event_loop()
loop.run_until_complete(harvest_loop(loop))
