import graphene

from graphene_sqlalchemy_filter import FilterSet

from substrateinterface.utils.ss58 import ss58_decode
from app.models.explorer import Block, Extrinsic, Event
from app.models.runtime import Runtime, RuntimeCallArgument, RuntimeCall, RuntimeConstant, RuntimeErrorMessage, \
    RuntimeEvent, RuntimeEventAttribute, RuntimePallet, RuntimeStorage, RuntimeType


class BlockFilter(FilterSet):

    class Meta:
        model = Block
        fields = {
            'hash':  ['eq',],
            'number':  ['eq',],
        }


class BlocksFilter(FilterSet):
    hash_from = graphene.String()

    @staticmethod
    def hash_from(info, query, value, direction):
        if value:
            sub_select = query.session.query(Block.number)
            block_nr = sub_select.filter(Block.hash == value).one()
            block_nr = block_nr and block_nr[0] or None
            if direction == 'lte':
                query = query.filter(Block.number <= block_nr)
            elif direction == 'lt':
                query = query.filter(Block.number < block_nr)
            elif direction == 'gte':
                query = query.filter(Block.number >= block_nr)
            elif direction == 'gt':
                query = query.filter(Block.number > block_nr)

        return query, None

    @staticmethod
    def hash_from_filter(info, query, value):
        return BlocksFilter.hash_from(info, query, value, 'gte')

    class Meta:
        model = Block
        fields = {
            'hash':  ['eq',],
            'number':  ['eq', 'gt', 'lt', 'gte', 'lte'],
        }


class ExtrinsicFilter(FilterSet):
    multi_address_account_id = graphene.String(description='')

    class Meta:
        model = Extrinsic
        fields = {
            'block_number': ['eq',],
            'extrinsic_idx': ['eq',],
            'call_module': ['eq',],
            'call_name': ['eq',],
            'signed': ['eq',],
        }

    @staticmethod
    def multi_address_account_id_filter(info, query, value):
        """ """
        return Extrinsic.multi_address_account_id == ss58_decode(value)


class EventFilter(FilterSet):
    class Meta:
        model = Event
        fields = {
            'block_number':  ['eq',],
            'event_idx':  ['eq',],
        }


class EventsFilter(FilterSet):
    class Meta:
        model = Event
        fields = {
            'block_number':  ['eq',],
            'event_module':  ['eq',],
            'event_name':  ['eq',],
        }


class RuntimeFilter(FilterSet):
    class Meta:
        model = Runtime
        fields = {
            'spec_name':  ['eq',],
            'spec_version':  ['eq',],
        }


class RuntimeCallFilter(FilterSet):

    class Meta:
        model = RuntimeCall
        fields = {
            'spec_name':  ['eq',],
            'spec_version':  ['eq',],
            'pallet':  ['eq',],
        }


class RuntimeCallArgumentFilter(FilterSet):

    class Meta:
        model = RuntimeCallArgument
        fields = {
            'spec_name':  ['eq',],
            'spec_version':  ['eq',],
            'pallet':  ['eq',],
            'call_name':  ['eq',],
        }


class RuntimeConstantFilter(FilterSet):

    class Meta:
        model = RuntimeConstant
        fields = {
            'spec_name':  ['eq',],
            'spec_version':  ['eq',],
            'pallet':  ['eq',],
            'const_name':  ['eq',],
        }


class RuntimeErrorMessageFilter(FilterSet):

    class Meta:
        model = RuntimeErrorMessage
        fields = {
            'spec_name':  ['eq',],
            'spec_version':  ['eq',],
            'pallet':  ['eq',],
            'error_name':  ['eq',],
        }


class RuntimeEventFilter(FilterSet):

    class Meta:
        model = RuntimeEvent
        fields = {
            'spec_name':  ['eq',],
            'spec_version':  ['eq',],
            'pallet':  ['eq',],
            'event_name':  ['eq',],
        }


class RuntimeEventAttributeFilter(FilterSet):

    class Meta:
        model = RuntimeEventAttribute
        fields = {
            'spec_name':  ['eq',],
            'spec_version':  ['eq',],
            'pallet':  ['eq',],
        }


class RuntimePalletFilter(FilterSet):

    class Meta:
        model = RuntimePallet
        fields = {
            'spec_name':  ['eq',],
            'spec_version':  ['eq',],
            'pallet': ['eq', ],
        }


class RuntimeStorageFilter(FilterSet):

    class Meta:
        model = RuntimeStorage
        fields = {
            'spec_name':  ['eq',],
            'spec_version':  ['eq',],
            'pallet': ['eq', ],
            'storage_name': ['eq', ],
        }


class RuntimeTypeFilter(FilterSet):

    class Meta:
        model = RuntimeType
        fields = {
            'spec_name':  ['eq',],
            'spec_version':  ['eq',],
            'pallet': ['eq', ],
            'scale_type': ['eq', ],
        }
