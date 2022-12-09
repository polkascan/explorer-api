import random
from locust import TaskSet, task


class QueryTasks(TaskSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_client = args[0]

    def on_start(self):
        pass

    @task
    def getLatestBlock(self):
        self.custom_client.send(
            "getLatestBlock",
            "query { getLatestBlock { number, hash } }"
        )

    @task
    def getBlock(self):
        block_nr = random.choice(self.custom_client.AVAILABLE_BLOCKS)
        self.custom_client.send(
            "getBlock",
            f"query {{ getBlock(filters: {{number: {block_nr} }}) {{ number, hash }} }}"
        )

    @task
    def getBlocks(self):
        self.custom_client.send(
            "getBlocks",
            "query { getBlocks(pageSize: 10) { objects { number, hash}, pageInfo {pageSize, pageNext, pagePrev} } }"
        )

    # @task
    # def getExtrinsic(self):
    #     self.custom_client.send(
    #         "GetExtrinsic",
    #         "query { getExtrinsic(filters: {number: 1}) { number, hash } }"
    #     )
    #
    #
    # @task
    # def getExtrinsics(self):
    #     self.custom_client.send(
    #         "GetExtrinsics",
    #         "query { getExtrinsics(pageSize: 10) { objects { number, hash}, pageInfo {pageSize, pageNext, pagePrev} } }"
    #     )
    #
    # @task
    # def getEvent(self):
    #     self.custom_client.send(
    #         "GetEvent",
    #         "query { getEvent(filters: {number: 1}) { number, hash } }"
    #     )
    #
    # @task
    # def getEvents(self):
    #     self.custom_client.send(
    #         "GetEvents",
    #         "query { getEvents(pageSize: 10) { objects { number, hash}, pageInfo {pageSize, pageNext, pagePrev} } }"
    #     )
    #
    # @task
    # def getRuntime(self):
    #     self.custom_client.send(
    #         "GetRuntime",
    #         "query { getRuntime(filters: {number: 1}) { number, hash } }"
    #     )
    #
    # @task
    # def getLatestRuntime(self):
    #     self.custom_client.send(
    #         "getLatestRuntime",
    #         "query { getLatestRuntime(pageSize: 10) { objects { number, hash}, pageInfo {pageSize, pageNext, pagePrev} } }"
    #     )
    #
    # @task
    # def getRuntimes(self):
    #     self.custom_client.send(
    #         "GetRuntimes",
    #         "query { getRuntimes(pageSize: 10) { objects { number, hash}, pageInfo {pageSize, pageNext, pagePrev} } }"
    #     )
    #
    # @task
    # def getRuntimeCall(self):
    #     self.custom_client.send(
    #         "GetRuntimeCall",
    #         "query { getRuntimeCall(filters: {number: 1}) { number, hash } }"
    #     )
    #
    # @task
    # def getRuntimeCalls(self):
    #     self.custom_client.send(
    #         "GetRuntimeCalls",
    #         "query { getRuntimeCalls(pageSize: 10) { objects { number, hash}, pageInfo {pageSize, pageNext, pagePrev} } }"
    #     )
    #
    # @task
    # def getRuntimeCallArguments(self):
    #     self.custom_client.send(
    #         "GetRuntimeCallArguments",
    #         "query { getRuntimeCallArguments(pageSize: 10) { objects { number, hash}, pageInfo {pageSize, pageNext, pagePrev} } }"
    #     )
    #
    # @task
    # def getRuntimeConstant(self):
    #     self.custom_client.send(
    #         "GetRuntimeConstant",
    #         "query { getRuntimeConstant(filters: {number: 1}) { number, hash } }"
    #     )
    #
    # @task
    # def getRuntimeConstants(self):
    #     self.custom_client.send(
    #         "GetRuntimeConstants",
    #         "query { getRuntimeConstants(pageSize: 10) { objects { number, hash}, pageInfo {pageSize, pageNext, pagePrev} } }"
    #     )
    #
    # @task
    # def getRuntimeErrorMessage(self):
    #     self.custom_client.send(
    #         "GetRuntimeErrorMessage",
    #         "query { getRuntimeErrorMessage(filters: {number: 1}) { number, hash } }"
    #     )
    #
    # @task
    # def getRuntimeErrorMessages(self):
    #     self.custom_client.send(
    #         "GetRuntimeErrorMessages",
    #         "query { getRuntimeErrorMessages(pageSize: 10) { objects { number, hash}, pageInfo {pageSize, pageNext, pagePrev} } }"
    #     )
    #
    # @task
    # def getRuntimeEvent(self):
    #     self.custom_client.send(
    #         "GetRuntimeEvent",
    #         "query { getRuntimeEvent(filters: {number: 1}) { number, hash } }"
    #     )
    #
    # @task
    # def getRuntimeEvents(self):
    #     self.custom_client.send(
    #         "GetRuntimeEvents",
    #         "query { getRuntimeEvents(pageSize: 10) { objects { number, hash}, pageInfo {pageSize, pageNext, pagePrev} } }"
    #     )
    #
    # @task
    # def getRuntimeEventAttributes(self):
    #     self.custom_client.send(
    #         "GetRuntimeEventAttributes",
    #         "query { getRuntimeEventAttributes(pageSize: 10) { objects { number, hash}, pageInfo {pageSize, pageNext, pagePrev} } }"
    #     )
    #
    # @task
    # def getRuntimePallet(self):
    #     self.custom_client.send(
    #         "GetRuntimePallet",
    #         "query { getRuntimePallet(filters: {number: 1}) { number, hash } }"
    #     )
    #
    # @task
    # def getRuntimePallets(self):
    #     self.custom_client.send(
    #         "GetRuntimePallets",
    #         "query { getRuntimePallets(pageSize: 10) { objects { number, hash}, pageInfo {pageSize, pageNext, pagePrev} } }"
    #     )
    #
    # @task
    # def getRuntimeStorage(self):
    #     self.custom_client.send(
    #         "GetRuntimeStorage",
    #         "query { getRuntimeStorage(filters: {number: 1}) { number, hash } }"
    #     )
    #
    # @task
    # def getRuntimeStorages(self):
    #     self.custom_client.send(
    #         "GetRuntimeStorages",
    #         "query { getRuntimeStorages(pageSize: 10) { objects { number, hash}, pageInfo {pageSize, pageNext, pagePrev} } }"
    #     )
    #
    # @task
    # def getRuntimeType(self):
    #     self.custom_client.send(
    #         "GetRuntimeType",
    #         "query { getRuntimeType(filters: {number: 1}) { number, hash } }"
    #     )
    #
    # @task
    # def getRuntimeTypes(self):
    #     self.custom_client.send(
    #         "GetRuntimeTypes",
    #         "query { getRuntimeTypes(pageSize: 10) { objects { number, hash}, pageInfo {pageSize, pageNext, pagePrev} } }"
    #     )
    #
    # @task
    # def getLog(self):
    #     self.custom_client.send(
    #         "GetLog",
    #         "query { getLog(filters: {number: 1}) { number, hash } }"
    #     )
    #
    # @task
    # def getLogs(self):
    #     self.custom_client.send(
    #         "GetLogs",
    #         "query { getLogs(pageSize: 10) { objects { number, hash}, pageInfo {pageSize, pageNext, pagePrev} } }"
    #     )
    #
    # @task
    # def getTransfer(self):
    #     self.custom_client.send(
    #         "GetTransfer",
    #         "query { getTransfer(filters: {number: 1}) { number, hash } }"
    #     )
    #
    # @task
    # def getTransfers(self):
    #     self.custom_client.send(
    #         "GetTransfers",
    #         "query { getTransfers(pageSize: 10) { objects { number, hash}, pageInfo {pageSize, pageNext, pagePrev} } }"
    #     )
