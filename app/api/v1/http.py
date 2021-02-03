from fastapi import Depends
from sqlalchemy.orm import Session

from typing import Any
from fastapi.responses import HTMLResponse

from app.main import app
from app.db import get_db
from app.models.harvester import Block


@app.get("/test/ping")
def test_ping() -> Any:
    return {"result": "OK"}


@app.get("/test/db")
def test_db(db: Session = Depends(get_db)) -> Any:
    item = db.query(Block).first()
    return {"result": "OK", "id": item.id}


@app.get("/test/sentry")
def test_sentry() -> Any:
    raise Exception("TEST ERROR")


ws_html = """
<!DOCTYPE html>
<html>
    <head>
        <title>GraphQL </title>
    </head>
    <body>
        <h1>WebSocket test</h1>
        <textarea type="textarea" id="query-text" rows="4" cols="50">query allBlockies { allBlocks { id, hash } }</textarea>
        <button onclick="sendQuery()">Send</button>
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

            var ws = new WebSocket("ws://127.0.0.1:8000/graphql-ws", "graphql-ws");

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
        </script>
    </body>
</html>
"""


@app.get("/test/ws")
def test_websocket() -> Any:
    return HTMLResponse(ws_html)
