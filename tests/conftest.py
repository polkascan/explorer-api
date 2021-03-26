# import os
# import sys
#
# import pytest
#
# from sqlalchemy.ext.compiler import compiles
# from sqlalchemy.dialects.mysql import MEDIUMINT, INTEGER, TEXT, TINYINT
#
# from fastapi.testclient import TestClient
#
#
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#
# if not os.path.exists(".test.env"):
#     raise Exception("Please specify a .test.env file")
#
# from app import session
# from app.db import BaseModel
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
# @pytest.fixture
# def client():
#     from app import app
#     with TestClient(app) as client:
#         BaseModel.metadata.drop_all(bind=session.engine)
#         BaseModel.metadata.create_all(bind=session.engine)
#         import pdb;pdb.set_trace()
#         yield client
