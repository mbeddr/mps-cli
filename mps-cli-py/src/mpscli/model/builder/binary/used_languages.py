# mpscli/model/builder/binary/used_languages.py
#
# Standalone helper for reading the used-languages section.
# The canonical implementation lives in SModelBuilderBinaryPersistency.
# This module exists for call sites that import it directly.

from mpscli.model.builder.binary.model_input_stream import ModelInputStream

_V2 = ModelInputStream.STREAM_ID_V2
_V3 = ModelInputStream.STREAM_ID_V3


def load_used_languages(reader: ModelInputStream, version: int) -> None:
    """
    V2 format:
        u16  count
        for each: uuid + string name
        there is no version int per entry in V2 format.

    V3 format:
        u16  count
        for each: uuid + string name + i32 import_version
    """
    count = reader.read_u16()

    for _ in range(count):
        # language uuid
        reader.read_uuid()
        # language name
        reader.read_string()
        if version == _V3:
            # import version (which is present in V3 format only)
            reader.read_i32()
