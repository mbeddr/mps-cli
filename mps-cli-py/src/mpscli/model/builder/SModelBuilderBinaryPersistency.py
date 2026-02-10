# SModelBuilderBinaryPersistency.py

from mpscli.model.builder.binary.constants import *
from mpscli.model.builder.binary.utils import *
from mpscli.model.builder.binary.reader import BinaryReader
from mpscli.model.builder.SModelBuilderBase import SModelBuilderBase
from mpscli.model.builder.binary.constants import REGISTRY_START, REGISTRY_END
from mpscli.model.builder.binary.utils import advance_until_after
from mpscli.model.builder.binary.registry import load_registry


class SModelBuilderBinaryPersistency(SModelBuilderBase):

    def __init__(self):
        super().__init__()
        self.model_refs = []
        self.registry = {
            "concepts": {},
            "properties": {},
            "references": {},
            "containments": {},
        }

    def build(self, path_to_model: str):
        with open(path_to_model, "rb") as f:
            reader = BinaryReader(f.read())

        header = reader.read_u32()
        if header != HEADER_START:
            raise ValueError(f"Invalid header: 0x{header:X}")

        stream_id = reader.read_u32()
        if stream_id != STREAM_ID:
            raise ValueError(f"Unsupported stream id: 0x{stream_id:X}")

        model = self.read_model_header(reader)

        # --- registry ---
        advance_until_after(reader, REGISTRY_START)
        load_registry(reader, self.registry)
        advance_until_after(reader, REGISTRY_END)

        return model

    def read_model_header(self, reader):
        ref_kind = reader.read_u8()

        if ref_kind == NULL:
            raise ValueError("Unexpected NULL model reference")

        if ref_kind == MODELREF_INDEX:
            index = reader.read_u32()
            return self.model_refs[index]

        model_id_kind = reader.read_u8()

        if model_id_kind != MODELID_REGULAR:
            raise ValueError(f"Unsupported model id type: 0x{model_id_kind:X}")

        uuid = read_uuid(reader)
        model_id = f"r:{uuid}"

        model_name = read_string(reader)

        advance_until_after(reader, HEADER_END)

        model = {
            "uuid": model_id,
            "name": model_name
        }

        self.model_refs.append(model)
        return model

