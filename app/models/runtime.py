#  Polkascan Harvester
#
#  Copyright 2018-2020 Stichting Polkascan (Polkascan Foundation).
#  This file is part of Polkascan.
#
#  Polkascan is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Polkascan is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Polkascan. If not, see <http://www.gnu.org/licenses/>.
import sqlalchemy as sa
from sqlalchemy import BLOB

from app import settings
from app.db import BaseModel
from app.models.field_types import HashBinary


class CodecBlockExtrinsic(BaseModel):
    __tablename__ = 'codec_block_extrinsic'
    # __table_args__ = (Index('ix_codec_block_extrinsic_block_idx', "block_number", "extrinsic_idx"),)
    __table_args__ = {"schema": settings.DB_HARVESTER_NAME}

    block_hash = sa.Column(HashBinary(32), primary_key=True, index=True, nullable=False)
    extrinsic_idx = sa.Column(sa.Integer(), primary_key=True, index=True, nullable=False)
    block_number = sa.Column(sa.Integer(), nullable=False, index=True)

    scale_type = sa.Column(sa.String(255))

    call_module = sa.Column(sa.String(255), nullable=True, index=True)
    call_name = sa.Column(sa.String(255), nullable=True, index=True)
    signed = sa.Column(sa.SmallInteger(), index=True)

    data = sa.Column(sa.JSON())

    complete = sa.Column(sa.Boolean(), nullable=False, default=False, index=True)

    def __repr__(self):
        return "<{}(block_hash={}, extrinsic_idx={})>".format(
            self.__class__.__name__, self.block_hash.hex(), self.extrinsic_idx
        )


class CodecBlockEvent(BaseModel):
    __tablename__ = 'codec_block_event'
    # __table_args__ = (Index('ix_codec_block_event_block_idx', "block_number", "event_idx"),)
    __table_args__ = {"schema": settings.DB_HARVESTER_NAME}

    block_hash = sa.Column(HashBinary(32), primary_key=True, index=True, nullable=False)
    event_idx = sa.Column(sa.Integer(), primary_key=True, index=True, nullable=False)
    block_number = sa.Column(sa.Integer(), nullable=False, index=True)

    scale_type = sa.Column(sa.String(255))

    event_module = sa.Column(sa.String(255), nullable=True, index=True)
    event_name = sa.Column(sa.String(255), nullable=True, index=True)
    extrinsic_idx = sa.Column(sa.Integer(), index=True)

    data = sa.Column(sa.JSON())

    complete = sa.Column(sa.Boolean(), nullable=False, default=False, index=True)

    def __repr__(self):
        return "<{}(block_hash={}, event_idx={})>".format(
            self.__class__.__name__, self.block_hash.hex(), self.event_idx
        )


class CodecBlockHeaderDigestLog(BaseModel):
    __tablename__ = 'codec_block_header_digest_log'
    __table_args__ = {"schema": settings.DB_HARVESTER_NAME}

    block_hash = sa.Column(HashBinary(32), primary_key=True, index=True, nullable=False)
    log_idx = sa.Column(sa.Integer(), primary_key=True, index=True, nullable=False)

    block_number = sa.Column(sa.Integer(), nullable=False, index=True)

    scale_type = sa.Column(sa.String(255))
    data = sa.Column(sa.JSON())

    complete = sa.Column(sa.Boolean(), nullable=False, default=False, index=True)

    def __repr__(self):
        return "<{}(block_hash={}, log_idx={})>".format(self.__class__.__name__, self.block_hash.hex(), self.log_idx)


class CodecBlockStorage(BaseModel):
    __tablename__ = 'codec_block_storage'
    __table_args__ = {"schema": settings.DB_HARVESTER_NAME}

    block_hash = sa.Column(HashBinary(32), primary_key=True, index=True, nullable=False)
    storage_key = sa.Column(sa.VARBINARY(128), primary_key=True, index=True)

    block_number = sa.Column(sa.Integer(), nullable=False, index=True)

    scale_type = sa.Column(sa.String(255))

    storage_module = sa.Column(sa.String(255), nullable=True, index=True)
    storage_name = sa.Column(sa.String(255), nullable=True, index=True)

    data = sa.Column(sa.JSON())

    complete = sa.Column(sa.Boolean(), nullable=False, default=False, index=True)

    def __repr__(self):
        return "<{}(storage_key={}, block_hash={})>".format(
            self.__class__.__name__, self.storage_key.hex(), self.block_hash.hex()
        )


