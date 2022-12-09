import time
import json
import gevent
import websocket

from locust import events, User

from app.session import engine
from app.models.explorer import Block

from tests.settings import settings
from tests.queries import QueryTasks

from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

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


class SocketClient(object):

    def __init__(self, host):
        self.host = host
        self.connect()

    def connect(self):
        self.ws = websocket.WebSocket()
        self.connection_timeout = int(settings.TEST_CONNECTION_WAIT_TIME)
        self.ws.settimeout(self.connection_timeout)
        self.ws.connect(self.host)
        self.query_timeout = int(settings.TEST_QUERY_WAIT_TIME)

    def on_start(self):
        self.send('GQL_CONNECTION_INIT', '{"type": "' + settings.GQL_CONNECTION_INIT + '" }', False)

    def on_quit(self):
        self.ws.close()

    def on_stop(self):
        self.ws.close()

    def send(self, name, payload, parse=True):
        start_at = time.time()

        if parse:
            ws_req = json.dumps({
                "type": settings.GQL_START,
                "id": name,
                "payload": {
                    "query": payload,
                    "operationName": None,
                },
            })
        else:
            ws_req = payload

        self.ws.send(ws_req)

        #TODO: this makes the whole thing blocking, which kinda defies the throughput benchmark?
        g = gevent.spawn(self.ws.recv)
        result = g.get(block=True, timeout=self.query_timeout)

        if not result:
            events.request_failure.fire(
                request_type='WEBSOCKET',
                exception='Empty response',
                name=name,
                response_time=int((time.time() - start_at)),
                response_length=len(result),
                context={},
            )

        res = json.loads(result)

        if (time.time() - start_at) > 1:
            events.request.fire(
                request_type='WEBSOCKET',
                exception='Response Time was more than 1 second',
                name=name,
                response_time=int((time.time() - start_at)),
                response_length=len(result),
                context={},
            )


        if res["type"] == "error":
            events.request.fire(
                request_type='WEBSOCKET',
                exception=result,
                name=name,
                response_time=int((time.time() - start_at)),
                response_length=len(result),
                context={},
            )
        else:
            events.request.fire(
                request_type='WEBSOCKET',
                name=name,
                response_time=int((time.time() - start_at)),
                response_length=len(result),
                exception=None,
                context={},
            )
        return res


class WSUser(User):
    tasks = [QueryTasks]

    def __init__(self, *args, **kwargs):
        super(WSUser, self).__init__(*args, **kwargs)
        self.client = SocketClient(settings.WEBSOCKET_URI+settings.WS_MOUNT)
        with session_scope() as db:
            blocks = db.query(Block.number).limit(settings.TEST_SUBSCRIPTION_NR_BLOCKS)
            self.AVAILABLE_BLOCKS = [x[0] for x in blocks]

    def send(self, *args, **kwargs):
        self.client.send(*args, **kwargs)

    def on_start(self):
        self.client.on_start()

    def on_stop(self):
        self.client.on_stop()
