import graphene

from app import settings, broadcast
from app.db import SessionManager
from app.session import SessionLocal
from app.models.explorer import Block, Event, Extrinsic

from app.api.graphql.filters import EventFilter, EventsFilter, ExtrinsicFilter
from app.api.graphql.schemas import BlockSchema, EventSchema, ExtrinsicSchema


class Subscription(graphene.ObjectType):
    subscribe_new_block = graphene.Field(BlockSchema)
    subscribe_new_event = graphene.Field(EventSchema, filters=EventsFilter())
    subscribe_new_extrinsic = graphene.Field(ExtrinsicSchema, filters=ExtrinsicFilter())

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
            latest_event = session.query(Event).order_by(Event.block_number.desc(), Event.event_idx.desc()).first()
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
                            query = EventFilter.filter(info, query, filters)

                        for item in query.order_by(Event.block_number, Event.event_idx):
                            yield item

    async def subscribe_subscribe_new_extrinsic(root, info, filters=None):
        with SessionManager(session_cls=SessionLocal) as session:
            latest_extrinsic = session.query(Extrinsic).order_by(Extrinsic.block_number.desc(), Extrinsic.extrinsic_idx.desc()).first()
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
                            query = EventFilter.filter(info, query, filters)

                        for item in query.order_by(Extrinsic.block_number, Extrinsic.extrinsic_idx):
                            yield item