class CodecMetadata(BaseModel):
    __tablename__ = 'codec_metadata'
    __table_args__ = {"schema": settings.DB_HARVESTER_NAME}

    spec_name = sa.Column(sa.String(64), nullable=False, primary_key=True, index=True)
    spec_version = sa.Column(sa.Integer(), nullable=False, primary_key=True, index=True)

    scale_type = sa.Column(sa.String(255))
    data = sa.Column(sa.JSON())

    complete = sa.Column(sa.Boolean(), nullable=False, default=False, index=True)

    def __repr__(self):
        return "<{}(spec_name={}, spec_version={})>".format(
            self.__class__.__name__, self.spec_name, self.spec_version
        )


class Runtime(BaseModel):
    __tablename__ = 'runtime'
    __table_args__ = {"schema": settings.DB_HARVESTER_NAME}

    spec_name = sa.Column(sa.String(255), nullable=False, primary_key=True, index=True)
    spec_version = sa.Column(sa.Integer(), nullable=False, primary_key=True, index=True)
    impl_name = sa.Column(sa.String(255))
    impl_version = sa.Column(sa.Integer())
    authoring_version = sa.Column(sa.Integer())
    count_call_functions = sa.Column(sa.Integer(), default=0, nullable=False)
    count_events = sa.Column(sa.Integer(), default=0, nullable=False)
    count_pallets = sa.Column(sa.Integer(), default=0, nullable=False)
    count_storage_functions = sa.Column(sa.Integer(), default=0, nullable=False)
    count_constants = sa.Column(sa.Integer(), nullable=False, server_default='0')
    count_errors = sa.Column(sa.Integer(), nullable=False, server_default='0')


class RuntimeCall(BaseModel):
    __tablename__ = 'runtime_call'
    __table_args__ = {"schema": settings.DB_HARVESTER_NAME}

    spec_name = sa.Column(sa.String(255), nullable=False, primary_key=True, index=True)
    spec_version = sa.Column(sa.Integer(), nullable=False, primary_key=True, index=True)
    pallet = sa.Column(sa.String(255), nullable=False, primary_key=True, index=True)
    call_name = sa.Column(sa.String(255), nullable=False, primary_key=True, index=True)
    pallet_call_idx = sa.Column(sa.Integer(), nullable=False)
    lookup = sa.Column(HashBinary(2), index=True, nullable=False)
    documentation = sa.Column(sa.Text())
    count_arguments = sa.Column(sa.Integer(), nullable=False)


class RuntimeCallArgument(BaseModel):
    __tablename__ = 'runtime_call_argument'
    __table_args__ = {"schema": settings.DB_HARVESTER_NAME}

    spec_name = sa.Column(sa.String(255), nullable=False, primary_key=True, index=True)
    spec_version = sa.Column(sa.Integer(), nullable=False, primary_key=True, index=True)
    pallet = sa.Column(sa.String(255), nullable=False, primary_key=True, index=True)
    call_name = sa.Column(sa.String(255), nullable=False, primary_key=True, index=True)
    call_argument_idx = sa.Column(sa.Integer(), primary_key=True, index=True)
    name = sa.Column(sa.String(255), index=True)
    scale_type = sa.Column(sa.String(255))


class RuntimeConstant(BaseModel):
    __tablename__ = 'runtime_constant'
    __table_args__ = {"schema": settings.DB_HARVESTER_NAME}

    spec_name = sa.Column(sa.String(255), nullable=False, primary_key=True, index=True)
    spec_version = sa.Column(sa.Integer(), nullable=False, primary_key=True, index=True)
    pallet = sa.Column(sa.String(255), nullable=False, primary_key=True, index=True)
    constant_name = sa.Column(sa.String(255), primary_key=True, index=True)
    pallet_constant_idx = sa.Column(sa.Integer(), nullable=False, index=True)
    scale_type = sa.Column(sa.String(255))
    value = sa.Column(sa.JSON())
    documentation = sa.Column(sa.Text())


class RuntimeErrorMessage(BaseModel):
    __tablename__ = 'runtime_error'
    __table_args__ = {"schema": settings.DB_HARVESTER_NAME}

    spec_name = sa.Column(sa.String(255), nullable=False, primary_key=True, index=True)
    spec_version = sa.Column(sa.Integer(), nullable=False, primary_key=True, index=True)
    pallet = sa.Column(sa.String(255), nullable=False, primary_key=True, index=True)
    error_name = sa.Column(sa.String(255), primary_key=True, index=True)
    pallet_idx = sa.Column(sa.Integer(), index=True, nullable=False)
    error_idx = sa.Column(sa.Integer(), index=True, nullable=False)
    documentation = sa.Column(sa.Text())


