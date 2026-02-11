# mpscli/model/builder/binary/imports.py

from mpscli.model.builder.binary.constants import *
from mpscli.model.builder.binary.utils import (
    read_uuid,
    read_string,
    read_module_reference,
)


def load_imports(reader, builder):
    imports_count = reader.read_u32()

    for i in range(imports_count):
        ref_kind = reader.read_u8()

        if ref_kind == MODELREF_INDEX:
            raise ValueError("Unexpected MODELREF_INDEX in imports")

        model_id_kind = reader.read_u8()

        if model_id_kind == MODELID_REGULAR:
            uuid = read_uuid(reader)
            model_id = f"r:{uuid}"
        elif model_id_kind == NULL:
            model_id = ""
        else:
            raise ValueError(f"Unsupported model id kind: 0x{model_id_kind:X}")

        model_name = read_string(reader)
        read_module_reference(reader)

        builder.index_2_imported_model_uuid[str(i + 1)] = model_id
