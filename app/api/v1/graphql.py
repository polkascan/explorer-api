import graphene

from starlette_graphene3 import GraphQLApp

from app.main import app
from .schemas import BlockSchema, ExtrinsicFilter, EventFilter, BlockFilter, \
    BlocksFilter, BlockPaginatedType, ExtrinsicsPaginatedType, EventPaginatedType

from ... import broadcast, settings
from ...db import SessionManager
from ...session import SessionLocal

from app.models.harvester import Block
from app.models.harvester import Extrinsic
from app.models.harvester import Event


class GraphQLQueries(graphene.ObjectType):

    get_block = graphene.Field(BlockSchema, filters=BlockFilter())
    get_blocks = graphene.Field(BlockPaginatedType, filters=BlocksFilter(), page_key=graphene.String(), page_size=graphene.Int())
    all_extrinsics = graphene.Field(ExtrinsicsPaginatedType, filters=ExtrinsicFilter(), page_key=graphene.String(), page_size=graphene.Int())
    all_events = graphene.List(EventPaginatedType, filters=EventFilter(), page_key=graphene.String(), page_size=graphene.Int())

    def resolve_get_block(self, info, filters=None):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(Block)
            if filters is not None:
                query = BlockFilter.filter(info, query, filters).one()
            else:
                query = query.order_by(Block.id.desc()).first()

            return query

    def resolve_get_blocks(self, info, filters=None, page_key=None, page_size=settings.DEFAULT_PAGE_SIZE):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(Block)
            if filters is not None:
                query = BlocksFilter.filter(info, query, filters)

            return BlockPaginatedType.create_paginated_result(query.order_by(Block.id.desc()), page_key, page_size)

    def resolve_all_extrinsics(self, info, filters=None, page_key=graphene.String(), page_size=settings.DEFAULT_PAGE_SIZE):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(Extrinsic)
            if filters is not None:
                query = ExtrinsicFilter.filter(info, query, filters)

            return ExtrinsicsPaginatedType.create_paginated_result(query.order_by(Extrinsic.id.desc()), page_key, page_size)

    def resolve_all_events(self, info, filters=None, page_key=graphene.String(), page_size=settings.DEFAULT_PAGE_SIZE):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(Event)
            if filters is not None:
                query = EventFilter.filter(info, query, filters)

            return EventPaginatedType.create_paginated_result(query.order_by(Event.id.desc()), page_key, page_size)


class Subscription(graphene.ObjectType):
    subscribe_new_block = graphene.Field(BlockSchema)

    async def subscribe_subscribe_new_block(root, info):
        async with broadcast.subscribe(channel="blocks") as subscriber:
            async for event in subscriber:
                if event.message:
                    with SessionManager(session_cls=SessionLocal) as session:
                        query = session.query(Block)
                        query = query.filter(Block.id == int(event.message))
                        item = query.one_or_none()
                        if item:
                            yield item


graphql_app = GraphQLApp(schema=graphene.Schema(query=GraphQLQueries, subscription=Subscription))
app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql-ws", graphql_app)
