# import json
# from locust import HttpUser, task, between



#https://loadforge.com/directory/websockets
#
# class PerformanceTests(HttpUser):
#     wait_time = between(1, 3)
#
#     @task(1)
#     def testFastApi1(self):
#         # headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
#         # self.client.get("/predict", data=json.dumps(sample.dict()), headers=headers)
#         self.client.get("/test/ping")
#
#     @task(2)
#     def testFastApi2(self):
#         # headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
#         # self.client.get("/predict", data=json.dumps(sample.dict()), headers=headers)
#         self.client.get("/test/db")
#
#
# from websocket import create_connection
# https://loadforge.com/directory/websockets


import time
import json
import gevent

from uuid import uuid4

from locust import HttpUser, TaskSet, task, events, User
import websocket


GQL_CONNECTION_ACK = "connection_ack"
GQL_CONNECTION_ERROR = "connection_error"
GQL_CONNECTION_INIT = "connection_init"
GQL_CONNECTION_TERMINATE = "connection_terminate"
GQL_COMPLETE = "complete"
GQL_DATA = "data"
GQL_ERROR = "error"
GQL_START = "start"
GQL_STOP = "stop"


class SocketClient(object):

    def __init__(self, host):
        self.host = "ws://127.0.0.1:5002/graphql-ws"
        self.connect()

    def connect(self):
        self.ws = websocket.WebSocket()
        self.ws.settimeout(10)
        self.ws.connect(self.host)
        #self.ws.send('{"type": "' + GQL_CONNECTION_INIT + '" }')
        data = self.send_with_response({"type": GQL_CONNECTION_INIT})
        #import pdb;pdb.set_trace()
        #events.quitting += self.on_close

    def on_close(self):
        self.ws.close()

    def on_quit(self):
        self.ws.disconnect()

    def send(self, payload):

        start_time = time.time()
        e = None
        try:
            data = self.send_with_response(payload)
            #assert data['_messageId'] == message_id
            #assert data['session_id'] == self.session_id
        except AssertionError as exp:
            e = exp
        except Exception as exp:
            e = exp
            self.ws.close()
            self.connect()
        elapsed = int((time.time() - start_time) * 1000)
        if e:
            events.request_failure.fire(request_type='sockjs', name='send',
                                        response_time=elapsed, exception=e)
        else:
            events.request_success.fire(request_type='sockjs', name='send',
                                        response_time=elapsed,
                                        response_length=0)

    def send_with_response(self, payload):
        json_data = json.dumps(payload)

        g = gevent.spawn(self.ws.send, json_data)
        g.get(block=True, timeout=2)
        g = gevent.spawn(self.ws.recv)
        result = g.get(block=True, timeout=10)

        json_data = json.loads(result)
        return json_data


class WSBehavior(TaskSet):
    @task(1)
    def action(self):
        data = {
            "action": "do_stuff",
            "param": "123",
        }
        self.client.send(data)


class WSUser(User):
    task_set = WSBehavior
    min_wait = 1000
    max_wait = 3000

    def __init__(self, *args, **kwargs):
        super(WSUser, self).__init__(*args, **kwargs)
        self.client = SocketClient('ws://%s/rt/websocket' % self.host)