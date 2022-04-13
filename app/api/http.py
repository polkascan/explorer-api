from fastapi import Depends
from sqlalchemy.orm import Session

from typing import Any
from fastapi.responses import HTMLResponse

from app import settings
from app.main import app
from app.db import get_db
from app.models.explorer import Block


@app.get("/test/ping")
def test_ping() -> Any:
    return {"result": "OK"}


@app.get("/test/db")
def test_db(db: Session = Depends(get_db)) -> Any:
    item = db.query(Block).first()
    return {"result": "OK", "id": item.hash}


@app.get("/test/sentry")
def test_sentry() -> Any:
    raise Exception("TEST ERROR")


@app.get("/test/version")
def test_version() -> Any:
    import gitcommit
    return {"datetime": gitcommit.date, "prev_commit": gitcommit.prev_commit, "branch": gitcommit.branch  or "master"}


@app.get("/test/ws")
def test_websocket() -> Any:
    import gitcommit
    ws_html = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>GraphQL</title>
        </head>
        <body>
            <h1>WebSocket test</h1>
            <h4>Commit dt: {gitcommit.date}</h4>
            <h4>Prev commit: {gitcommit.prev_commit}</h4>
            <h4>Branch: {gitcommit.branch or 'master'}</h4>
            <textarea type="textarea" id="query-text" rows="4" cols="50">query {{ getLatestBlock {{ number, hash }} }}</textarea>
            <button onclick="sendQuery()">Query</button>
            <button onclick="subscribeBlocks()">Subscribe new blocks</button>
            <button onclick="subscribeEvents()">Subscribe new events</button>
            <button onclick="subscribeExtrinsics()">Subscribe new extrinsics</button>
            <button onclick="subscribeTransfer()">Subscribe new transfers</button>
            <button onclick="subscribeLog()">Subscribe new logs</button>
            <ul id='messages'>
            </ul>
            <script>
                var GQL_CONNECTION_ACK = "connection_ack";
                var GQL_CONNECTION_ERROR = "connection_error";
                var GQL_CONNECTION_INIT = "connection_init";
                var GQL_CONNECTION_TERMINATE = "connection_terminate";
                var GQL_COMPLETE = "complete";
                var GQL_DATA = "data";
                var GQL_ERROR = "error";
                var GQL_START = "start";
                var GQL_STOP = "stop";

                var ws = new WebSocket(\"""" + settings.WEBSOCKET_URI + """/graphql-ws", "graphql-ws");

                ws.onopen = function(event) {
                    ws.send('{"type": "' + GQL_CONNECTION_INIT+ '" }')
                }
                ws.onmessage = function(event) {
                    console.log("WS: received msg: ", event);
                    let data = JSON.parse(event.data);
                    if (data.type === 'connection_ack') {
                        console.log("WS: connection_ack");
                    }
                    else if (data.type === 'data') { 
                        console.log('WS: received data: ', data.payload); 
                    }
                    else { 
                        console.log('WS: received message type: ', data) 
                    }
                };

                function sendQuery() {
                    let q = document.getElementById("query-text"); 
                    console.log("sending query: ", q.value);
                    payload = {
                        "type": GQL_START,
                        "id": "test",
                        "payload": {
                            "query": q.value,
                            "operationName": null,
                        },
                    };
                    ws.send(JSON.stringify(payload));
                }
                function subscribeBlocks() {
                    payload = {
                        "type": GQL_START,
                        "id": "sub_blocks",
                        "payload": {
                            "query": "subscription { subscribeNewBlock {number, hash} }",
                            "operationName": null,
                        },
                    };
                    ws.send(JSON.stringify(payload));
                }
                function subscribeEvents() {
                    payload = {
                        "type": GQL_START,
                        "id": "sub_events",
                        "payload": {
                            "query": "subscription { subscribeNewEvent {blockNumber, eventIdx, event} }",
                            "operationName": null,
                        },
                    };
                    ws.send(JSON.stringify(payload));
                }
                function subscribeExtrinsics() {
                    payload = {
                        "type": GQL_START,
                        "id": "sub_events",
                        "payload": {
                            "query": "subscription { subscribeNewExtrinsic {blockNumber, extrinsicIdx, hash} }",
                            "operationName": null,
                        },
                    };
                    ws.send(JSON.stringify(payload));
                }
                function subscribeTransfer() {
                    payload = {
                        "type": GQL_START,
                        "id": "sub_transfer",
                        "payload": {
                            "query": "subscription { subscribeNewTransfer {blockNumber, eventIdx, blockDatetime, fromMultiAddressAccountId, toMultiAddressAccountId} }",
                            "operationName": null,
                        },
                    };
                    ws.send(JSON.stringify(payload));
                }

                function subscribeLog() {
                    payload = {
                        "type": GQL_START,
                        "id": "sub_log",
                        "payload": {
                            "query": "subscription { subscribeNewLog {blockNumber, logIdx} }",
                            "operationName": null,
                        },
                    };
                    ws.send(JSON.stringify(payload));
                } 
            </script>
        </body>
    </html>
    """
    return HTMLResponse(ws_html)
