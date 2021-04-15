import graphene

from starlette_graphene3 import GraphQLApp
from app import app

from app.api.graphql.queries import GraphQLQueries
from app.api.graphql.subscriptions import Subscription

graphql_app = GraphQLApp(schema=graphene.Schema(query=GraphQLQueries, subscription=Subscription))
app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql-ws", graphql_app)
