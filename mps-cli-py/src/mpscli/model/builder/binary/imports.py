# mpscli/model/builder/binary/imports.py
#
# Standalone import-loading helper.
# The canonical implementation lives in SModelBuilderBinaryPersistency._load_imports().
# This module provides the same logic for external call sites.

from mpscli.model.builder.binary.model_input_stream import ModelInputStream

_V2 = ModelInputStream.STREAM_ID_V2
_V3 = ModelInputStream.STREAM_ID_V3


def load_imports(reader: ModelInputStream, builder, version: int) -> None:
    """
    Reads the imports section:

        u32  count
        for each:
            model_reference  (kind byte + optional uuid + name string)
            [V2 only] i32    (import element version, compatibility field)

    Populates builder.index_2_imported_model_uuid[str(i+1)].
    """
    count = reader.read_u32()

    for i in range(count):
        kind = reader.read_u8()

        if kind == 0x70:  # NULL model ref
            model_id = None
        elif kind == 0x09:  # MODELREF_INDEX
            reader.read_u32()
            model_id = None
        else:
            # Full model reference
            model_id_kind = reader.read_u8()

            if model_id_kind == 0x48:  # uuid-based
                uuid = reader.read_uuid()
                model_id = f"r:{uuid[0]:016x}{uuid[1]:016x}"
            elif model_id_kind == 0x70:  # NULL id
                model_id = ""
            else:
                raise RuntimeError(
                    f"Unsupported model_id_kind 0x{model_id_kind:02X} "
                    f"at pos {reader.tell()}"
                )

            reader.read_string()  # model name

        if version == _V2:
            reader.read_i32()  # V2 import version field

        builder.index_2_imported_model_uuid[str(i + 1)] = model_id or ""
