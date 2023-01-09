import graphene

from app import settings, broadcast
from app.db import SessionManager
from app.models.runtime import CodecEventIndexAccount
from app.session import SessionLocal
from app.models.explorer import Block, Event, Extrinsic, Log

from app.api.graphql.filters import ExtrinsicFilter, EventsFilter, CodecEventIndexAccountFilter
from app.api.graphql.schemas import ExtrinsicSchema

from scalecodec.utils.ss58 import ss58_decode

from graphene_sqlalchemy_filter import FilterSet
from graphene_sqlalchemy import SQLAlchemyObjectType


class BlockSchema(SQLAlchemyObjectType):
    number = graphene.Int()

    class Meta:
        model = Block


class EventSchema(SQLAlchemyObjectType):
    block_number = graphene.Int()
    event_idx = graphene.Int()

    class Meta:
        model = Event


class EventIndexAccountSchema(SQLAlchemyObjectType):
    block_number = graphene.Int()
    event_idx = graphene.Int()
    attribute_name = graphene.String()

    class Meta:
        model = CodecEventIndexAccount


class LogSchema(SQLAlchemyObjectType):
    block_number = graphene.Int()
    log_idx = graphene.Int()

    class Meta:
        model = Log


class LogFilter(FilterSet):
    class Meta:
        model = Log
        fields = {
            'block_number':  ['eq',],
            'log_idx':  ['eq',],
            'type_id':  ['eq',],
            'block_datetime': ['eq', 'gt', 'lt', 'gte', 'lte'],
        }


class Subscription(graphene.ObjectType):
    subscribe_new_block = graphene.Field(BlockSchema)
    subscribe_new_event = graphene.Field(EventSchema, filters=EventsFilter())
    subscribe_new_extrinsic = graphene.Field(ExtrinsicSchema, filters=ExtrinsicFilter())
    subscribe_new_log = graphene.Field(LogSchema, filters=LogFilter())
    subscribe_new_event_by_account = graphene.Field(EventIndexAccountSchema, filters=CodecEventIndexAccountFilter())

    async def subscribe_subscribe_new_block(root, info):
        with SessionManager(session_cls=SessionLocal) as session:
            latest_block = session.query(Block).order_by(Block.number.desc()).first()
            if latest_block:
                yield latest_block

        async with broadcast.subscribe(channel=f"{settings.CHAIN_ID}-last-block") as subscriber:
            async for event in subscriber:
                if event.message:
                    with SessionManager(session_cls=SessionLocal) as session:
                        block_nrs = event.message.split(",")
                        block_nrs = block_nrs[-100:] # Sanity precaution
                        query = session.query(Block).filter(Block.number.in_(block_nrs))
                        for item in query:
                            yield item

    async def subscribe_subscribe_new_event(root, info, filters=None):
        with SessionManager(session_cls=SessionLocal) as session:
            latest_events = session.query(Event).order_by(Event.block_number.desc(), Event.event_idx.desc())
            if filters is not None:
                latest_events = EventsFilter.filter(info, latest_events, filters)

            latest_event = latest_events.first()
            if latest_event:
                yield latest_event

        async with broadcast.subscribe(channel=f"{settings.CHAIN_ID}-last-block") as subscriber:
            async for event in subscriber:
                if event.message:
                    with SessionManager(session_cls=SessionLocal) as session:
                        event_records = event.message.split(",")
                        event_records = event_records[-100:] # Sanity precaution
                        query = session.query(Event).filter(Event.block_number.in_(event_records))

                        if filters is not None:
                            query = EventsFilter.filter(info, query, filters)

                        for item in query.order_by(Event.block_number, Event.event_idx):
                            yield item

    async def subscribe_subscribe_new_extrinsic(root, info, filters=None):
        with SessionManager(session_cls=SessionLocal) as session:
            latest_extrinsics = session.query(Extrinsic).order_by(Extrinsic.block_number.desc(), Extrinsic.extrinsic_idx.desc())
            if filters is not None:
                latest_extrinsics = ExtrinsicFilter.filter(info, latest_extrinsics, filters)
            latest_extrinsic = latest_extrinsics.first()
            if latest_extrinsic:
                yield latest_extrinsic

        async with broadcast.subscribe(channel=f"{settings.CHAIN_ID}-last-block") as subscriber:
            async for event in subscriber:
                if event.message:
                    with SessionManager(session_cls=SessionLocal) as session:
                        extrinsic_records = event.message.split(",")
                        extrinsic_records = extrinsic_records[-100:] # Sanity precaution
                        query = session.query(Extrinsic).filter(Extrinsic.block_number.in_(extrinsic_records))

                        if filters is not None:
                            query = ExtrinsicFilter.filter(info, query, filters)

                        for item in query.order_by(Extrinsic.block_number, Extrinsic.extrinsic_idx):
                            yield item

    async def subscribe_subscribe_new_log(root, info, filters=None):

        with SessionManager(session_cls=SessionLocal) as session:
            latest_log = session.query(Log).order_by(Log.block_number.desc(), Log.log_idx.desc())
            if filters is not None:
                latest_log = LogFilter.filter(info, latest_log, filters)
            latest_log = latest_log.first()
            if latest_log:
                yield latest_log

        async with broadcast.subscribe(channel=f"{settings.CHAIN_ID}-last-block") as subscriber:
            async for event in subscriber:
                if event.message:
                    with SessionManager(session_cls=SessionLocal) as session:
                        log_records = event.message.split(",")
                        log_records = log_records[-100:] # Sanity precaution
                        query = session.query(Log).filter(Log.block_number.in_(log_records))

                        if filters is not None:
                            query = LogFilter.filter(info, query, filters)

                        for item in query.order_by(Log.block_number, Log.log_idx):
                            yield item


    async def subscribe_subscribe_new_event_by_account(root, info, filters=None):
        with SessionManager(session_cls=SessionLocal) as session:
            latest_events = session.query(CodecEventIndexAccount).order_by(CodecEventIndexAccount.block_number.desc(), CodecEventIndexAccount.event_idx.desc())
            if filters is not None:
                latest_events = CodecEventIndexAccountFilter.filter(info, latest_events, filters)

            latest_event = latest_events.first()
            if latest_event:
                yield latest_event

        async with broadcast.subscribe(channel=f"{settings.CHAIN_ID}-last-block") as subscriber:
            async for event in subscriber:
                if event.message:
                    with SessionManager(session_cls=SessionLocal) as session:
                        event_records = event.message.split(",")
                        event_records = event_records[-100:] # Sanity precaution
                        query = session.query(CodecEventIndexAccount).filter(CodecEventIndexAccount.block_number.in_(event_records))

                        if filters is not None:
                            query = CodecEventIndexAccountFilter.filter(info, query, filters)

                        for item in query.order_by(CodecEventIndexAccount.block_number, CodecEventIndexAccount.event_idx):
                            yield item