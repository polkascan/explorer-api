import graphene

from graphene_sqlalchemy_filter import FilterSet
from scalecodec.utils.ss58 import ss58_decode
from app.models.explorer import Block, Extrinsic, Event
from app.models.runtime import CodecEventIndexAccount


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
            'datetime':  ['eq', 'gt', 'lt', 'gte', 'lte'],
        }


class ExtrinsicFilter(FilterSet):
    multi_address_account_id = graphene.String(description='')

    class Meta:
        model = Extrinsic
        fields = {
            "block_number": ['eq', 'gt', 'lt', 'gte', 'lte', 'range'],
            'extrinsic_idx': ['eq',],
            'call_module': ['eq',],
            'call_name': ['eq',],
            'signed': ['eq',],
            "block_datetime": ['eq', 'gt', 'lt', 'gte', 'lte', 'range'],
            "spec_name": ['eq', ],
            "spec_version": ['eq', ],
        }

    @staticmethod
    def multi_address_account_id_filter(info, query, value):
        """ """
        return Extrinsic.multi_address_account_id == ss58_decode(value)


class EventsFilter(FilterSet):
    class Meta:
        model = Event
        fields = {
            "block_number": ['eq', 'gt', 'lt', 'gte', 'lte', 'range'],
            "event_module": ['eq', ],
            "event_idx": ['eq', ],
            "event_name": ['eq', ],
            "extrinsic_idx": ['eq', ],
            "block_datetime": ['eq', 'gt', 'lt', 'gte', 'lte', 'range'],
            "spec_name": ['eq', ],
            "spec_version": ['eq', ],
        }


class CodecEventIndexAccountFilter(FilterSet):
    class Meta:
        model = CodecEventIndexAccount
        fields = {
            "block_number": ['eq', 'gt', 'gte', 'lt', 'lte', 'range'],
            "block_datetime": ['eq', 'gt', 'gte', 'lt', 'lte', 'range'],
            "attribute_name": ['eq',],
            "pallet": ['eq', 'in'],
            "event_name": ['eq', 'in'],
            "account_id": ['eq', ],
        }
