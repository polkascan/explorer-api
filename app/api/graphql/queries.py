import graphene

from app.api.graphql.filters import BlocksFilter, ExtrinsicFilter
from app.api.graphql.node import QueryGenerator, QueryNodeOne, QueryNodeMany
from app.models.explorer import Block, Extrinsic, Event, Log, Transfer
from app.models.runtime import Runtime, RuntimeCall, RuntimeCallArgument, RuntimeConstant, RuntimeErrorMessage, \
    RuntimeEvent, RuntimeEventAttribute, RuntimePallet, RuntimeStorage, RuntimeType


"""
pagination
filter_dependencies
subscriptions
"""


class GraphQLQueries(metaclass=QueryGenerator):

    get_latest_block = QueryNodeOne(
        class_name="LatestBlock",
        model_=Block,
        order_by=Block.number.desc()
    )

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

    get_blocks = QueryNodeMany(
        class_name="GetBlocks",
        model_=Block,
        order_by=Block.number.desc(),
        filters=BlocksFilter(),
        paginated=True
    )

    get_extrinsic = QueryNodeOne(
        class_name="GetExtrinsic",
        model_=Extrinsic,
        schema_overrides={"multi_address_account_id": graphene.String(description='')},
        order_by=Extrinsic.block_number.desc(),
        filters=ExtrinsicFilter(),
    )

    get_extrinsics = QueryNodeMany(
        class_name="GetExtrinsics",
        model_=Extrinsic,
        schema_overrides={"multi_address_account_id": graphene.String(description='')},
        order_by=Extrinsic.block_number.desc(),
        filters=ExtrinsicFilter(),
        paginated=True
    )

    get_event = QueryNodeOne(
        class_name="GetEvent",
        model_=Event,
        order_by=Event.block_number.desc(),
        filters={
            Event.block_number:  ['eq',],
            Event.event_idx: ['eq',],
        }
    )

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

    get_latest_runtime = QueryNodeOne(
        class_name="GetLatestRuntime",
        model_=Runtime,
        order_by=Runtime.spec_version.desc(),
        filter_required=True,
    )

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
