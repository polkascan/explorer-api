import os, sys
from dotenv import load_dotenv

import asyncio
import aiomysql

from broadcaster import Broadcast

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


env_file = ".env"
if os.path.exists(".local.env"):
    env_file = ".local.env"
load_dotenv(os.path.join(BASE_DIR, env_file))
sys.path.append(BASE_DIR)


class CACHE():
    def __init__(self):
        self.last_block_id = -1


broadcast = Broadcast(f"redis://{os.environ['POLLING_REDIS_HOST']}:{os.environ['POLLING_REDIS_PORT']}")
cache = CACHE()


async def poll_db(loop):
    await broadcast.connect()

    while True:
        conn = await aiomysql.connect(
            user=os.environ["DB_USERNAME"],
            db=os.environ["DB_NAME"],
            host=os.environ["DB_HOST"],
            port=int(os.environ["DB_PORT"], 0),
            password=os.environ["DB_PASSWORD"],
            loop=loop
        )

        async with conn.cursor() as cur:
            if cache.last_block_id == -1:
                await cur.execute(f"SELECT MAX(bt.id) FROM data_block_total bt")
            else:
                await cur.execute(f"SELECT bt.id FROM data_block_total bt WHERE bt.id > {cache.last_block_id} ORDER BY bt.id LIMIT 100")

            res = await cur.fetchall()
            if res and res[-1][0] > cache.last_block_id:
                blocks = ",".join([str(x[0]) for x in res])
                await broadcast.publish(channel=f"{os.environ['CHAIN_ID']}-last-block", message=f"{blocks}")
                cache.last_block_id = res[-1][0]
            else:
                pass

        conn.close()
        await asyncio.sleep(6)


loop = asyncio.get_event_loop()
loop.run_until_complete(poll_db(loop))
