from collections import Iterable

import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphene_sqlalchemy_filter import FilterSet
from graphql import GraphQLError
from app import settings

from app.api.graphql.filters import create_filter, BlocksFilter, ExtrinsicFilter
from app.api.graphql.pagination import create_paginated_type
from app.api.graphql.schemas import create_schema, ExtrinsicSchema
from app.db import SessionManager
from app.models.explorer import Block, Extrinsic, Event, Log, Transfer
from app.models.runtime import Runtime, RuntimeCall, RuntimeCallArgument, RuntimeConstant, RuntimeErrorMessage, \
    RuntimeEvent, RuntimeEventAttribute, RuntimePallet, RuntimeStorage, RuntimeType
from app.session import SessionLocal


"""
pagination
filter_dependencies
subscriptions


meta zooi in een node.py
breng functies onder in verschillende files en import de node functies
custom filters & schemas terug naar deze specifieke files
"""

REGISTERED_GRAPHQL_NODES = set()


class QueryNodeOne(object):

    def __init__(
            self,
            class_name,
            model_,
            filters=None,
            filter_required=False,
            filter_dependencies=None,
            schema_overrides=None,
            order_by=None,
            paginated=False,
            return_type=None
    ):
        if class_name in REGISTERED_GRAPHQL_NODES:
            raise Exception(f"Node with name '{class_name}' already registered")

        REGISTERED_GRAPHQL_NODES.add(class_name)

        node_args = {}
        pagination_obj = None

        if isinstance(schema_overrides, SQLAlchemyObjectType):
            node_schema = schema_overrides
        else:
            node_schema = create_schema(class_name, model_, schema_overrides=schema_overrides)

        if paginated:
            pagination_obj = create_paginated_type(class_name, node_schema)
            node_schema = pagination_obj
            node_args["page_key"] = graphene.String()
            node_args["page_size"] = graphene.Int()

        #if isinstance(filters, FilterSet):
        if filters and hasattr(filters, "FILTER_OBJECT_TYPES"):
            filter_obj = filters
            node_args["filters"] = filter_obj
        elif filters:
            filter_obj = create_filter(class_name, model_, filters)()
            node_args["filters"] = filter_obj
        else:
            filter_obj = None

        self.node_resolve_func = self.resolve(
            class_name,
            model_,
            order_by,
            filter_obj,
            filter_required,
            filter_dependencies,
            pagination_obj
        )

        if not return_type:
            return_type = graphene.Field

        self.node = return_type(
            node_schema,
            **node_args
        )

    @staticmethod
    def resolve(class_name, model, order_by, filter_obj, filter_required, filter_dependencies, pagination_obj):
        def resolve_func(self, info, filters=None, page_key=None, page_size=settings.DEFAULT_PAGE_SIZE):
            with SessionManager(session_cls=SessionLocal) as session:
                query = session.query(model)
                if isinstance(order_by, Iterable):
                    query = query.order_by(*order_by)
                else:
                    query = query.order_by(order_by)

                if filters:
                    if not filter_obj:
                        raise GraphQLError(f'{class_name} is not filterable')

                    #if filter_dependencies:
                    #    #TODO!
                    #    #import pdb;pdb.set_trace()

                    return filter_obj.filter(info, query, filters).one()
                elif filter_required:
                    raise GraphQLError(f'{class_name} requires filters')

                return query.first()
        return resolve_func


class QueryNodeMany(QueryNodeOne):
    def __init__(self, *args, **kwargs):
        super(QueryNodeMany, self).__init__(*args, **kwargs)

    @staticmethod
    def resolve(class_name, model, order_by, filter_obj, filter_required, filter_dependencies, pagination_obj):
        def resolve_func(self, info, filters=None, page_key=None, page_size=settings.DEFAULT_PAGE_SIZE):
            with SessionManager(session_cls=SessionLocal) as session:
                query = session.query(model)
                if isinstance(order_by, Iterable):
                    query = query.order_by(*order_by)
                else:
                    query = query.order_by(order_by)

                if filters:
                    if not filter_obj:
                        raise GraphQLError(f'{class_name} is not filterable')

                    # if filter_dependencies:
                    #     #TODO
                    #     #import pdb;pdb.set_trace()

                    query = filter_obj.filter(info, query, filters)

                elif filter_required:
                    raise GraphQLError(f'{class_name} requires filters')

                if pagination_obj:
                    query = pagination_obj.create_paginated_result(query, page_key, page_size)

                return query

        return resolve_func


