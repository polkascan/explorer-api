"""
A (debug)wrapper around the API to log all graphql queries.
It is used to measure frequently occuring gql queries, which then can be replayed using the recorded
timeline and frequency, and further examined using introspection and the automated playback test suite.
"""
import os, sys
import time
import json
import uuid as uuid
import starlette_graphene3

import asyncio_redis

from datetime import datetime
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

env_file = ".env"
if os.path.exists(".local.env"):
    env_file = ".local.env"
load_dotenv(os.path.join(BASE_DIR, env_file))
sys.path.append(BASE_DIR)

__org_handle_http_request = starlette_graphene3.GraphQLApp._handle_http_request
__org_handle_websocket_message = starlette_graphene3.GraphQLApp._handle_websocket_message


async def __store_query(start, host, payload):
    connection = await asyncio_redis.Connection.create(host=os.environ['REDIS_IP'], port=int(os.environ['REDIS_PORT']))
    stat = json.dumps({
        "origin": hash(host),
        "start": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
        "duration": time.time() - start,
        "query": payload["query"],
        "operation_name": payload["operationName"],
        "operation_vars": payload["variables"],
    })
    await connection.set(f"__query_stat_{uuid.uuid4().hex}", stat)
    connection.close()


async def __patched___handle_http_request(*args, **kwargs):
    start = time.time()
    req = args[1]
    payload = await req.json()
    res = await __org_handle_http_request(*args, **kwargs)
    if payload and payload.get("query", None):
        if payload["operationName"] != "IntrospectionQuery":
            await __store_query(start, req.client.host, payload)

    return res


async def __patched___handle_websocket_message(*args, **kwargs):
    return await __org_handle_websocket_message(*args, **kwargs)


starlette_graphene3.GraphQLApp._handle_http_request = __patched___handle_http_request
starlette_graphene3.GraphQLApp._handle_websocket_message = __patched___handle_websocket_message


from app.main import app
