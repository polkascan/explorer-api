import logging
import os, sys
import asyncio
import aiomysql
import sentry_sdk

from dotenv import load_dotenv
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from broadcaster import Broadcast


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


class CACHE():
    def __init__(self):
        self.last_block_number = -1


broadcast = Broadcast(os.environ['BROADCAST_URI'])
cache = CACHE()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 1  # 1 minutes
wait_seconds = 1

@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.DEBUG),
    after=after_log(logger, logging.WARN),
)
async def get_connection() -> None:
    try:
        return await aiomysql.connect(
            user=os.environ["DB_USERNAME"],
            db=os.environ["DB_NAME"],
            host=os.environ["DB_HOST"],
            port=int(os.environ["DB_PORT"], 0),
            password=os.environ["DB_PASSWORD"],
            loop=loop
        )
    except Exception as e:
        logger.error(e)
        if sentry_enabled: sentry_sdk.capture_exception(e)
        raise e


async def poll_db(loop):
    try:
        await broadcast.connect()
    except Exception as e:
        logger.error(e)
        if sentry_enabled: sentry_sdk.capture_exception(e)
        raise e

    while True:
        try:
            conn = await get_connection()

            async with conn.cursor() as cur:
                if cache.last_block_number == -1:
                    await cur.execute(f"SELECT MAX(bt.number) FROM explorer_block bt")
                else:
                    await cur.execute(f"""
                        SELECT
                            bt.number
                        FROM
                            explorer_block bt
                        WHERE
                            bt.number > {cache.last_block_number} 
                        ORDER BY
                            bt.number LIMIT 100""")

                res = await cur.fetchall()
                if res and res[-1][0] and res[-1][0] > cache.last_block_number:
                    blocks = ",".join([str(x[0]) for x in res])
                    await broadcast.publish(channel=f"{os.environ['CHAIN_ID']}-last-block", message=f"{blocks}")
                    cache.last_block_number = res[-1][0]
                else:
                    pass

            conn.close()
        except Exception as e:
            # Alternatively the argument can be omitted
            if sentry_enabled: sentry_sdk.capture_exception(e)
            raise e

        await asyncio.sleep(6)


loop = asyncio.get_event_loop()
loop.run_until_complete(poll_db(loop))
