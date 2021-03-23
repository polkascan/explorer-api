# import graphene
# import pytest
#
# from sqlalchemy import create_engine
#
# from sqlalchemy.orm import sessionmaker
#
# from sqlalchemy.ext.compiler import compiles
# from sqlalchemy.dialects.mysql import MEDIUMINT, INTEGER, TEXT, TINYINT
#
# from fastapi.testclient import TestClient
# from fastapi import FastAPI
# from starlette_graphene3 import GraphQLApp
#
# from app.db import BaseModel
# from app.settings import settings
# from app.api.graphql.queries import GraphQLQueries
# from app.api.graphql.subscriptions import Subscription
#
#
# @compiles(TINYINT, 'sqlite')
# def compile_TINYINT(element, compiler, **kw):
#     """ Handles mysql TINYINT datatype as Integer in sqlite.  """
#     return compiler.visit_integer(element, **kw)
#
# @compiles(MEDIUMINT, 'sqlite')
# def compile_MEDIUMINT(element, compiler, **kw):
#     """ Handles mysql MEDIUMINT datatype as Integer in sqlite.  """
#     return compiler.visit_integer(element, **kw)
#
# @compiles(INTEGER, 'sqlite')
# def compile_INTEGER(element, compiler, **kw):
#     """ Handles mysql INTEGER datatype as Integer in sqlite.  """
#     return compiler.visit_integer(element, **kw)
#
# @compiles(TEXT, 'sqlite')
# def compile_TEXT(element, compiler, **kw):
#     """ Handles mysql TEXT datatype as text in sqlite.  """
#     return compiler.visit_text(element, **kw)
#
# @compiles(TEXT, 'sqlite')
# def compile_HASH(element, compiler, **kw):
#     """ Handles mysql BIN datatype as text in sqlite.  """
#     return compiler.visit_binary(element, **kw)
#
# @compiles(TEXT, 'sqlite')
# def compile_VARHASH(element, compiler, **kw):
#     """ Handles mysql VARBIN datatype as text in sqlite.  """
#     return compiler.visit_VARBINARY(element, **kw)
#
#
# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# BaseModel.metadata.create_all(bind=engine)
#
# #app = FastAPI(title=settings.PROJECT_NAME)
# #graphql_app = GraphQLApp(schema=graphene.Schema(query=GraphQLQueries, subscription=Subscription))
# #app.add_route("/graphql", graphql_app)
# #app.add_websocket_route("/graphql-ws", graphql_app)
# from app import app
#
#
# @pytest.fixture
# def client():
#     with TestClient(app) as client:
#         yield client
