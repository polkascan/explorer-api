# from app.models import Base
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
#
#
# #https://stackoverflow.com/questions/10558965/how-do-i-change-column-type-on-sqlalchemy-declarative-model-dynamically
# #from sqlalchemy.dialects.sqlite import INTEGER, SMALLINT, TEXT
# from app.models import field_types
# # field_types.INTEGER = INTEGER
# # field_types.TINYINT = SMALLINT
# # field_types.HashBinary = TEXT
# # field_types.HashVarBinary = TEXT
#
# from sqlalchemy.ext.compiler import compiles
# from sqlalchemy.dialects.mysql import MEDIUMINT, INTEGER, TEXT
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
# import pytest
#
# from starlette.testclient import TestClient
#
# from app import app
#
#
# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
#
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# Base.metadata.create_all(bind=engine)
#
# import pdb;pdb.set_trace()
#
# @pytest.fixture
# def client():
#     with TestClient(app) as client:
#         yield client
