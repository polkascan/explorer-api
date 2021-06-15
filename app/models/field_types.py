import binascii
import codecs
from datetime import timezone

from graphene_sqlalchemy.converter import convert_sqlalchemy_type
from graphene import String

import sqlalchemy as sa
from sqlalchemy.dialects.mysql import INTEGER, NUMERIC, TINYINT


class UTCDateTime(sa.types.TypeDecorator):

    impl = sa.types.DateTime

    def process_bind_param(self, value, engine):
        if value is None:
            return
        if value.utcoffset() is None:
            raise ValueError(
                'Got naive datetime while timezone-aware is expected'
            )
        return value.astimezone(timezone.utc)

    def result_processor(self, dialect, coltype):
        """Return a processor that encodes hex values."""
        def process(value):
            return value.replace(tzinfo=timezone.utc)
        return process

    def adapt(self, impltype):
        """Produce an adapted form of this type, given an impl class."""
        return UTCDateTime()


class HashBinary(sa.types.BINARY):
    """Extend BINARY to handle hex strings."""

    impl = sa.types.BINARY

    def bind_processor(self, dialect):
        """Return a processor that decodes hex values."""
        def process(value):
            try:
                return value and codecs.decode(value[2:], 'hex') or None
            except binascii.Error:
                raise Exception(f"Invalid HEX input: {value}")
        return process

    def result_processor(self, dialect, coltype):
        """Return a processor that encodes hex values."""
        def process(value):
            try:
                return value and f"0x{codecs.encode(value, 'hex').decode('utf-8')}" or None
            except binascii.Error:
                raise Exception(f"Invalid HEX input: {value}")
        return process

    def adapt(self, impltype):
        """Produce an adapted form of this type, given an impl class."""
        return HashBinary()


class HashVarBinary(sa.types.VARBINARY):
    """Extend VARBINARY to handle hex strings."""

    impl = sa.types.VARBINARY

    def bind_processor(self, dialect):
        """Return a processor that decodes hex values."""
        def process(value):
            try:
                return value and codecs.decode(value[2:], 'hex') or None
            except binascii.Error:
                raise Exception(f"Invalid HEX input: {value}")
        return process

    def result_processor(self, dialect, coltype):
        """Return a processor that encodes hex values."""
        def process(value):
            try:
                return value and f"0x{codecs.encode(value, 'hex').decode('utf-8')}" or None
            except binascii.Error:
                raise Exception(f"Invalid HEX input: {value}")
        return process

    def adapt(self, impltype):
        """Produce an adapted form of this type, given an impl class."""
        return HashVarBinary()


@convert_sqlalchemy_type.register(UTCDateTime)
def convert_column_to_datetime(type, column, registry=None):
    from graphene.types.datetime import DateTime
    return DateTime


@convert_sqlalchemy_type.register(HashBinary)
@convert_sqlalchemy_type.register(HashVarBinary)
def convert_column_to_string(type, column, registry=None):
    return String
