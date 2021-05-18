from collections import Iterable

import graphene
from graphql import GraphQLError
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphene_sqlalchemy_filter import FilterSet

from sqlalchemy import INTEGER, Integer
from sqlalchemy.orm.attributes import InstrumentedAttribute

from sqlakeyset import get_page

from app import settings
from app.db import SessionManager
from app.session import SessionLocal


REGISTERED_GRAPHQL_NODES = set()


def create_schema(query_name, model_, schema_overrides):
    class meta_:
        model = model_

    schema_overrides = schema_overrides or {}
    dct = {"Meta": meta_}

    # Note:
    # We override all INTEGER primary keys to be graphene int types;
    # graphene_sqlalchemy converts them to string by default
    for col in model_.__mapper__.primary_key:
        if isinstance(col.type, (INTEGER, Integer)):
            if col.name not in schema_overrides:
                dct[col.name] = graphene.Int()

    for key, val in schema_overrides.items():
        if isinstance(key, InstrumentedAttribute):
            dct[key.name] = val

    return type(f"Schema{query_name}", (SQLAlchemyObjectType, ), dct)


def create_filter(query_name, model_, field_options):
    class meta_:
        model = model_
        fields = {}

    for field, operators in field_options.items():
        meta_.fields[field.name] = operators
    return type(f"Filter{query_name}", (FilterSet, ), {"Meta": meta_})


def create_paginated_type(class_name, schema):
    class PaginatedType(AbstractPaginatedType):
        page_info = graphene.Field(PaginationType)
        objects = graphene.List(schema)

    dct = {"PaginatedType": PaginatedType}

    return type(f"Paginated{class_name}", (PaginatedType, ), dct)


class PaginationType(graphene.ObjectType):
    page_size = graphene.Int()
    page_next = graphene.String()
    page_prev = graphene.String()


class AbstractPaginatedType(graphene.ObjectType):

    @classmethod
    def create_paginated_result(cls, query, page_key=None, page_size=settings.DEFAULT_PAGE_SIZE):
        page_size = page_size or settings.DEFAULT_PAGE_SIZE
        paged_qs = get_page(query, per_page=page_size, page=page_key)
        page_info = PaginationType(
            page_size=page_size,
            page_next=paged_qs.paging.bookmark_next,
            page_prev=paged_qs.paging.bookmark_previous
        )

        return cls(objects=paged_qs, page_info=page_info)


class QueryNodeOne(object):

    def __init__(
            self,
            class_name,
            model_,
            filters=None,
            filter_required=False,
            filter_dependencies=None,
            schema_overrides=None,
            order_by=None,
            paginated=False,
            return_type=None
    ):
        if class_name in REGISTERED_GRAPHQL_NODES:
            raise Exception(f"Node with name '{class_name}' already registered")

        REGISTERED_GRAPHQL_NODES.add(class_name)

        node_args = {}
        pagination_obj = None

        if isinstance(schema_overrides, SQLAlchemyObjectType):
            node_schema = schema_overrides
        else:
            node_schema = create_schema(class_name, model_, schema_overrides=schema_overrides)

        if paginated:
            pagination_obj = create_paginated_type(class_name, node_schema)
            node_schema = pagination_obj
            node_args["page_key"] = graphene.String()
            node_args["page_size"] = graphene.Int()

        #if isinstance(filters, FilterSet):
        if filters and hasattr(filters, "FILTER_OBJECT_TYPES"):
            filter_obj = filters
            node_args["filters"] = filter_obj
        elif filters:
            filter_obj = create_filter(class_name, model_, filters)()
            node_args["filters"] = filter_obj
        else:
            filter_obj = None

        self.node_resolve_func = self.resolve(
            class_name,
            model_,
            order_by,
            filter_obj,
            filter_required,
            filter_dependencies,
            pagination_obj
        )

        if not return_type:
            return_type = graphene.Field

        self.node = return_type(
            node_schema,
            **node_args
        )

    @staticmethod
    def resolve(class_name, model, order_by, filter_obj, filter_required, filter_dependencies, pagination_obj):
        def resolve_func(self, info, filters=None, page_key=None, page_size=settings.DEFAULT_PAGE_SIZE):
            with SessionManager(session_cls=SessionLocal) as session:
                query = session.query(model)
                if isinstance(order_by, Iterable):
                    query = query.order_by(*order_by)
                else:
                    query = query.order_by(order_by)

                if filters:
                    if not filter_obj:
                        raise GraphQLError(f'{class_name} is not filterable')

                    #if filter_dependencies:
                    #    #TODO!
                    #    #import pdb;pdb.set_trace()

                    return filter_obj.filter(info, query, filters).one()

                elif filter_required:
                    raise GraphQLError(f'{class_name} requires filters')

                return query.first()
        return resolve_func


class QueryNodeMany(QueryNodeOne):
    def __init__(self, *args, **kwargs):
        super(QueryNodeMany, self).__init__(*args, **kwargs)

    @staticmethod
    def resolve(class_name, model, order_by, filter_obj, filter_required, filter_dependencies, pagination_obj):
        def resolve_func(self, info, filters=None, page_key=None, page_size=settings.DEFAULT_PAGE_SIZE):
            with SessionManager(session_cls=SessionLocal) as session:
                query = session.query(model)
                if isinstance(order_by, Iterable):
                    query = query.order_by(*order_by)
                else:
                    query = query.order_by(order_by)

                if filters:
                    if not filter_obj:
                        raise GraphQLError(f'{class_name} is not filterable')

                    # if filter_dependencies:
                    #     #TODO
                    #     #import pdb;pdb.set_trace()

                    query = filter_obj.filter(info, query, filters)

                elif filter_required:
                    raise GraphQLError(f'{class_name} requires filters')

                if pagination_obj:
                    query = pagination_obj.create_paginated_result(query, page_key, page_size)

                return query

        return resolve_func


class QueryGenerator(graphene.ObjectType):
    def __new__(cls, name, bases, dct):
        node_dict = {}
        for key_id, key_val in dct.items():
            if isinstance(dct[key_id], (QueryNodeOne,)):
                node_dict[key_id] = dct[key_id].node
                node_dict[f"resolve_{key_id}"] = dct[key_id].node_resolve_func
            else:
                node_dict[key_id] = dct[key_id]

        return type(f"{name}", (graphene.ObjectType, ), node_dict)
