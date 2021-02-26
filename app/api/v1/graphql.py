import graphene

from starlette_graphene3 import GraphQLApp

from app.main import app
from .schemas import BlockSchema, ExtrinsicSchema, ExtrinsicFilter, EventSchema, EventFilter, BlockFilter, BlocksFilter

from ... import broadcast
from ...db import SessionManager
from ...session import SessionLocal

from app.models.harvester import Block
from app.models.harvester import Extrinsic
from app.models.harvester import Event


class GraphQLQueries(graphene.ObjectType):

    get_block = graphene.Field(BlockSchema, filters=BlockFilter())
    get_blocks = graphene.List(BlockSchema, filters=BlocksFilter())
    all_extrinsics = graphene.List(ExtrinsicSchema, filters=ExtrinsicFilter())
    all_events = graphene.List(EventSchema, filters=EventFilter())

    def resolve_get_block(self, info, filters=None):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(Block)
            if filters is not None:
                query = BlockFilter.filter(info, query, filters).one()
            else:
                query = query.order_by(Block.id.desc()).first()

            return query

    def resolve_get_blocks(self, info, filters=None):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(Block)
            if filters is not None:
                query = BlocksFilter.filter(info, query, filters)

            offset = 0 #kwargs.pop('offset', 0)
            limit = 10 #kwargs.pop('limit', 10)

            return query.order_by(Block.id.desc()).offset(offset).limit(limit).all()

    def resolve_all_extrinsics(self, info, filters=None):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(Extrinsic)
            if filters is not None:
                query = ExtrinsicFilter.filter(info, query, filters)

            offset = 0 #kwargs.pop('offset', 0)
            limit = 10 #kwargs.pop('limit', 10)

            return query.order_by(Extrinsic.id.desc()).offset(offset).limit(limit).all()

    def resolve_all_events(self, info, filters=None):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(Event)
            if filters is not None:
                query = EventFilter.filter(info, query, filters)

            offset = 0 #kwargs.pop('offset', 0)
            limit = 10 #kwargs.pop('limit', 10)

            return query.order_by(Event.id.desc()).offset(offset).limit(limit).all()


class Subscription(graphene.ObjectType):
    subscribe_block = graphene.List(BlockSchema)

    async def subscribe_subscribe_block(root, info):
        async with broadcast.subscribe(channel="blocks") as subscriber:
            async for event in subscriber:
                if event.message:
                    with SessionManager(session_cls=SessionLocal) as session:
                        query = session.query(Block)
                        query = query.filter(Block.id > int(event.message))
                        query = query.order_by(Block.id.desc()).offset(0).limit(10)
                        items = query.all()
                        if items:
                            yield items


graphql_app = GraphQLApp(schema=graphene.Schema(query=GraphQLQueries, subscription=Subscription))
app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql-ws", graphql_app)
