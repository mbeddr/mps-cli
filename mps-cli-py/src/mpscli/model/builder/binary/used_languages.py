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
    V2 (loadUsedLanguagesV2):
        u16  count
        for each: uuid (2×u64) + string name
        NOTE: no version int per entry in V2.

    V3 (loadUsedLanguagesV3):
        u16  count
        for each: uuid (2×u64) + string name + i32 import_version
    """
    count = reader.read_u16()

    for _ in range(count):
        reader.read_uuid()  # language uuid
        reader.read_string()  # language name
        if version == _V3:
            reader.read_i32()  # import version (V3 only)
