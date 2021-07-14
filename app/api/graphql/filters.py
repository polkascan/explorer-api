import graphene

from graphene_sqlalchemy_filter import FilterSet
from substrateinterface.utils.ss58 import ss58_decode
from app.models.explorer import Block, Extrinsic


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
            'block_number': ['eq',],
            'extrinsic_idx': ['eq',],
            'call_module': ['eq',],
            'call_name': ['eq',],
            'signed': ['eq',],
            'block_datetime': ['eq', 'gt', 'lt', 'gte', 'lte'],
        }

    @staticmethod
    def multi_address_account_id_filter(info, query, value):
        """ """
        return Extrinsic.multi_address_account_id == ss58_decode(value)