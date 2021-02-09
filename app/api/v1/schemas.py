import graphene

from graphene_sqlalchemy import SQLAlchemyObjectType
from graphene_sqlalchemy_filter import FilterSet

from substrateinterface.utils.ss58 import ss58_decode, ss58_encode

from app.models.harvester import Block, Extrinsic, Event


class BlockFilter(FilterSet):

    class Meta:
        model = Block
        fields = {
            'hash':  ['eq','in'],
            'parent_hash':  ['eq',],
        }


class BlockSchema(SQLAlchemyObjectType):
    class Meta:
        model = Block


class ExtrinsicFilter(FilterSet):
    address = graphene.String(description='')

    class Meta:
        model = Extrinsic
        fields = {
            'module_id': ['eq',],
            'call_id': ['eq',],
            'success': ['eq',],
            'error':  ['eq',],
        }

    @staticmethod
    def address_filter(info, query, value):
        """ """
        return Extrinsic.address == ss58_decode(value)


class ExtrinsicSchema(SQLAlchemyObjectType):

    def resolve_address(self, info):
        return ss58_encode(self.address)

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

    class Meta:
        model = Event
