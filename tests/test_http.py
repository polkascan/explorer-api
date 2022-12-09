import os
import time

from locust.contrib.fasthttp import FastHttpUser
from locust import events

from tests.settings import settings
from tests.queries import QueryTasks

from app.session import engine
from app.models.explorer import Block

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


class HttpClient(FastHttpUser):
    tasks = [QueryTasks]

    def __init__(self, *args, **kwargs):
        self.host = f"http://{settings.SERVER_ADDR}:{settings.SERVER_PORT}{settings.HTTP_MOUNT}"
        super().__init__(*args, **kwargs)
        with session_scope() as db:
            blocks = db.query(Block.number).limit(settings.TEST_SUBSCRIPTION_NR_BLOCKS)
            self.AVAILABLE_BLOCKS = [x[0] for x in blocks]

    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        pass

    def on_stop(self):
        """ on_stop is called when the TaskSet is stopping """
        pass

    def send(self, name, payload):
        start_at = time.time()
        with self.client.post(
                self.host,
                name=name,
                json={"query": payload},
                catch_response=True) as response:

            res = response.json()

            if (time.time() - start_at) > 1:
                events.request.fire(
                    request_type='POST',
                    exception='Response Time was more than 1 second',
                    name=name,
                    response_time=int((time.time() - start_at)),
                    response_length=len(res),
                    context={},
                )

            if res.get("errors", None):
                events.request.fire(
                    request_type='POST',
                    exception=res,
                    name=name,
                    response_time=int((time.time() - start_at)),
                    response_length=len(res),
                    context={},
                )
            else:
                events.request.fire(
                    request_type='POST',
                    name=name,
                    response_time=int((time.time() - start_at)),
                    response_length=len(res),
                    exception=None,
                    context={},
                )

            return res