class QueryGenerator(graphene.ObjectType):
    def __new__(cls, name, bases, dct):
        node_dict = {}
        for key_id, key_val in dct.items():
            if isinstance(dct[key_id], (QueryNodeOne,)):
                node_dict[key_id] = dct[key_id].node
                node_dict[f"resolve_{key_id}"] = dct[key_id].node_resolve_func
            else:
                node_dict[key_id] = dct[key_id]

        return type(f"{name}", (graphene.ObjectType, ), node_dict)


class GraphQLQueries(metaclass=QueryGenerator):
    #get_latest_block = graphene.Field(BlockSchema)
    get_latest_block = QueryNodeOne(
        class_name="LatestBlock",
        model_=Block,
        #schema_overrides={Block.number: graphene.String()},
        order_by=Block.number.desc()
    )
    #get_block = graphene.Field(BlockSchema, filters=BlockFilter())
    get_block = QueryNodeOne(
        class_name="GetBlock",
        model_=Block,
        filters={
            Block.hash: ['eq',],
            Block.number: ['eq',]
        },
        order_by=Block.number.desc(),
        filter_required=True,
        # filter_dependencies={
        #     Block.number: (Block.hash,)
        # }
    )
    #get_blocks = graphene.Field(paginated_blocks, filters=BlocksFilter(), page_key=graphene.String(), page_size=graphene.Int())
    get_blocks = QueryNodeMany(
        class_name="GetBlocks",
        model_=Block,
        order_by=Block.number.desc(),
        filters=BlocksFilter(),
        paginated=True
    )
    #get_extrinsic = graphene.Field(ExtrinsicSchema, filters=ExtrinsicFilter())
    get_extrinsic = QueryNodeOne(
        class_name="GetExtrinsic",
        model_=Extrinsic,
        schema_overrides={"multi_address_account_id": graphene.String(description='')},
        order_by=Extrinsic.block_number.desc(),
        filters=ExtrinsicFilter(),
    )
    #get_extrinsics = graphene.Field(paginated_event, filters=ExtrinsicFilter(), page_key=graphene.String(), page_size=graphene.Int())
    get_extrinsics = QueryNodeMany(
        class_name="GetExtrinsics",
        model_=Extrinsic,
        schema_overrides={"multi_address_account_id": graphene.String(description='')},
        order_by=Extrinsic.block_number.desc(),
        filters=ExtrinsicFilter(),
        paginated=True
    )
    #get_event = graphene.Field(EventSchema, filters=EventFilter())
    get_event = QueryNodeOne(
        class_name="GetEvent",
        model_=Event,
        order_by=Event.block_number.desc(),
        filters={
            Event.block_number:  ['eq',],
            Event.event_idx:  ['eq',],
        }
    )
    #get_events = graphene.Field(paginated_event, filters=EventsFilter(), page_key=graphene.String(), page_size=graphene.Int())
    get_events = QueryNodeMany(
        class_name="GetEvents",
        model_=Event,
        order_by=Event.block_number.desc(),
        filters={
            Event.block_number:  ['eq',],
            Event.event_module:  ['eq',],
            Event.event_name:  ['eq',],
        },
        paginated=True
    )

    #get_runtime = graphene.Field(RuntimeSchema, filters=RuntimeFilter())
    get_runtime = QueryNodeOne(
        class_name="GetRuntime",
        model_=Runtime,
        order_by=Runtime.spec_version.desc(),
        filters={
            Runtime.spec_name:  ['eq',],
            Runtime.spec_version:  ['eq',],
        },
        filter_required=True,
    )

    #get_latest_runtime = graphene.Field(RuntimeSchema)
    get_latest_runtime = QueryNodeOne(
        class_name="GetLatestRuntime",
        model_=Runtime,
        order_by=Runtime.spec_version.desc(),
        filter_required=True,
    )

    #get_runtimes = graphene.Field(paginated_runtime, filters=RuntimeFilter(), page_key=graphene.String(), page_size=graphene.Int())
    get_runtimes = QueryNodeMany(
        class_name="GetRuntimes",
        model_=Runtime,
        order_by=(Runtime.spec_version.desc(), Runtime.spec_name.desc()),
        filters={
            Runtime.spec_name:  ['eq',],
            Runtime.spec_version:  ['eq',],
        },
        filter_required=True,
        paginated=True
    )

    #get_runtime_call = graphene.Field(RuntimeCallSchema, filters=RuntimeCallFilter())
    get_runtime_call = QueryNodeOne(
        class_name="GetRuntimeCall",
        model_=RuntimeCall,
        filters={
            RuntimeCall.spec_name:  ['eq',],
            RuntimeCall.spec_version:  ['eq',],
            RuntimeCall.pallet:  ['eq',],
        },
        filter_required=True,
        order_by=(RuntimeCall.pallet.desc(), RuntimeCall.call_name.desc(), RuntimeCall.spec_version.desc()),
    )

    #get_runtime_calls = graphene.Field(paginated_runtime_call, filters=RuntimeCallFilter(), page_key=graphene.String(), page_size=graphene.Int())
    get_runtime_calls = QueryNodeMany(
        class_name="GetRuntimeCalls",
        model_=RuntimeCall,
        order_by=(RuntimeCall.pallet.desc(), RuntimeCall.call_name.desc(), RuntimeCall.spec_version.desc()),
        filters={
            RuntimeCall.spec_name:  ['eq',],
            RuntimeCall.spec_version:  ['eq',],
            RuntimeCall.pallet:  ['eq',],
        },
        filter_required=True,
        paginated=True
    )

    #get_runtime_call_argument = graphene.Field(RuntimeCallArgumentSchema, filters=RuntimeCallArgumentFilter())
    get_runtime_call_argument = QueryNodeOne(
        class_name="GetRuntimeCallArgument",
        model_=RuntimeCallArgument,
        filters={
            RuntimeCallArgument.spec_name:  ['eq',],
            RuntimeCallArgument.spec_version:  ['eq',],
            RuntimeCallArgument.pallet:  ['eq',],
            RuntimeCallArgument.call_name:  ['eq',],
        },
        filter_required=True,
        order_by=(RuntimeCallArgument.pallet.desc(), RuntimeCallArgument.call_name.desc(), RuntimeCallArgument.spec_version.desc()),
    )

    #get_runtime_call_arguments = graphene.Field(paginated_runtime_call_argument, filters=RuntimeCallArgumentFilter(), page_key=graphene.String(), page_size=graphene.Int())
    get_runtime_call_arguments = QueryNodeMany(
        class_name="GetRuntimeCallArguments",
        model_=RuntimeCallArgument,
        order_by=(RuntimeCallArgument.pallet.desc(), RuntimeCallArgument.call_name.desc(), RuntimeCallArgument.spec_version.desc()),
        filters={
            RuntimeCallArgument.spec_name:  ['eq',],
            RuntimeCallArgument.spec_version:  ['eq',],
            RuntimeCallArgument.pallet:  ['eq',],
            RuntimeCallArgument.call_name:  ['eq',],
        },
        filter_required=True,
        paginated=True
    )

    #get_runtime_constant = graphene.Field(RuntimeConstantSchema, filters=RuntimeConstantFilter())
    get_runtime_constant = QueryNodeOne(
        class_name="GetRuntimeConstant",
        model_=RuntimeConstant,
        filters={
            RuntimeConstant.spec_name:  ['eq',],
            RuntimeConstant.spec_version:  ['eq',],
            RuntimeConstant.pallet:  ['eq',],
            RuntimeConstant.constant_name:  ['eq',],
        },
        filter_required=True,
        order_by=(RuntimeConstant.pallet.desc(), RuntimeConstant.constant_name.desc(), RuntimeConstant.spec_version.desc()),
    )

    #get_runtime_constants = graphene.Field(paginated_runtime_constant, filters=RuntimeConstantFilter(), page_key=graphene.String(), page_size=graphene.Int())
    get_runtime_constants = QueryNodeMany(
        class_name="GetRuntimeConstants",
        model_=RuntimeConstant,
        order_by=(RuntimeConstant.pallet.desc(), RuntimeConstant.constant_name.desc(), RuntimeConstant.spec_version.desc()),
        filters={
            RuntimeConstant.spec_name:  ['eq',],
            RuntimeConstant.spec_version:  ['eq',],
            RuntimeConstant.pallet:  ['eq',],
            RuntimeConstant.constant_name:  ['eq',],
        },
        filter_required=True,
        paginated=True
    )

    #get_runtime_error_message = graphene.Field(RuntimeErrorMessageSchema, filters=RuntimeErrorMessageFilter())
    get_runtime_error_message = QueryNodeOne(
        class_name="GetRuntimeErrorMessage",
        model_=RuntimeErrorMessage,
        filters={
            RuntimeErrorMessage.spec_name:  ['eq',],
            RuntimeErrorMessage.spec_version:  ['eq',],
            RuntimeErrorMessage.pallet:  ['eq',],
            RuntimeErrorMessage.error_name:  ['eq',],
        },
        filter_required = True,
        order_by=(RuntimeErrorMessage.pallet.desc(), RuntimeErrorMessage.error_name.desc(), RuntimeErrorMessage.spec_version.desc()),
    )

    #get_runtime_error_messages = graphene.Field(paginated_runtime_error_message, filters=RuntimeErrorMessageFilter())
    get_runtime_error_messages = QueryNodeMany(
        class_name="GetRuntimeErrorMessages",
        model_=RuntimeErrorMessage,
        order_by=RuntimeErrorMessage.spec_version.desc(),
        filters={
            RuntimeErrorMessage.spec_name:  ['eq',],
            RuntimeErrorMessage.spec_version:  ['eq',],
            RuntimeErrorMessage.pallet:  ['eq',],
            RuntimeErrorMessage.error_name:  ['eq',],
        },
        filter_required = True,
        paginated=True
    )

    #get_runtime_event = graphene.Field(RuntimeEventSchema, filters=RuntimeEventFilter())
    get_runtime_event = QueryNodeOne(
        class_name="GetRuntimeEvent",
        model_=RuntimeEvent,
        filters={
            RuntimeEvent.spec_name:  ['eq',],
            RuntimeEvent.spec_version:  ['eq',],
            RuntimeEvent.pallet:  ['eq',],
            RuntimeEvent.event_name:  ['eq',],
        },
        filter_required = True,
        order_by=RuntimeEvent.spec_version.desc(),
    )

    #get_runtime_events = graphene.Field(paginated_runtime_event, filters=RuntimeEventFilter(), page_key=graphene.String(), page_size=graphene.Int())
    get_runtime_events = QueryNodeMany(
        class_name="GetRuntimeEvents",
        model_=RuntimeEvent,
        order_by=RuntimeEvent.spec_version.desc(),
        filters={
            RuntimeEvent.spec_name:  ['eq',],
            RuntimeEvent.spec_version:  ['eq',],
            RuntimeEvent.pallet:  ['eq',],
            RuntimeEvent.event_name:  ['eq',],
        },
        filter_required = True,
        paginated=True
    )

    #get_runtime_event_attributes = graphene.Field(paginated_runtime_event_attribute, filters=RuntimeEventAttributeFilter(), page_key=graphene.String(), page_size=graphene.Int())
    get_runtime_event_attributes = QueryNodeMany(
        class_name="GetRuntimeEventAttributes",
        model_=RuntimeEventAttribute,
        order_by=RuntimeEventAttribute.spec_version.desc(),
        filters={
            RuntimeEventAttribute.spec_name:  ['eq',],
            RuntimeEventAttribute.spec_version:  ['eq',],
            RuntimeEventAttribute.pallet:  ['eq',],
            RuntimeEventAttribute.event_name:  ['eq',],
        },
        filter_required = True,
        paginated=True
    )

    #get_runtime_pallet = graphene.Field(RuntimePalletSchema, filters=RuntimePalletFilter())
    get_runtime_pallet = QueryNodeOne(
        class_name="GetRuntimePallet",
        model_=RuntimePallet,
        filters={
            RuntimePallet.spec_name:  ['eq',],
            RuntimePallet.spec_version:  ['eq',],
            RuntimePallet.pallet: ['eq', ],
        },
        filter_required=True,
        order_by=(RuntimePallet.pallet.desc(), RuntimePallet.spec_version.desc()),
    )


    #get_runtime_pallets = graphene.Field(paginated_runtime_pallet, filters=RuntimePalletFilter(), page_key=graphene.String(), page_size=graphene.Int())
    get_runtime_pallets = QueryNodeMany(
        class_name="GetRuntimePallets",
        model_=RuntimePallet,
        order_by=(RuntimePallet.pallet.desc(), RuntimePallet.spec_version.desc()),
        filters={
            RuntimePallet.spec_name:  ['eq',],
            RuntimePallet.spec_version:  ['eq',],
            RuntimePallet.pallet: ['eq', ],
        },
        filter_required=True,
        paginated=True
    )

    #get_runtime_storage = graphene.Field(RuntimeStorageSchema, filters=RuntimeStorageFilter())
    get_runtime_storage = QueryNodeOne(
        class_name="GetRuntimeStorage",
        model_=RuntimeStorage,
        filters={
            RuntimeStorage.spec_name:  ['eq',],
            RuntimeStorage.spec_version:  ['eq',],
            RuntimeStorage.pallet: ['eq', ],
            RuntimeStorage.storage_name: ['eq', ],
        },
        filter_required = True,
        order_by=(RuntimeStorage.pallet.desc(), RuntimeStorage.spec_version.desc()),
    )

    #get_runtime_storages = graphene.Field(paginated_runtime_storage, filters=RuntimeStorageFilter(), page_key=graphene.String(), page_size=graphene.Int())
    get_runtime_storages = QueryNodeMany(
        class_name="GetRuntimeStorages",
        model_=RuntimeStorage,
        filters={
            RuntimeStorage.spec_name:  ['eq',],
            RuntimeStorage.spec_version:  ['eq',],
            RuntimeStorage.pallet: ['eq', ],
            RuntimeStorage.storage_name: ['eq', ],
        },
        filter_required = True,
        order_by=(RuntimeStorage.pallet.desc(), RuntimeStorage.spec_version.desc()),
    )

    #get_runtime_type = graphene.Field(RuntimeTypeSchema, filters=RuntimeTypeFilter())
    get_runtime_type = QueryNodeOne(
        class_name="GetRuntimeType",
        model_=RuntimeType,
        filters={
            RuntimeType.spec_name:  ['eq',],
            RuntimeType.spec_version:  ['eq',],
            RuntimeType.scale_type: ['eq', ],
        },
        filter_required = True,
        order_by=RuntimeType.spec_version.desc(),
    )

    #get_runtime_types = graphene.Field(paginated_runtime_type, filters=RuntimeTypeFilter(), page_key=graphene.String(), page_size=graphene.Int())
    get_runtime_types = QueryNodeMany(
        class_name="GetRuntimeTypes",
        model_=RuntimeType,
        filters={
            RuntimeType.spec_name:  ['eq',],
            RuntimeType.spec_version:  ['eq',],
            RuntimeType.scale_type: ['eq', ],
        },
        filter_required = True,
        order_by=RuntimeType.spec_version.desc(),
    )

    get_log = QueryNodeOne(
        class_name="GetLog",
        model_=Log,
        filters={
            Log.block_number: ['eq', ],
            Log.type_id: ['eq',],
            Log.type_name:  ['eq',],
            Log.block_datetime:  ['eq', 'lt', 'lte', 'gt', 'gte'],
            Log.block_hash:  ['eq',],
            Log.spec_name:  ['eq',],
            Log.spec_version:  ['eq',],
            Log.complete:  ['eq',],
        },
        filter_required=True,
        order_by=Log.spec_version.desc(),
    )

    get_logs = QueryNodeMany(
        class_name="GetLogs",
        model_=Log,
        filters={
            Log.block_number: ['eq',],
            Log.type_id: ['eq',],
            Log.type_name:  ['eq',],
            Log.block_datetime:  ['eq', 'lt', 'lte', 'gt', 'gte'],
            Log.block_hash:  ['eq',],
            Log.spec_name:  ['eq',],
            Log.spec_version:  ['eq',],
            Log.complete:  ['eq',],
        },
        filter_required=True,
        order_by=Log.spec_version.desc(),
        paginated=True
    )

    get_transfer = QueryNodeOne(
        class_name="GetTransfer",
        model_=Transfer,
        filters={
            Transfer.block_number: ['eq',],
            Transfer.event_idx: ['eq',],
            Transfer.extrinsic_idx: ['eq',],
            Transfer.from_multi_address_type: ['eq',],
            Transfer.from_multi_address_account_id: ['eq',],
            Transfer.from_multi_address_address_20: ['eq',],
            Transfer.from_multi_address_address_32: ['eq',],
            Transfer.to_multi_address_type: ['eq', ],
            Transfer.to_multi_address_account_id: ['eq', ],
            Transfer.to_multi_address_address_20: ['eq', ],
            Transfer.to_multi_address_address_32: ['eq', ],
            Transfer.block_datetime: ['eq', 'lt', 'lte', 'gt', 'gte'],
        },
        filter_required=True,
        order_by=Transfer.block_number.desc(),
    )

    get_transfers = QueryNodeMany(
        class_name="GetTransfers",
        model_=Transfer,
        filters={
            Transfer.block_number: ['eq', ],
            Transfer.event_idx: ['eq', ],
            Transfer.extrinsic_idx: ['eq', ],
            Transfer.from_multi_address_type: ['eq', ],
            Transfer.from_multi_address_account_id: ['eq', ],
            Transfer.from_multi_address_address_20: ['eq', ],
            Transfer.from_multi_address_address_32: ['eq', ],
            Transfer.to_multi_address_type: ['eq', ],
            Transfer.to_multi_address_account_id: ['eq', ],
            Transfer.to_multi_address_address_20: ['eq', ],
            Transfer.to_multi_address_address_32: ['eq', ],
            Transfer.block_datetime: ['eq', 'lt', 'lte', 'gt', 'gte'],
        },
        filter_required=True,
        order_by=Transfer.block_number.desc(),
        paginated=True
    )