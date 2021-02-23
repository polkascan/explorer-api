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
            await cur.execute(f"SELECT MAX(bt.id) FROM data_block_total bt")
            res = await cur.fetchall()
            if cache.last_block_id == -1:
                #print("initial block_id tip: ", res[0][0])
                cache.last_block_id = res[0][0]
            elif res and res[0][0] > cache.last_block_id:
                #print("send block_id tip: ", res[0][0])
                await broadcast.publish(channel="blocks", message=f"{cache.last_block_id}")
                cache.last_block_id = res[0][0]
            else:
                #print("no updates..")
                pass

        conn.close()
        await asyncio.sleep(6)


loop = asyncio.get_event_loop()
loop.run_until_complete(poll_db(loop))
