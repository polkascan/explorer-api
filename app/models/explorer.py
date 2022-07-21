#  Polkascan PRE Explorer API
#
#  Copyright 2018-2021 openAware BV (NL).
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

from app.db import BaseModel

from .field_types import INTEGER, NUMERIC, TINYINT, HashBinary, HashVarBinary, UTCDateTime


class Block(BaseModel):
    __tablename__ = 'explorer_block'

    number = sa.Column(INTEGER(unsigned=True, display_width=11), primary_key=True, autoincrement=False, nullable=False, index=True)
    parent_number = sa.Column(INTEGER(unsigned=True, display_width=11), nullable=True)
    hash = sa.Column(HashBinary(32), nullable=False, index=True)
    parent_hash = sa.Column(HashBinary(32), nullable=False, index=True)
    state_root = sa.Column(HashBinary(32), nullable=False)
    extrinsics_root = sa.Column(HashBinary(32), nullable=False)
    datetime = sa.Column(UTCDateTime(timezone=True), nullable=True)
    author_authority_index = sa.Column(INTEGER(unsigned=True, display_width=11), nullable=True)
    author_slot_number = sa.Column(NUMERIC(precision=65, scale=0, unsigned=True), nullable=True)
    author_account_id = sa.Column(HashBinary(32), nullable=True, index=True)
    count_extrinsics = sa.Column(INTEGER(unsigned=True, display_width=11), nullable=False)
    count_events = sa.Column(INTEGER(unsigned=True, display_width=11), nullable=False)
    count_logs = sa.Column(INTEGER(unsigned=True, display_width=11), nullable=False)
    total_fee = sa.Column(NUMERIC(precision=65, scale=0, unsigned=True), nullable=True)
    total_fee_treasury = sa.Column(NUMERIC(precision=65, scale=0), nullable=True)
    total_fee_block_author = sa.Column(NUMERIC(precision=65, scale=0), nullable=True)
    total_tip = sa.Column(NUMERIC(precision=65, scale=0, unsigned=True), nullable=True)
    total_weight = sa.Column(NUMERIC(precision=65, scale=0, unsigned=True), nullable=True)
    total_weight_normal = sa.Column(NUMERIC(precision=65, scale=0, unsigned=True), nullable=True)
    total_weight_operational = sa.Column(NUMERIC(precision=65, scale=0, unsigned=True), nullable=True)
    total_weight_mandatory = sa.Column(NUMERIC(precision=65, scale=0, unsigned=True), nullable=True)
    spec_name = sa.Column(sa.String(64), nullable=False)
    spec_version = sa.Column(INTEGER(unsigned=True, display_width=11), nullable=False)
    complete = sa.Column(TINYINT(display_width=1), nullable=False, index=True)


class Event(BaseModel):
    __tablename__ = 'explorer_event'

    block_number = sa.Column(INTEGER(unsigned=True, display_width=11), primary_key=True, autoincrement=False, nullable=False, index=True)
    event_idx = sa.Column(INTEGER(unsigned=True, display_width=11), primary_key=True, autoincrement=False, nullable=False, index=True)
    extrinsic_idx = sa.Column(INTEGER(unsigned=True, display_width=11), nullable=True, index=True)
    event = sa.Column(HashBinary(2), nullable=True)
    event_module = sa.Column(sa.String(255), nullable=True, index=True)
    event_name = sa.Column(sa.String(255), nullable=True, index=True)
    phase_idx = sa.Column(INTEGER(unsigned=True, display_width=11), nullable=True)
    phase_name = sa.Column(sa.String(255), nullable=True)
    attributes = sa.Column(sa.JSON(), nullable=True)
    topics = sa.Column(sa.JSON(), nullable=True)
    block_datetime = sa.Column(UTCDateTime(timezone=True), nullable=True)
    block_hash = sa.Column(HashBinary(32), nullable=False, index=True)
    spec_name = sa.Column(sa.String(64), nullable=True)
    spec_version = sa.Column(INTEGER(unsigned=True, display_width=11), nullable=True)
    complete = sa.Column(TINYINT(display_width=1), nullable=False, index=True)


