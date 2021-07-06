import graphene

from starlette_graphene3 import GraphQLApp, make_playground_handler
from app import app

from app.api.graphql.queries import GraphQLQueries
from app.api.graphql.subscriptions import Subscription

graphql_app = GraphQLApp(schema=graphene.Schema(query=GraphQLQueries, subscription=Subscription), on_get=make_playground_handler())

app.mount("/graphql", graphql_app)
app.add_websocket_route("/graphql-ws", graphql_app)
