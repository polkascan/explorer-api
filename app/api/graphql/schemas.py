import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType

from app.models.explorer import Extrinsic


class ExtrinsicSchema(SQLAlchemyObjectType):
    multi_address_account_id = graphene.String()
    block_number = graphene.Int()
    extrinsic_idx = graphene.Int()

    class Meta:
        model = Extrinsic
