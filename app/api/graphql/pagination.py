import graphene

from sqlakeyset import get_page

from app import settings


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


def CreatePaginatedType(schema):
    class PaginatedType(AbstractPaginatedType):
        page_info = graphene.Field(PaginationType)
        objects = graphene.List(schema)

    return PaginatedType
