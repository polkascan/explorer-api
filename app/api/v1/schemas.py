import json

import graphene

from graphene_sqlalchemy import SQLAlchemyObjectType
from graphene_sqlalchemy_filter import FilterSet

from sqlakeyset import get_page

from substrateinterface.utils.ss58 import ss58_decode, ss58_encode

from app.models.explorer import Block, Extrinsic, Event


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


class BlockSchema(SQLAlchemyObjectType):
    hash = graphene.String()
    parent_hash = graphene.String()
    state_root = graphene.String()
    extrinsics_root = graphene.String()
    author_account_id = graphene.String()

    class Meta:
        model = Block


class ExtrinsicFilter(FilterSet):
    multi_address_account_id = graphene.String(description='')

    class Meta:
        model = Extrinsic
        fields = {
            'module_id': ['eq',],
            'call_id': ['eq',],
            'success': ['eq',],
            'error':  ['eq',],
        }

    @staticmethod
    def multi_address_account_id_filter(info, query, value):
        """ """
        return Extrinsic.multi_address_account_id == ss58_decode(value)


class ExtrinsicSchema(SQLAlchemyObjectType):
    hash = graphene.String()
    version_info = graphene.String()
    call = graphene.String()
    call_hash = graphene.String()
    multi_address_account_id = graphene.String()
    multi_address_raw = graphene.String()
    multi_address_address_32 = graphene.String()
    multi_address_address_20 = graphene.String()
    signature = graphene.String()
    block_hash = graphene.String()


    def resolve_multi_address_account_id(self, info):
        return ss58_encode(self.multi_address_account_id)

    class Meta:
        model = Extrinsic


class EventFilter(FilterSet):
    class Meta:
        model = Event
        fields = {
            'module_id':  ['eq',],
            'event_id':  ['eq',],
        }


class EventSchema(SQLAlchemyObjectType):
    event = graphene.String()
    block_hash = graphene.String()

    class Meta:
        model = Event


class PaginationType(graphene.ObjectType):
    page_size = graphene.Int()
    page_next = graphene.String()
    page_prev = graphene.String()


class AbstractPaginatedType(graphene.ObjectType):

    @classmethod
    def create_paginated_result(cls, query, page_key=None, page_size=10):
        page_key = page_key and json.loads(page_key) or None
        paged_qs = get_page(query, per_page=page_size, page=page_key)
        page_info = PaginationType(
            page_size=page_size,
            page_next=json.dumps(paged_qs.paging.next),
            page_prev=json.dumps(paged_qs.paging.previous),
        )

        return cls(objects=paged_qs, page_info=page_info)


class BlockPaginatedType(AbstractPaginatedType):
    page_info = graphene.Field(PaginationType)
    objects = graphene.List(BlockSchema)


class ExtrinsicsPaginatedType(AbstractPaginatedType):
    page_info = graphene.Field(PaginationType)
    objects = graphene.List(ExtrinsicSchema)


class EventPaginatedType(AbstractPaginatedType):
    page_info = graphene.Field(PaginationType)
    objects = graphene.List(EventSchema)
