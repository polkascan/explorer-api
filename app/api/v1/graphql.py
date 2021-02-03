import graphene
from starlette_graphene3 import GraphQLApp

from app.main import app
from .schemas import BlockSchema, ExtrinsicSchema, ExtrinsicFilter, EventSchema, EventFilter, BlockFilter


class GraphQLQueries(graphene.ObjectType):

    all_blocks = graphene.List(BlockSchema, filters=ExtrinsicFilter())
    all_extrinsics = graphene.List(ExtrinsicSchema, filters=ExtrinsicFilter())
    all_events = graphene.List(EventSchema, filters=EventFilter())

    def resolve_all_blocks(self, info, filters=None):
        from app.models.harvester import Block
        query = Block.query
        if filters is not None:
            query = BlockFilter.filter(info, query, filters)

        offset = 0 #kwargs.pop('offset', 0)
        limit = 10 #kwargs.pop('limit', 10)

        return query.offset(offset).limit(limit).all()

    def resolve_all_extrinsics(self, info, filters=None):
        from app.models.harvester import Extrinsic
        query = Extrinsic.query
        if filters is not None:
            query = ExtrinsicFilter.filter(info, query, filters)

        offset = 0 #kwargs.pop('offset', 0)
        limit = 10 #kwargs.pop('limit', 10)

        return query.offset(offset).limit(limit).all()

    def resolve_all_events(self, info, filters=None):
        from app.models.harvester import Event
        query = Event.query
        if filters is not None:
            query = EventFilter.filter(info, query, filters)

        offset = 0 #kwargs.pop('offset', 0)
        limit = 10 #kwargs.pop('limit', 10)

        return query.offset(offset).limit(limit).all()


graphql_app = GraphQLApp(schema=graphene.Schema(query=GraphQLQueries))
app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql-ws", graphql_app)
