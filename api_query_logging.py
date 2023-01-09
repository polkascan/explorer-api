"""
A (debug)wrapper around the API to log all graphql queries.
It is used to measure frequently occuring gql queries, which then can be replayed using the recorded
timeline and frequency, and further examined using introspection and the automated playback test suite.
"""
import os, sys
import time
import starlette_graphene3

from dotenv import load_dotenv

from broadcaster import Broadcast

from aiologger.loggers.json import JsonLogger
from aiologger.handlers.files import AsyncTimedRotatingFileHandler, RolloverInterval
from aiologger.formatters.json import ExtendedJsonFormatter


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

env_file = ".env"
if os.path.exists(".local.env"):
    env_file = ".local.env"
load_dotenv(os.path.join(BASE_DIR, env_file))
sys.path.append(BASE_DIR)


__org_handle_http_request = starlette_graphene3.GraphQLApp._handle_http_request
__org_handle_websocket_message = starlette_graphene3.GraphQLApp._handle_websocket_message


# Warning! Below shall be monkeys and dragons :S


class __AsyncLogger(object):
    logger = None


async def __store_query(start, host, src, payload):
    stat = {
        "origin": hash(host),
        "type": src,
        "duration": time.time() - start,
        "query": payload["query"],
        "operation_name": payload.get("operationName", None),
        "operation_vars": payload.get("variables", None),
    }

    await __AsyncLogger.logger.info(stat)


async def __patched___handle_http_request(*args, **kwargs):
    start = time.time()
    req = args[1]
    payload = await req.json()
    res = await __org_handle_http_request(*args, **kwargs)
    if payload and payload.get("query", None):
        if payload["operationName"] != "IntrospectionQuery":
            await __store_query(start, req.client.host, "http", payload)

    return res


async def __patched___handle_websocket_message(*args, **kwargs):
    start = time.time()
    payload = args[1]
    payload = payload and payload.get("payload", None)
    res = await __org_handle_websocket_message(*args, **kwargs)

    if payload and payload.get("query", None):
        if payload["operationName"] != "IntrospectionQuery":
            await __store_query(start, args[2].client.host, "ws", payload)

    return res


# HACK NR1: We monkeypatch our starlette http & websocket handlers to be able to log the
#           raw GQL query. Starlette/FastAPI/Graphene unfortunatly do not provide hooks
#           to tap into this data, so we create one ourselves before starting the application
starlette_graphene3.GraphQLApp._handle_http_request = __patched___handle_http_request
starlette_graphene3.GraphQLApp._handle_websocket_message = __patched___handle_websocket_message


__org_connect__ = Broadcast.connect
__org_disconnect__ = Broadcast.disconnect


async def __logging_connect__(self):
    formatter = ExtendedJsonFormatter(
        exclude_fields=[
            "line_number",
            "function",
            "level",
            "file_path"]
    )
    handler = AsyncTimedRotatingFileHandler(
        filename="api_query_log.csv",
        when=RolloverInterval.DAYS,
        formatter=formatter
    )
    __AsyncLogger.logger = JsonLogger()
    __AsyncLogger.logger.add_handler(handler)
    return await __org_connect__(self)


async def __logging_disconnect__(self):
    await __AsyncLogger.logger.shutdown()
    return await __org_disconnect__(self)


# HACK NR2: We want to store the raw GQL queries to disk, we cannot abuse redis for this as it would
#           cache all queries in memory. We do not want to have this logging to have impact
#           on our requests, so we save to disk asynchronous. To achieve this we apply
#           another dirty hack; by tapping into the API Broadcast initialization, which is
#           already initialized asynchronous by our FastAPI app
Broadcast.connect = __logging_connect__
Broadcast.disconnect = __logging_disconnect__


from app.main import app
