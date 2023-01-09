import sys, os
from dotenv import load_dotenv

from dataclasses import dataclass


sys.path = ['', '..'] + sys.path[1:]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(BASE_DIR, "..", ".env"))

# Override settings with local or test specific ones if they exist
if os.path.exists(".local.env"):
    load_dotenv(os.path.join(BASE_DIR, "..", ".local.env"))
if os.path.exists(".test.env"):
    load_dotenv(os.path.join(BASE_DIR, "..", ".test.env"))

sys.path.append(BASE_DIR)


@dataclass
class SETTINGS:

    SERVER_ADDR: str = os.environ['SERVER_ADDR']
    SERVER_PORT: str = os.environ['SERVER_PORT']
    HTTP_MOUNT: str = os.environ['HTTP_MOUNT']
    WS_MOUNT: str = os.environ['WS_MOUNT']
    BROADCAST_URI: str = os.environ['BROADCAST_URI']
    WEBSOCKET_URI: str = os.environ['WEBSOCKET_URI']
    CHAIN_ID: str = os.environ['CHAIN_ID']

    TEST_CONNECTION_WAIT_TIME: int = os.environ['TEST_CONNECTION_WAIT_TIME']
    TEST_QUERY_WAIT_TIME: int = os.environ['TEST_QUERY_WAIT_TIME']
    TEST_SUBSCRIPTION_WAIT_TIME: int = os.environ['TEST_SUBSCRIPTION_WAIT_TIME']
    TEST_SUBSCRIPTION_NR_BLOCKS: int = os.environ['TEST_SUBSCRIPTION_WAIT_TIME']

    SUBSCRIBE_NEW_BLOCK_CONNECTIONS: int = os.environ['SUBSCRIBE_NEW_BLOCK_CONNECTIONS']
    SUBSCRIBE_NEW_EVENT_CONNECTIONS: int = os.environ['SUBSCRIBE_NEW_EVENT_CONNECTIONS']
    SUBSCRIBE_NEW_EXTRINSIC_CONNECTIONS: int = os.environ['SUBSCRIBE_NEW_EXTRINSIC_CONNECTIONS']
    SUBSCRIBE_NEW_TRANSFER_CONNECTIONS: int = os.environ['SUBSCRIBE_NEW_TRANSFER_CONNECTIONS']
    SUBSCRIBE_NEW_LOG_CONNECTIONS: int = os.environ['SUBSCRIBE_NEW_LOG_CONNECTIONS']

    GQL_CONNECTION_ACK = "connection_ack"
    GQL_CONNECTION_ERROR = "connection_error"
    GQL_CONNECTION_INIT = "connection_init"
    GQL_CONNECTION_TERMINATE = "connection_terminate"
    GQL_COMPLETE = "complete"
    GQL_DATA = "data"
    GQL_ERROR = "error"
    GQL_START = "start"
    GQL_STOP = "stop"

    def __post_init__(self):
        if self.SUBSCRIBE_NEW_BLOCK_CONNECTIONS is None:
            self.SUBSCRIBE_NEW_BLOCK_CONNECTIONS = 1
        if self.SUBSCRIBE_NEW_EVENT_CONNECTIONS is None:
            self.SUBSCRIBE_NEW_EVENT_CONNECTIONS = 1
        if self.SUBSCRIBE_NEW_EXTRINSIC_CONNECTIONS is None:
            self.SUBSCRIBE_NEW_EXTRINSIC_CONNECTIONS = 1
        if self.SUBSCRIBE_NEW_TRANSFER_CONNECTIONS is None:
            self.SUBSCRIBE_NEW_TRANSFER_CONNECTIONS = 1
        if self.SUBSCRIBE_NEW_LOG_CONNECTIONS is None:
            self.SUBSCRIBE_NEW_LOG_CONNECTIONS = 1
        if self.TEST_SUBSCRIPTION_NR_BLOCKS is None:
            self.TEST_SUBSCRIPTION_NR_BLOCKS = 10


settings = SETTINGS()
