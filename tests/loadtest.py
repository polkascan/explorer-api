import json
from locust import HttpUser, task, between



#https://loadforge.com/directory/websockets

class PerformanceTests(HttpUser):
    wait_time = between(1, 3)

    @task(1)
    def testFastApi1(self):
        # headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        # self.client.get("/predict", data=json.dumps(sample.dict()), headers=headers)
        self.client.get("/test/ping")

    @task(2)
    def testFastApi2(self):
        # headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        # self.client.get("/predict", data=json.dumps(sample.dict()), headers=headers)
        self.client.get("/test/db")


from websocket import create_connection
https://loadforge.com/directory/websockets