import graphene
from graphql import GraphQLError

from app import settings
from app.api.graphql.filters import BlockFilter, BlocksFilter, EventFilter, ExtrinsicFilter, EventsFilter
from app.api.graphql.pagination import BlockPaginatedType, ExtrinsicsPaginatedType, EventPaginatedType
from app.api.graphql.schemas import BlockSchema, EventSchema, ExtrinsicSchema
from app.db import SessionManager
from app.models.explorer import Block, Extrinsic, Event
from app.session import SessionLocal


class GraphQLQueries(graphene.ObjectType):

    get_block = graphene.Field(BlockSchema, filters=BlockFilter())
    get_blocks = graphene.Field(BlockPaginatedType, filters=BlocksFilter(), page_key=graphene.String(), page_size=graphene.Int())
    get_extrinsic = graphene.Field(ExtrinsicSchema, filters=ExtrinsicFilter())
    get_extrinsics = graphene.Field(ExtrinsicsPaginatedType, filters=ExtrinsicFilter(), page_key=graphene.String(), page_size=graphene.Int())
    get_event = graphene.Field(EventSchema, filters=EventFilter())
    get_events = graphene.Field(EventPaginatedType, filters=EventsFilter(), page_key=graphene.String(), page_size=graphene.Int())

    def resolve_get_block(self, info, filters=None):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(Block)
            if filters is not None:
                query = BlockFilter.filter(info, query, filters).one()
            else:
                query = query.order_by(Block.number.desc()).first()

            return query

    def resolve_get_blocks(self, info, filters=None, page_key=None, page_size=settings.DEFAULT_PAGE_SIZE):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(Block)
            if filters is not None:
                query = BlocksFilter.filter(info, query, filters)
            return BlockPaginatedType.create_paginated_result(query.order_by(Block.number.desc()), page_key, page_size)

    def resolve_get_extrinsics(self, info, filters=None, page_key=graphene.String(), page_size=settings.DEFAULT_PAGE_SIZE):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(Extrinsic)
            if filters is not None:
                query = ExtrinsicFilter.filter(info, query, filters)

            return ExtrinsicsPaginatedType.create_paginated_result(query.order_by(Extrinsic.block_number.desc()), page_key, page_size)

    def resolve_get_event(self, info, filters=None):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(Event)
            if filters is not None:
                if (filters.get("block_number", None) or filters.get("event_idx", None)) and not (filters.get("block_number", None) and filters.get("event_idx", None)):
                    raise GraphQLError('Both block_number and event_idx must be specified when filtering an event')

                query = EventFilter.filter(info, query, filters).one()
            else:
                query = query.order_by(Event.block_number.desc(), Event.event_idx.desc()).first()

            return query

    def resolve_get_events(self, info, filters=None, page_key=graphene.String(), page_size=settings.DEFAULT_PAGE_SIZE):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(Event)
            if filters is not None:
                query = EventsFilter.filter(info, query, filters)

            return EventPaginatedType.create_paginated_result(query.order_by(Event.block_number.desc()), page_key, page_size)
