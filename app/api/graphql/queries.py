import graphene
from graphql import GraphQLError

from app import settings
from app.api.graphql.filters import BlockFilter, BlocksFilter, EventFilter, ExtrinsicFilter, EventsFilter, \
    RuntimeFilter, RuntimeCallFilter, RuntimeCallArgumentFilter, RuntimeConstantFilter, RuntimeErrorMessageFilter, \
    RuntimeEventFilter, RuntimeEventAttributeFilter, RuntimePalletFilter, RuntimeStorageFilter, RuntimeTypeFilter
from app.api.graphql.pagination import CreatePaginatedType
from app.api.graphql.schemas import BlockSchema, EventSchema, ExtrinsicSchema, RuntimeSchema, RuntimeCallSchema, \
    RuntimeCallArgumentSchema, RuntimeConstantSchema, RuntimeErrorMessageSchema, RuntimeEventSchema, \
    RuntimeEventAttributeSchema, RuntimePalletSchema, RuntimeStorageSchema, RuntimeTypeSchema
from app.db import SessionManager
from app.models.explorer import Block, Extrinsic, Event
from app.models.runtime import Runtime, RuntimeCall, RuntimeCallArgument, RuntimeConstant, RuntimeErrorMessage, \
    RuntimeEvent, RuntimeEventAttribute, RuntimePallet, RuntimeStorage, RuntimeType
from app.session import SessionLocal


paginated_blocks = CreatePaginatedType(BlockSchema)
paginated_extrinsic = CreatePaginatedType(ExtrinsicSchema)
paginated_event = CreatePaginatedType(EventSchema)
paginated_runtime = CreatePaginatedType(RuntimeSchema)
paginated_runtime_call = CreatePaginatedType(RuntimeCallSchema)
paginated_runtime_call_argument = CreatePaginatedType(RuntimeCallArgumentSchema)
paginated_runtime_constant = CreatePaginatedType(RuntimeConstantSchema)
paginated_runtime_error_message = CreatePaginatedType(RuntimeErrorMessageSchema)
paginated_runtime_event = CreatePaginatedType(RuntimeEventSchema)
paginated_runtime_event_attribute = CreatePaginatedType(RuntimeEventAttributeSchema)
paginated_runtime_pallet = CreatePaginatedType(RuntimePalletSchema)
paginated_runtime_storage = CreatePaginatedType(RuntimeStorageSchema)
paginated_runtime_type = CreatePaginatedType(RuntimeTypeSchema)


