from mpscli.model.builder.binary.model_input_stream import ModelInputStream
from mpscli.model.builder.binary.constants import (
    NULL,
    MODELREF_INDEX,
    MODELID_REGULAR,
    MODELID_FOREIGN,
    STREAM_ID_V2,
)
from mpscli.model.builder.binary.uuid_utils import uuid_str

_V2 = STREAM_ID_V2


def load_imports(reader: ModelInputStream, builder, version: int) -> None:
    # mirrors BinaryPersistence.loadImports() in
    # https://github.com/JetBrains/MPS/blob/1970ede7678695d2201b0773ac7cfba6c4010623/core/persistence/source/jetbrains/mps/persistence/binary/BinaryPersistence.java
    #
    # Purpose: Reads the import table and populates builder.index_2_imported_model_uuid, which maps import index
    # strings such as "1", "2", etc.. to model uuid strings.
    # Index 0 is always the current model's own UUID that is set separately in build().
    # These indices are used in _read_other_model_ref() in nodes.py to resolve cross-model references found
    # in thee node tree.
    #
    # Count is written as i32 (readInt in Java), not u16
    #
    # V2 format (in MPS 2024.1 this is the current active format explained as below) -
    #   i32 count
    #   per import: model_reference + i32 usedVersion
    #
    # V3 format (forward compatibility):
    #   i32 count
    #   per import: model_reference only (usedVersion field was removed)
    #
    # model_reference encoding mirrors Java ModelInputStream.readModelReference():
    #   kind byte:
    #     NULL (0x70) - no model, model_id = None
    #     MODELREF_INDEX (0x09) - indexed back-ref: read u32 index, model_id = None
    #     anything else - this IS the model_id_kind byte (readModelID() is called directly):
    #       MODELID_REGULAR (0x28) - UUID-based: 2xu64, formatted as "r:..."
    #       MODELID_FOREIGN (0x26) - string-based (e.g. "java:java.lang")
    #       NULL (0x70) - empty model id
    #   then: read model name string + read module reference (always present for full refs)

    count = reader.read_u32()

    for i in range(count):
        kind = reader.read_u8()

        if kind == NULL:
            model_id = None

        elif kind == MODELREF_INDEX:
            reader.read_u32()
            model_id = None

        else:
            model_id_kind = reader.read_u8()

            if model_id_kind == MODELID_REGULAR:
                uuid = reader.read_uuid()
                model_id = uuid_str(uuid[0], uuid[1])
            elif model_id_kind == MODELID_FOREIGN:
                # string-based foreign model id ex: "java:java.lang"
                model_id = reader.read_string()
            elif model_id_kind == NULL:
                model_id = ""
            else:
                raise RuntimeError(
                    f"Unsupported model_id_kind 0x{model_id_kind:02X} "
                    f"at pos {reader.tell()}"
                )
            # model name and declaring module ref
            reader.read_string()
            reader.read_module_ref()

        if version == _V2:
            reader.read_i32()

        builder.index_2_imported_model_uuid[str(i + 1)] = model_id or ""
