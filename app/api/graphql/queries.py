import graphene

from app.api.graphql.filters import BlocksFilter, ExtrinsicFilter
from app.api.graphql.node import QueryGenerator, QueryNodeOne, QueryNodeMany
from app.models.explorer import Block, Extrinsic, Event, Log, Transfer, TaggedAccount
from app.models.runtime import Runtime, RuntimeCall, RuntimeCallArgument, RuntimeConstant, RuntimeErrorMessage, \
    RuntimeEvent, RuntimeEventAttribute, RuntimePallet, RuntimeStorage, RuntimeType


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
            Block.number: ['eq',],
            Block.datetime: ['eq', 'gt', 'lt', 'gte', 'lte']
        },
        order_by=Block.number.desc(),
        filter_required=True
    )

    get_blocks = QueryNodeMany(
        class_name="GetBlocks",
        model_=Block,
        order_by=Block.number.desc(),
        filters=BlocksFilter(),
        paginated=True,
    )

    get_extrinsic = QueryNodeOne(
        class_name="GetExtrinsic",
        model_=Extrinsic,
        schema_overrides={"multi_address_account_id": graphene.String(description='')},
        order_by=(Extrinsic.block_number.desc(), Extrinsic.extrinsic_idx.desc()),
        filters=ExtrinsicFilter(),
    )

    get_extrinsics = QueryNodeMany(
        class_name="GetExtrinsics",
        model_=Extrinsic,
        schema_overrides={"multi_address_account_id": graphene.String(description='')},
        order_by=(Extrinsic.block_number.desc(), Extrinsic.extrinsic_idx.desc()),
        filters=ExtrinsicFilter(),
        paginated=True,
        filter_combinations={
            Extrinsic.call_name: (Extrinsic.call_module,),
        }

    )

    get_event = QueryNodeOne(
        class_name="GetEvent",
        model_=Event,
        order_by=(Event.block_number.desc(), Event.event_idx.desc(),),
        filters={
            Event.block_number:  ['eq',],
            Event.event_idx:  ['eq',],
            Event.block_datetime:  ['eq', 'gt', 'lt', 'gte', 'lte'],
        },
        filter_combinations={
            Event.block_number: (Event.event_idx,),
            Event.event_idx: (Event.block_number,),
        }
    )

    get_events = QueryNodeMany(
        class_name="GetEvents",
        model_=Event,
        order_by=(Event.block_number.desc(), Event.event_idx.desc(),),
        filters={
            Event.block_number:  ['eq',],
            Event.event_module:  ['eq',],
            Event.event_name:  ['eq',],
            Event.extrinsic_idx:  ['eq',],
            Event.block_datetime: ['eq', 'gt', 'lt', 'gte', 'lte'],
        },
        paginated=True,
        filter_combinations={
            Event.event_name: (Event.event_module,),
            Event.extrinsic_idx: (Event.block_number,),
        }
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
        filter_combinations={
            Runtime.spec_name: (Runtime.spec_version,),
            Runtime.spec_version: (Runtime.spec_name,),
        }
    )

    get_latest_runtime = QueryNodeOne(
        class_name="GetLatestRuntime",
        model_=Runtime,
        order_by=Runtime.spec_version.desc(),
    )

    get_runtimes = QueryNodeMany(
        class_name="GetRuntimes",
        model_=Runtime,
        order_by=(Runtime.spec_version.desc(), Runtime.spec_name),
        filters={
            Runtime.spec_name:  ['eq',],
            Runtime.spec_version:  ['eq',],
        },
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
        order_by=(RuntimeCall.spec_version.desc(), RuntimeCall.pallet, RuntimeCall.call_name),
        filter_combinations={
            RuntimeCall.spec_name: (RuntimeCall.spec_version, RuntimeCall.pallet),
            RuntimeCall.spec_version: (RuntimeCall.spec_name, RuntimeCall.pallet),
            RuntimeCall.pallet: (RuntimeCall.spec_name, RuntimeCall.spec_version),
        }
    )

    get_runtime_calls = QueryNodeMany(
        class_name="GetRuntimeCalls",
        model_=RuntimeCall,
        order_by=(RuntimeCall.spec_version.desc(), RuntimeCall.pallet, RuntimeCall.call_name),
        filters={
            RuntimeCall.spec_name:  ['eq',],
            RuntimeCall.spec_version:  ['eq',],
            RuntimeCall.pallet:  ['eq',],
        },
        filter_required=True,
        #paginated=True,
        filter_combinations={
            RuntimeCall.spec_name: (RuntimeCall.spec_version,),
            RuntimeCall.spec_version: (RuntimeCall.spec_name,),
            RuntimeCall.pallet: (RuntimeCall.spec_name, RuntimeCall.spec_version),
        }
    )

    get_runtime_call_arguments = QueryNodeMany(
        class_name="GetRuntimeCallArguments",
        model_=RuntimeCallArgument,
        order_by=(RuntimeCallArgument.spec_version.desc(), RuntimeCallArgument.pallet, RuntimeCallArgument.call_name),
        filters={
            RuntimeCallArgument.spec_name:  ['eq',],
            RuntimeCallArgument.spec_version:  ['eq',],
            RuntimeCallArgument.pallet:  ['eq',],
            RuntimeCallArgument.call_name:  ['eq',],
        },
        filter_required=True,
        #paginated=True,
        filter_combinations={
            RuntimeCallArgument.spec_name: (RuntimeCallArgument.spec_version, RuntimeCallArgument.pallet, RuntimeCallArgument.call_name),
            RuntimeCallArgument.spec_version: (RuntimeCallArgument.spec_name, RuntimeCallArgument.pallet, RuntimeCallArgument.call_name),
            RuntimeCallArgument.pallet: (RuntimeCallArgument.spec_name, RuntimeCallArgument.spec_version, RuntimeCallArgument.call_name),
            RuntimeCallArgument.call_name: (RuntimeCallArgument.spec_name, RuntimeCallArgument.spec_version, RuntimeCallArgument.pallet),
        }
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
        order_by=(RuntimeConstant.spec_version.desc(), RuntimeConstant.pallet, RuntimeConstant.constant_name),
        filter_combinations={
            RuntimeConstant.spec_name: (RuntimeConstant.spec_version, RuntimeConstant.pallet, RuntimeConstant.constant_name),
            RuntimeConstant.spec_version: (RuntimeConstant.spec_name, RuntimeConstant.pallet, RuntimeConstant.constant_name),
            RuntimeConstant.pallet: (RuntimeConstant.spec_name, RuntimeConstant.spec_version, RuntimeConstant.constant_name),
            RuntimeConstant.constant_name: (RuntimeConstant.spec_name, RuntimeConstant.spec_version, RuntimeConstant.pallet),
        }
    )

    get_runtime_constants = QueryNodeMany(
        class_name="GetRuntimeConstants",
        model_=RuntimeConstant,
        order_by=(RuntimeConstant.spec_version.desc(), RuntimeConstant.pallet, RuntimeConstant.constant_name),
        filters={
            RuntimeConstant.spec_name:  ['eq',],
            RuntimeConstant.spec_version:  ['eq',],
            RuntimeConstant.pallet:  ['eq',],
            RuntimeConstant.constant_name:  ['eq',],
        },
        filter_required=True,
        #paginated=True,
        filter_combinations={
            RuntimeConstant.spec_name: (RuntimeConstant.spec_version,),
            RuntimeConstant.spec_version: (RuntimeConstant.spec_name,),
            RuntimeConstant.pallet: (RuntimeConstant.spec_name, RuntimeConstant.spec_version),
        }
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
        order_by=(RuntimeErrorMessage.spec_version.desc(), RuntimeErrorMessage.pallet, RuntimeErrorMessage.error_name),
        filter_combinations={
            RuntimeErrorMessage.spec_name: (RuntimeErrorMessage.spec_version, RuntimeErrorMessage.pallet, RuntimeErrorMessage.error_name),
            RuntimeErrorMessage.spec_version: (RuntimeErrorMessage.spec_name, RuntimeErrorMessage.pallet, RuntimeErrorMessage.error_name),
            RuntimeErrorMessage.pallet: (RuntimeErrorMessage.spec_name, RuntimeErrorMessage.spec_version, RuntimeErrorMessage.error_name),
            RuntimeErrorMessage.error_name: (RuntimeErrorMessage.spec_name, RuntimeErrorMessage.spec_version, RuntimeErrorMessage.pallet),
        }
    )

    get_runtime_error_messages = QueryNodeMany(
        class_name="GetRuntimeErrorMessages",
        model_=RuntimeErrorMessage,
        order_by=(RuntimeErrorMessage.spec_version.desc(), RuntimeErrorMessage.pallet, RuntimeErrorMessage.error_name),
        filters={
            RuntimeErrorMessage.spec_name:  ['eq',],
            RuntimeErrorMessage.spec_version:  ['eq',],
            RuntimeErrorMessage.pallet:  ['eq',],
            RuntimeErrorMessage.error_name:  ['eq',],
        },
        filter_required=True,
        #paginated=True,
        filter_combinations={
            RuntimeErrorMessage.spec_name: (RuntimeErrorMessage.spec_version, ),
            RuntimeErrorMessage.spec_version: (RuntimeErrorMessage.spec_name, ),
            RuntimeErrorMessage.pallet: (RuntimeErrorMessage.spec_name, RuntimeErrorMessage.spec_version),
        }
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
        filter_required=True,
        order_by=(RuntimeEvent.spec_version.desc(), RuntimeEvent.pallet, RuntimeEvent.event_name),
        filter_combinations={
            RuntimeEvent.spec_name: (RuntimeEvent.spec_version, RuntimeEvent.pallet, RuntimeEvent.event_name),
            RuntimeEvent.spec_version: (RuntimeEvent.spec_name, RuntimeEvent.pallet, RuntimeEvent.event_name),
            RuntimeEvent.pallet: (RuntimeEvent.spec_name, RuntimeEvent.spec_version, RuntimeEvent.event_name),
            RuntimeEvent.event_name: (RuntimeEvent.spec_name, RuntimeEvent.spec_version, RuntimeEvent.pallet),
        }
    )

    get_runtime_events = QueryNodeMany(
        class_name="GetRuntimeEvents",
        model_=RuntimeEvent,
        order_by=(RuntimeEvent.spec_version.desc(), RuntimeEvent.pallet, RuntimeEvent.event_name),
        filters={
            RuntimeEvent.spec_name:  ['eq',],
            RuntimeEvent.spec_version:  ['eq',],
            RuntimeEvent.pallet:  ['eq',],
            RuntimeEvent.event_name:  ['eq',],
        },
        filter_required=True,
        #paginated=True,
        filter_combinations={
            RuntimeEvent.spec_name: (RuntimeEvent.spec_version,),
            RuntimeEvent.spec_version: (RuntimeEvent.spec_name,),
            RuntimeEvent.pallet: (RuntimeEvent.spec_name, RuntimeEvent.spec_version),
        }
    )

    get_runtime_event_attributes = QueryNodeMany(
        class_name="GetRuntimeEventAttributes",
        model_=RuntimeEventAttribute,
        order_by=(RuntimeEventAttribute.spec_version.desc(), RuntimeEventAttribute.pallet, RuntimeEventAttribute.event_name),
        filters={
            RuntimeEventAttribute.spec_name:  ['eq',],
            RuntimeEventAttribute.spec_version:  ['eq',],
            RuntimeEventAttribute.pallet:  ['eq',],
            RuntimeEventAttribute.event_name:  ['eq',],
        },
        filter_required = True,
        #paginated=True,
        filter_combinations={
            RuntimeEventAttribute.spec_name: (RuntimeEventAttribute.spec_version, RuntimeEventAttribute.pallet, RuntimeEventAttribute.event_name),
            RuntimeEventAttribute.spec_version: (RuntimeEventAttribute.spec_name, RuntimeEventAttribute.pallet, RuntimeEventAttribute.event_name),
            RuntimeEventAttribute.pallet: (RuntimeEventAttribute.spec_name, RuntimeEventAttribute.spec_version, RuntimeEventAttribute.event_name),
            RuntimeEventAttribute.event_name: (RuntimeEventAttribute.spec_name, RuntimeEventAttribute.spec_version, RuntimeEventAttribute.pallet),
        }
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
        order_by=(RuntimePallet.spec_version.desc(), RuntimePallet.pallet, RuntimePallet.name),
        filter_combinations={
            RuntimePallet.spec_name: (RuntimePallet.spec_version, RuntimePallet.pallet,),
            RuntimePallet.spec_version: (RuntimePallet.spec_name, RuntimePallet.pallet,),
            RuntimePallet.pallet: (RuntimePallet.spec_name, RuntimePallet.spec_version,),
        }
    )

    get_runtime_pallets = QueryNodeMany(
        class_name="GetRuntimePallets",
        model_=RuntimePallet,
        order_by=(RuntimePallet.spec_version.desc(), RuntimePallet.pallet, RuntimePallet.name),
        filters={
            RuntimePallet.spec_name:  ['eq',],
            RuntimePallet.spec_version:  ['eq',],
            RuntimePallet.pallet: ['eq', ],
        },
        filter_required=True,
        #paginated=True,
        filter_combinations={
            RuntimePallet.spec_name: (RuntimePallet.spec_version,),
            RuntimePallet.spec_version: (RuntimePallet.spec_name,),
        }
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
        order_by=(RuntimeStorage.spec_version.desc(), RuntimeStorage.pallet, RuntimeStorage.storage_name),
        filter_combinations={
            RuntimeStorage.spec_name: (RuntimeStorage.spec_version, RuntimeStorage.pallet, RuntimeStorage.storage_name),
            RuntimeStorage.spec_version: (RuntimeStorage.spec_name, RuntimeStorage.pallet, RuntimeStorage.storage_name),
            RuntimeStorage.pallet: (RuntimeStorage.spec_name, RuntimeStorage.spec_version, RuntimeStorage.storage_name),
            RuntimeStorage.storage_name: (RuntimeStorage.spec_name, RuntimeStorage.spec_version, RuntimeStorage.pallet),
        }
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
        filter_required=True,
        #paginated=True,
        order_by=(RuntimeStorage.spec_version.desc(), RuntimeStorage.pallet, RuntimeStorage.storage_name),
        filter_combinations={
            RuntimeStorage.spec_name: (RuntimeStorage.spec_version,),
            RuntimeStorage.spec_version: (RuntimeStorage.spec_name,),
            RuntimeStorage.pallet: (RuntimeStorage.spec_name, RuntimeStorage.spec_version,),
        }
    )

    get_runtime_type = QueryNodeOne(
        class_name="GetRuntimeType",
        model_=RuntimeType,
        filters={
            RuntimeType.spec_name:  ['eq',],
            RuntimeType.spec_version:  ['eq',],
            RuntimeType.scale_type: ['eq', ],
        },
        filter_required=True,
        order_by=(RuntimeType.spec_version.desc(), RuntimeType.scale_type),
        filter_combinations={
            RuntimeType.spec_name: (RuntimeType.spec_version, RuntimeType.scale_type),
            RuntimeType.spec_version: (RuntimeType.spec_name,  RuntimeType.scale_type),
            RuntimeType.scale_type: (RuntimeType.spec_name, RuntimeType.spec_version),
        }
    )

    get_runtime_types = QueryNodeMany(
        class_name="GetRuntimeTypes",
        model_=RuntimeType,
        filters={
            RuntimeType.spec_name:  ['eq',],
            RuntimeType.spec_version:  ['eq',],
            RuntimeType.scale_type: ['eq', ],
        },
        filter_required=True,
        #paginated=True,
        order_by=(RuntimeType.spec_version.desc(), RuntimeType.scale_type),
        filter_combinations={
            RuntimeType.spec_name: (RuntimeType.spec_version,),
            RuntimeType.spec_version: (RuntimeType.spec_name,),
        }
    )

    get_log = QueryNodeOne(
        class_name="GetLog",
        model_=Log,
        filters={
            Log.block_number: ['eq', ],
            Log.log_idx: ['eq',],
            Log.type_id: ['eq',],
            Log.type_name:  ['eq',],
            Log.block_datetime:  ['eq', 'lt', 'lte', 'gt', 'gte'],
            Log.block_hash:  ['eq',],
            Log.spec_name:  ['eq',],
            Log.spec_version:  ['eq',],
            Log.complete:  ['eq',],
        },
        filter_required=True,
        order_by=(Log.block_number.desc(), Log.log_idx.desc()),
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
        order_by=(Log.block_number.desc(), Log.log_idx.desc()),
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
        order_by=(Transfer.block_number.desc(), Transfer.event_idx.desc(), Transfer.extrinsic_idx.desc()),
        filter_combinations={
            Transfer.block_number: (Transfer.event_idx,),
            Transfer.event_idx: (Transfer.block_number,),
        }
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
        order_by=(Transfer.block_number.desc(), Transfer.event_idx.desc(), Transfer.extrinsic_idx.desc()),
        paginated=True
    )

    get_tagged_account = QueryNodeOne(
        class_name="GetTaggedAccount",
        model_=TaggedAccount,
        schema_overrides={"account_id": graphene.String(description='')},
        filters={
            TaggedAccount.account_id: ['eq', ],
        },
        order_by=TaggedAccount.account_id.desc(),
        filter_required=True
    )