class GraphQLQueries(graphene.ObjectType):

    get_latest_block = graphene.Field(BlockSchema)
    get_block = graphene.Field(BlockSchema, filters=BlockFilter())
    get_blocks = graphene.Field(paginated_blocks, filters=BlocksFilter(), page_key=graphene.String(), page_size=graphene.Int())
    get_extrinsic = graphene.Field(ExtrinsicSchema, filters=ExtrinsicFilter())
    get_extrinsics = graphene.Field(paginated_event, filters=ExtrinsicFilter(), page_key=graphene.String(), page_size=graphene.Int())
    get_event = graphene.Field(EventSchema, filters=EventFilter())
    get_events = graphene.Field(paginated_event, filters=EventsFilter(), page_key=graphene.String(), page_size=graphene.Int())

    get_runtime = graphene.Field(RuntimeSchema, filters=RuntimeFilter())
    get_latest_runtime = graphene.Field(RuntimeSchema)
    get_runtimes = graphene.Field(paginated_runtime, filters=RuntimeFilter(), page_key=graphene.String(), page_size=graphene.Int())
    get_runtime_calls = graphene.Field(paginated_runtime_call, filters=RuntimeCallFilter(), page_key=graphene.String(), page_size=graphene.Int())
    get_runtime_call = graphene.Field(RuntimeCallSchema, filters=RuntimeCallFilter())
    get_runtime_call_arguments = graphene.Field(paginated_runtime_call_argument, filters=RuntimeCallArgumentFilter(), page_key=graphene.String(), page_size=graphene.Int())
    get_runtime_call_argument = graphene.Field(RuntimeCallArgumentSchema, filters=RuntimeCallArgumentFilter())
    get_runtime_constants = graphene.Field(paginated_runtime_constant, filters=RuntimeConstantFilter(), page_key=graphene.String(), page_size=graphene.Int())
    get_runtime_constant = graphene.Field(RuntimeConstantSchema, filters=RuntimeConstantFilter())
    get_runtime_error_messages = graphene.Field(paginated_runtime_error_message, filters=RuntimeErrorMessageFilter())
    get_runtime_error_message = graphene.Field(RuntimeErrorMessageSchema, filters=RuntimeErrorMessageFilter())
    get_runtime_events = graphene.Field(paginated_runtime_event, filters=RuntimeEventFilter(), page_key=graphene.String(), page_size=graphene.Int())
    get_runtime_event = graphene.Field(RuntimeEventSchema, filters=RuntimeEventFilter())
    get_runtime_event_attributes = graphene.Field(paginated_runtime_event_attribute, filters=RuntimeEventAttributeFilter(), page_key=graphene.String(), page_size=graphene.Int())
    get_runtime_pallets = graphene.Field(paginated_runtime_pallet, filters=RuntimePalletFilter(), page_key=graphene.String(), page_size=graphene.Int())
    get_runtime_pallet = graphene.Field(RuntimePalletSchema, filters=RuntimePalletFilter())
    get_runtime_storages = graphene.Field(paginated_runtime_storage, filters=RuntimeStorageFilter(), page_key=graphene.String(), page_size=graphene.Int())
    get_runtime_storage = graphene.Field(RuntimeStorageSchema, filters=RuntimeStorageFilter())
    get_runtime_types = graphene.Field(paginated_runtime_type, filters=RuntimeTypeFilter(), page_key=graphene.String(), page_size=graphene.Int())
    get_runtime_type = graphene.Field(RuntimeTypeSchema, filters=RuntimeTypeFilter())

    def resolve_get_latest_block(self, info, filters=None):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(Block)
            return query.order_by(Block.number.desc()).first()

    def resolve_get_block(self, info, filters=None):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(Block)
            query = BlockFilter.filter(info, query, filters).one()
            return query

    def resolve_get_blocks(self, info, filters=None, page_key=None, page_size=settings.DEFAULT_PAGE_SIZE):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(Block)
            if filters is not None:
                query = BlocksFilter.filter(info, query, filters)
            return paginated_blocks.create_paginated_result(query.order_by(Block.number.desc()), page_key, page_size)

    def resolve_get_extrinsic(self, info, filters=None):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(Extrinsic)
            if filters is not None:
                query = ExtrinsicFilter.filter(info, query, filters).one()
            else:
                query = query.order_by(Extrinsic.block_number.desc()).first()

            return query

    def resolve_get_extrinsics(self, info, filters=None, page_key=graphene.String(), page_size=settings.DEFAULT_PAGE_SIZE):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(Extrinsic)
            if filters is not None:
                query = ExtrinsicFilter.filter(info, query, filters)

            return paginated_extrinsic.create_paginated_result(query.order_by(Extrinsic.block_number.desc()), page_key, page_size)

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

            return paginated_event.create_paginated_result(query.order_by(Event.block_number.desc()), page_key, page_size)


    ################RUNTIME QUERIES####################################

    def resolve_get_runtime(self, info, filters):
        if not filters or not ("specName" not in filters and "specVersion" not in filters):
            raise GraphQLError("both specName and specVersion are required")

        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(Runtime)
            query = RuntimeFilter.filter(info, query, filters)
            return query.order_by(Runtime.spec_version.desc()).one()

    def resolve_get_latest_runtime(self, info, filters=None):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(Runtime)
            query = RuntimeFilter.filter(info, query, filters)
            return query.order_by(Runtime.spec_version.desc()).first()

    def resolve_get_runtimes(self, info, filters=None, page_key=graphene.String(), page_size=settings.DEFAULT_PAGE_SIZE):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(Runtime)
            if filters is not None:
                query = RuntimeFilter.filter(info, query, filters)

            return paginated_runtime.create_paginated_result(query.order_by(Runtime.spec_version.desc()), page_key, page_size)

    def resolve_get_runtime_calls(self, info, filters=None, page_key=graphene.String(), page_size=settings.DEFAULT_PAGE_SIZE):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(RuntimeCall)
            if filters is not None:
                query = RuntimeCallFilter.filter(info, query, filters)

            return paginated_runtime_call.create_paginated_result(query.order_by(RuntimeCall.spec_version.desc()), page_key, page_size)

    def resolve_get_runtime_call(self, info, filters=None):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(RuntimeCall)
            query = RuntimeCallFilter.filter(info, query, filters)
            return query.order_by(RuntimeCall.spec_version.desc()).one()

    def resolve_get_runtime_call_arguments(self, info, filters=None, page_key=graphene.String(), page_size=settings.DEFAULT_PAGE_SIZE):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(RuntimeCallArgument)
            if filters is not None:
                query = RuntimeCallArgumentFilter.filter(info, query, filters)

            return paginated_runtime_call_argument.create_paginated_result(query.order_by(RuntimeCallArgument.spec_version.desc()), page_key, page_size)

    def resolve_get_runtime_call_argument(self, info, filters=None):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(RuntimeCallArgument)
            query = RuntimeCallArgumentFilter.filter(info, query, filters)
            return query.order_by(RuntimeCallArgument.spec_version.desc()).one()

    def resolve_get_runtime_constants(self, info, filters=None, page_key=graphene.String(), page_size=settings.DEFAULT_PAGE_SIZE):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(RuntimeConstant)
            if filters is not None:
                query = RuntimeConstantFilter.filter(info, query, filters)

            return paginated_runtime_constant.create_paginated_result(query.order_by(RuntimeConstant.spec_version.desc()), page_key, page_size)

    def resolve_get_runtime_constant(self, info, filters=None):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(RuntimeConstant)
            query = RuntimeConstantFilter.filter(info, query, filters)
            return query.order_by(RuntimeConstant.spec_version.desc()).one()

    def resolve_get_runtime_error_messages(self, info, filters=None, page_key=graphene.String(), page_size=settings.DEFAULT_PAGE_SIZE):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(RuntimeErrorMessage)
            if filters is not None:
                query = RuntimeErrorMessageFilter.filter(info, query, filters)

            return paginated_runtime_error_message.create_paginated_result(query.order_by(RuntimeErrorMessage.spec_version.desc()), page_key, page_size)

    def resolve_get_runtime_error_message(self, info, filters=None):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(RuntimeErrorMessage)
            query = RuntimeErrorMessageFilter.filter(info, query, filters)
            return query.order_by(RuntimeErrorMessage.spec_version.desc()).one()

    def resolve_get_runtime_events(self, info, filters=None, page_key=graphene.String(), page_size=settings.DEFAULT_PAGE_SIZE):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(RuntimeEvent)
            if filters is not None:
                query = RuntimeEventFilter.filter(info, query, filters)

            return paginated_runtime_event.create_paginated_result(query.order_by(RuntimeEvent.spec_version.desc()), page_key, page_size)

    def resolve_get_runtime_event(self, info, filters=None):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(RuntimeEvent)
            query = RuntimeEventFilter.filter(info, query, filters)
            return query.order_by(RuntimeEvent.spec_version.desc()).one()

    def resolve_get_runtime_event_attributes(self, info, filters=None, page_key=graphene.String(), page_size=settings.DEFAULT_PAGE_SIZE):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(RuntimeEventAttribute)
            if filters is not None:
                query = RuntimeEventAttributeFilter.filter(info, query, filters)

            return paginated_runtime_event_attribute.create_paginated_result(query.order_by(RuntimeEventAttribute.spec_version.desc()), page_key, page_size)

    def resolve_get_runtime_pallets(self, info, filters=None, page_key=graphene.String(), page_size=settings.DEFAULT_PAGE_SIZE):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(RuntimePallet)
            if filters is not None:
                query = RuntimePalletFilter.filter(info, query, filters)

            return paginated_runtime_pallet.create_paginated_result(query.order_by(RuntimePallet.spec_version.desc()), page_key, page_size)

    def resolve_get_runtime_pallet(self, info, filters=None):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(RuntimePallet)
            query = RuntimePalletFilter.filter(info, query, filters)
            return query.order_by(RuntimePallet.spec_version.desc()).one()

    def resolve_get_runtime_storages(self, info, filters=None, page_key=graphene.String(), page_size=settings.DEFAULT_PAGE_SIZE):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(RuntimeStorage)
            if filters is not None:
                query = RuntimeStorageFilter.filter(info, query, filters)

            return paginated_runtime_storage.create_paginated_result(query.order_by(RuntimeStorage.spec_version.desc()), page_key, page_size)

    def resolve_get_runtime_storage(self, info, filters=None):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(RuntimeStorage)
            query = RuntimeStorageFilter.filter(info, query, filters)
            return query.order_by(RuntimeStorage.spec_version.desc()).one()

    def resolve_get_runtime_types(self, info, filters=None, page_key=graphene.String(), page_size=settings.DEFAULT_PAGE_SIZE):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(RuntimeType)
            if filters is not None:
                query = RuntimeTypeFilter.filter(info, query, filters)

            return paginated_runtime_type.create_paginated_result(query.order_by(RuntimeType.spec_version.desc()), page_key, page_size)

    def resolve_get_runtime_type(self, info, filters=None):
        with SessionManager(session_cls=SessionLocal) as session:
            query = session.query(RuntimeType)
            query = RuntimeTypeFilter.filter(info, query, filters)
            return query.order_by(RuntimeType.spec_version.desc()).one()
