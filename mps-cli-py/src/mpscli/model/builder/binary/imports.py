from mpscli.model.builder.binary.constants import *
from mpscli.model.builder.binary.utils import *


def load_imports(reader, imported_models: dict):
    imports_count = reader.read_u32()

    for i in range(imports_count):
        read_and_add_model_reference(reader, imported_models, str(i + 1))

    def read_and_add_model_reference(reader, imported_models: dict, index: str):
        ref_kind = reader.read_u8()
        if ref_kind == MODELREF_INDEX:
            raise ValueError("Unexpected MODELREF_INDEX while reading imports")

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

        imported_models[index] = {
            "uuid": model_id,
            "name": model_name,
        }
