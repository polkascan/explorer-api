import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType

from substrateinterface.utils.ss58 import ss58_encode
from app.models.explorer import Block, Extrinsic, Event


class BlockSchema(SQLAlchemyObjectType):
    # Note: we override these specific fields to mark them as string instead of binary
    number = graphene.Int()
    hash = graphene.String()
    parent_hash = graphene.String()
    state_root = graphene.String()
    extrinsics_root = graphene.String()
    author_account_id = graphene.String()

    class Meta:
        model = Block


class ExtrinsicSchema(SQLAlchemyObjectType):
    # Note: we override these specific fields to mark them as string instead of binary
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


class EventSchema(SQLAlchemyObjectType):
    # Note: we override these specific fields to mark them as string instead of binary
    event = graphene.String()
    block_hash = graphene.String()

    class Meta:
        model = Event