class RuntimeEvent(BaseModel):
    __tablename__ = 'runtime_event'
    __table_args__ = {"schema": settings.DB_HARVESTER_NAME}

    spec_name = sa.Column(sa.String(255), nullable=False, primary_key=True, index=True)
    spec_version = sa.Column(sa.Integer(), nullable=False, primary_key=True, index=True)
    pallet = sa.Column(sa.String(255), nullable=False, primary_key=True, index=True)
    event_name = sa.Column(sa.String(255), primary_key=True, index=True)
    pallet_event_idx = sa.Column(sa.Integer(), nullable=False)
    lookup = sa.Column(HashBinary(2), index=True, nullable=False)
    documentation = sa.Column(sa.Text())
    count_attributes = sa.Column(sa.Integer(), nullable=False)


class RuntimeEventAttribute(BaseModel):
    __tablename__ = 'runtime_event_attribute'
    __table_args__ = {"schema": settings.DB_HARVESTER_NAME}

    spec_name = sa.Column(sa.String(255), nullable=False, primary_key=True, index=True)
    spec_version = sa.Column(sa.Integer(), nullable=False, primary_key=True, index=True)
    pallet = sa.Column(sa.String(255), nullable=False, primary_key=True, index=True)
    event_name = sa.Column(sa.String(255), primary_key=True, index=True)
    event_attribute_idx = sa.Column(sa.Integer(), nullable=False, index=True, primary_key=True)
    scale_type = sa.Column(sa.String(255))


class RuntimePallet(BaseModel):
    __tablename__ = 'runtime_pallet'
    __table_args__ = {"schema": settings.DB_HARVESTER_NAME}

    spec_name = sa.Column(sa.String(255), nullable=False, primary_key=True, index=True)
    spec_version = sa.Column(sa.Integer(), nullable=False, primary_key=True, index=True)
    pallet = sa.Column(sa.String(255), nullable=False, primary_key=True, index=True)
    prefix = sa.Column(sa.String(255))
    name = sa.Column(sa.String(255))
    count_call_functions = sa.Column(sa.Integer(), nullable=False)
    count_storage_functions = sa.Column(sa.Integer(), nullable=False)
    count_events = sa.Column(sa.Integer(), nullable=False)
    count_constants = sa.Column(sa.Integer(), nullable=False, server_default='0')
    count_errors = sa.Column(sa.Integer(), nullable=False, server_default='0')


class RuntimeStorage(BaseModel):
    __tablename__ = 'runtime_storage'
    __table_args__ = {"schema": settings.DB_HARVESTER_NAME}

    spec_name = sa.Column(sa.String(255), nullable=False, primary_key=True, index=True)
    spec_version = sa.Column(sa.Integer(), nullable=False, primary_key=True, index=True)
    pallet = sa.Column(sa.String(255), nullable=False, primary_key=True, index=True)
    storage_name = sa.Column(sa.String(255), nullable=False, primary_key=True, index=True)
    pallet_storage_idx = sa.Column(sa.Integer(), nullable=False)
    #default = sa.Column(BLOB())
    modifier = sa.Column(sa.String(64))
    key_prefix_pallet = sa.Column(HashBinary(16))
    key_prefix_name = sa.Column(HashBinary(16))
    key1_scale_type = sa.Column(sa.String(255))
    key1_hasher = sa.Column(sa.String(255))
    key2_scale_type = sa.Column(sa.String(255))
    key2_hasher = sa.Column(sa.String(255))
    value_scale_type = sa.Column(sa.String(255))
    is_linked = sa.Column(sa.Boolean())
    documentation = sa.Column(sa.Text())


class RuntimeType(BaseModel):
    __tablename__ = 'runtime_type'
    __table_args__ = {"schema": settings.DB_HARVESTER_NAME}

    spec_name = sa.Column(sa.String(255), nullable=False, primary_key=True, index=True)
    spec_version = sa.Column(sa.Integer(), nullable=False, primary_key=True, index=True)
    scale_type = sa.Column(sa.String(255), nullable=False, primary_key=True, index=True)
    decoder_class = sa.Column(sa.String(255), nullable=True)
    is_core_primitive = sa.Column(sa.Boolean())
    is_runtime_primitive = sa.Column(sa.Boolean())
