from fastapi import Depends
from sqlalchemy.orm import Session

from typing import Any
from fastapi.responses import HTMLResponse

from app import settings
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

#
# @app.get("/test/blockie/{block_id}")
# def test_db(block_id, db: Session = Depends(get_db)) -> Any:
#     from app.models.harvester import Block, BlockTotal
#     b = Block(
#         id=block_id,
#         parent_id=0,
#         hash=block_id,
#         parent_hash=block_id,
#         state_root=block_id,
#         extrinsics_root=block_id,
#         count_extrinsics=1,
#         count_extrinsics_unsigned=1,
#         count_extrinsics_signed=1,
#         count_extrinsics_error=1,
#         count_extrinsics_success=1,
#         count_extrinsics_signedby_address=1,
#         count_extrinsics_signedby_index=1,
#         count_events=1,
#         count_events_system=1,
#         count_events_module=1,
#         count_events_extrinsic=1,
#         count_events_finalization=1,
#         count_accounts=1,
#         count_accounts_new=1,
#         count_accounts_reaped =1,
#         count_sessions_new=1,
#         count_contracts_new =1,
#         count_log=1,
#         range10000=1,
#         range100000=1,
#         range1000000=1,
#         spec_version_id ="123"
#     )
#     bt = BlockTotal(
#         id=block_id,
#         session_id=1,
#         blocktime=1,
#         total_extrinsics=1,
#         total_extrinsics_success=1,
#         total_extrinsics_error=1,
#         total_extrinsics_signed=1,
#         total_extrinsics_unsigned=1,
#         total_extrinsics_signedby_address=1,
#         total_extrinsics_signedby_index=1,
#         total_events=1,
#         total_events_system=1,
#         total_events_module=1,
#         total_events_extrinsic=1,
#         total_events_finalization=1,
#         total_logs=1,
#         total_blocktime =1,
#         total_accounts=1,
#         total_accounts_new =1,
#         total_accounts_reaped=1,
#         total_sessions_new=1,
#         total_contracts_new=1
#     )
#     db.add(b)
#     db.add(bt)
#     db.commit()
#     return {"result": "OK", "block_id": b.id, "block_total_id": bt.id}


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
        <textarea type="textarea" id="query-text" rows="4" cols="50">query { getBlocks(filters: {idGte: 100}) { id, hash } }</textarea>
        <button onclick="sendQuery()">Send</button>
        <button onclick="subscribe()">Subscribe</button>
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
            function subscribe() {
                payload = {
                    "type": GQL_START,
                    "id": "q1",
                    "payload": {
                        "query": "subscription { subscribeBlock {id, hash} }",
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
