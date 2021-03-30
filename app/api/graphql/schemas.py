import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType

from substrateinterface.utils.ss58 import ss58_encode
from app.models.explorer import Block, Extrinsic, Event


class BlockSchema(SQLAlchemyObjectType):
    number = graphene.Int()

    class Meta:
        model = Block


class ExtrinsicSchema(SQLAlchemyObjectType):
    multi_address_account_id = graphene.String()
    block_number = graphene.Int()

    def resolve_multi_address_account_id(self, info):
        return ss58_encode(self.multi_address_account_id)

    class Meta:
        model = Extrinsic


class EventSchema(SQLAlchemyObjectType):
    block_number = graphene.Int()

    class Meta:
        model = Event
