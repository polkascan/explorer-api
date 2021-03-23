import codecs

import sqlalchemy as sa
from sqlalchemy.dialects.mysql import INTEGER, NUMERIC, TINYINT


class HashBinary(sa.types.BINARY):
    """Extend BINARY to handle hex strings."""

    impl = sa.types.BINARY

    # def bind_processor(self, dialect):
    #     """Return a processor that decodes hex values."""
    #     # def process(value):
    #     #     return value and codecs.decode(value, 'hex') or None
    #     # return process

    def result_processor(self, dialect, coltype):
        """Return a processor that encodes hex values."""
        def process(value):
            return value and f"0x{codecs.encode(value, 'hex').decode('utf-8')}" or None
        return process

    def adapt(self, impltype):
        """Produce an adapted form of this type, given an impl class."""
        return HashBinary()


class HashVarBinary(sa.types.VARBINARY):
    """Extend VARBINARY to handle hex strings."""

    impl = sa.types.VARBINARY

    # def bind_processor(self, dialect):
    #     """Return a processor that decodes hex values."""
    #     def process(value):
    #         return value and codecs.decode(value, 'hex') or None
    #     return process

    def result_processor(self, dialect, coltype):
        """Return a processor that encodes hex values."""
        def process(value):
            return value and f"0x{codecs.encode(value, 'hex').decode('utf-8')}" or None
        return process

    def adapt(self, impltype):
        """Produce an adapted form of this type, given an impl class."""
        return HashVarBinary()