class Extrinsic(BaseModel):
    __tablename__ = 'explorer_extrinsic'

    block_number = sa.Column(INTEGER(unsigned=True, display_width=11), primary_key=True, autoincrement=False, nullable=False, index=True)
    extrinsic_idx = sa.Column(INTEGER(unsigned=True, display_width=11), primary_key=True, autoincrement=False, nullable=False, index=True)
    hash = sa.Column(HashBinary(32), nullable=True, index=True)
    version = sa.Column(INTEGER(unsigned=True, display_width=11), nullable=True)
    version_info = sa.Column(HashBinary(1), nullable=True)
    call = sa.Column(HashBinary(2), nullable=True)
    call_module = sa.Column(sa.String(255), nullable=True, index=True)
    call_name = sa.Column(sa.String(255), nullable=True, index=True)
    call_arguments = sa.Column(sa.JSON(), nullable=True)
    call_hash = sa.Column(HashBinary(32), nullable=True)
    signed = sa.Column(TINYINT(display_width=1), nullable=True, index=True)
    signature = sa.Column(HashVarBinary(65), nullable=True)
    signature_version = sa.Column(sa.String(16), nullable=True)
    multi_address_type = sa.Column(sa.String(16), nullable=True)
    multi_address_account_id = sa.Column(HashBinary(32), nullable=True, index=True)
    multi_address_account_index = sa.Column(INTEGER(unsigned=True, display_width=11), nullable=True)
    multi_address_raw = sa.Column(HashVarBinary(255), nullable=True)
    multi_address_address_32 = sa.Column(HashBinary(32), nullable=True)
    multi_address_address_20 = sa.Column(HashBinary(20), nullable=True)
    extrinsic_length = sa.Column(INTEGER(unsigned=True, display_width=11), nullable=True)
    nonce = sa.Column(INTEGER(unsigned=True, display_width=11), nullable=True)
    era = sa.Column(sa.JSON(), nullable=True)
    era_immortal = sa.Column(TINYINT(display_width=1), nullable=True)
    era_birth = sa.Column(INTEGER(unsigned=True, display_width=11), nullable=True)
    era_death = sa.Column(INTEGER(unsigned=True, display_width=11), nullable=True)
    tip = sa.Column(NUMERIC(precision=65, scale=0, unsigned=True), nullable=True)
    block_datetime = sa.Column(UTCDateTime(timezone=True), nullable=True)
    block_hash = sa.Column(HashBinary(32), nullable=False, index=True)
    spec_name = sa.Column(sa.String(64), nullable=True)
    spec_version = sa.Column(INTEGER(unsigned=True, display_width=11), nullable=True)
    complete = sa.Column(TINYINT(display_width=1), nullable=False, index=True)


class Transfer(BaseModel):
    __tablename__ = 'explorer_transfer'

    block_number = sa.Column(INTEGER(unsigned=True, display_width=11), primary_key=True, autoincrement=False, nullable=False, index=True)
    event_idx = sa.Column(INTEGER(unsigned=True, display_width=11), primary_key=True, autoincrement=False, nullable=False, index=True)
    extrinsic_idx = sa.Column(INTEGER(unsigned=True, display_width=11), nullable=True, index=True)
    from_multi_address_type = sa.Column(sa.String(16), nullable=True)
    from_multi_address_account_id = sa.Column(HashBinary(32), nullable=True, index=True)
    from_multi_address_account_index = sa.Column(INTEGER(unsigned=True, display_width=11), nullable=True)
    from_multi_address_raw = sa.Column(HashVarBinary(255), nullable=True)
    from_multi_address_address_32 = sa.Column(HashBinary(32), nullable=True)
    from_multi_address_address_20 = sa.Column(HashBinary(20), nullable=True)
    to_multi_address_type = sa.Column(sa.String(16), nullable=True)
    to_multi_address_account_id = sa.Column(HashBinary(32), nullable=True, index=True)
    to_multi_address_account_index = sa.Column(INTEGER(unsigned=True, display_width=11), nullable=True)
    to_multi_address_raw = sa.Column(HashVarBinary(255), nullable=True)
    to_multi_address_address_32 = sa.Column(HashBinary(32), nullable=True)
    to_multi_address_address_20 = sa.Column(HashBinary(20), nullable=True)
    value = sa.Column(NUMERIC(precision=65, scale=0, unsigned=True), nullable=True)
    block_datetime = sa.Column(UTCDateTime(timezone=True), nullable=True)
    block_hash = sa.Column(HashBinary(32), nullable=False, index=True)
    complete = sa.Column(sa.Boolean(), nullable=False, index=True)


class Log(BaseModel):
    __tablename__ = 'explorer_log'

    block_number = sa.Column(INTEGER(unsigned=True, display_width=11), primary_key=True, autoincrement=False, nullable=False, index=True)
    log_idx = sa.Column(INTEGER(unsigned=True, display_width=11), primary_key=True, autoincrement=False, nullable=False, index=True)
    type_id = sa.Column(INTEGER(unsigned=True, display_width=11), index=True)
    type_name = sa.Column(sa.String(255), nullable=True, index=True)
    data = sa.Column(sa.JSON(), nullable=True)
    block_datetime = sa.Column(UTCDateTime(timezone=True), nullable=True)
    block_hash = sa.Column(HashBinary(32), nullable=False, index=True)
    spec_name = sa.Column(sa.String(64), nullable=True)
    spec_version = sa.Column(INTEGER(unsigned=True, display_width=11), nullable=True)
    complete = sa.Column(sa.Boolean(), nullable=False, index=True)


class TaggedAccount(BaseModel):
    __tablename__ = 'explorer_tagged_account'

    account_id = sa.Column(HashBinary(32), primary_key=True, autoincrement=False, nullable=False, index=True)
    tag_name = sa.Column(sa.String(255), nullable=False)
    tag_type = sa.Column(sa.String(255), nullable=False, index=True)
    tag_sub_type = sa.Column(sa.String(255), nullable=True)
    risk_level = sa.Column(TINYINT(display_width=1), nullable=True, index=True)
    risk_level_verbose = sa.Column(sa.String(255), nullable=True)
    originator_info = sa.Column(sa.JSON(), nullable=True)
    beneficiary_info = sa.Column(sa.JSON(), nullable=True)




