# import os
# import datetime
# import pytest
#
# from sqlalchemy.ext.compiler import compiles
# from sqlalchemy.dialects.mysql import MEDIUMINT, INTEGER, TEXT, TINYINT
#
# from fastapi.testclient import TestClient
#
# from app.models.explorer import Block
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
# def create_blocks(session):
#     sess = session.SessionLocal()
#     prev_nr = None
#     for nr in range(1):
#         Block(
#             number=1,
#             parent_number=prev_nr,
#             hash="123".encode("utf8"),
#             parent_hash="123".encode("utf8"),
#             state_root="123".encode("utf8"),
#             extrinsics_root="123".encode("utf8"),
#             datetime=datetime.datetime.now().replace(tzinfo=datetime.timezone.utc),
#             author_authority_index=1,
#             author_slot_number=1,
#             author_account_id="123".encode("utf8"),
#             count_extrinsics=1,
#             count_events=1,
#             count_logs=1,
#             total_fee=1,
#             total_fee_treasury=1,
#             total_fee_block_author=1,
#             total_tip=1,
#             total_weight=1,
#             total_weight_normal=1,
#             total_weight_operational=1,
#             total_weight_mandatory=1,
#             spec_name="123",
#             spec_version=1,
#             complete=1
#         ).save(sess)
#     sess.commit()
#
#
# @pytest.fixture
# def client():
#     from app import app
#     with TestClient(app) as client:
#         BaseModel.metadata.drop_all(bind=session.engine)
#         BaseModel.metadata.create_all(bind=session.engine)
#         create_blocks(session)
#         import pdb;pdb.set_trace()
#         yield client
